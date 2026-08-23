#!/usr/bin/env python3
"""Standalone debugger for the "hình ảnh nhảy qua câu khác" bug in exam-PDF extract.

Reuses the REAL backend pipeline (bookforge_api.services.question_exam_extract /
pdf_figures) in-process — no API server, no DB, no Redis queue — so whatever it
reports is exactly what production would have done, using production's own
settings (backend/services/api/.env). It only ADDS observation: two module-level
functions are temporarily wrapped to record what the model claimed vs what the
pipeline finally decided for every figure crop; nothing in backend/ is modified.

See README.md in this folder for usage and how to read the report.
"""

from __future__ import annotations

import argparse
import sys
import threading
import time
import traceback
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[2]
BACKEND_SRC = REPO_ROOT / 'backend' / 'services' / 'api' / 'src'
if str(BACKEND_SRC) not in sys.path:
    sys.path.insert(0, str(BACKEND_SRC))

OUT_DIR = SCRIPT_DIR / 'out'


def _import_backend():
    """Deferred so --help works even if the backend venv/deps aren't active yet."""
    import bookforge_api.services.question_exam_extract as qee
    from bookforge_api.core.settings import get_settings
    from bookforge_api.services.pdf_figures import read_layout

    return qee, get_settings, read_layout


def iter_pdfs(inputs: list[str]) -> list[Path]:
    paths: list[Path] = []
    for raw in inputs:
        p = Path(raw)
        if p.is_dir():
            found = sorted(p.glob('*.pdf'))
            if not found:
                print(f'[WARN] Không tìm thấy .pdf nào trong thư mục: {p}')
            paths.extend(found)
        elif p.is_file():
            paths.append(p)
        else:
            print(f'[WARN] Không tìm thấy file/thư mục, bỏ qua: {raw}')
    return paths


def truncate_pdf(pdf_bytes: bytes, max_pages: int | None) -> bytes:
    if not max_pages:
        return pdf_bytes
    import fitz

    document = fitz.open(stream=pdf_bytes, filetype='pdf')
    try:
        if document.page_count <= max_pages:
            return pdf_bytes
        document.select(list(range(max_pages)))
        return document.tobytes()
    finally:
        document.close()


def install_trace(qee):
    """Wrap _run_one_window / _apply_figure_placement to record, per window:

    - the raw model output text(s) for that window (initial call + any repairs)
    - which crops were open to model arbitration (OCR crops with no geometric owner)
    - the model's own figure_anchors claims for those crops
    - each question's figure_ids BEFORE vs AFTER match_figures_to_questions ran

    Thread-local because extract_exam runs windows concurrently (ThreadPoolExecutor);
    each worker thread gets its own `window` / `raw_texts` slot.
    """
    tls = threading.local()
    trace: list[dict] = []

    real_run_one_window = qee._run_one_window
    real_apply_placement = qee._apply_figure_placement
    real_complete_window = qee._default_complete_window

    def complete_window(user_parts, *, settings):
        text, usage = real_complete_window(user_parts, settings=settings)
        if not hasattr(tls, 'raw_texts'):
            tls.raw_texts = []
        tls.raw_texts.append(text)
        return text, usage

    def traced_run_one_window(window, **kwargs):
        tls.window = list(window)
        tls.raw_texts = []
        outcome = real_run_one_window(window, **kwargs)
        if outcome.error is not None:
            trace.append(
                {
                    'window': list(window),
                    'raw_texts': list(tls.raw_texts),
                    'crops': {},
                    'anchors': [],
                    'before': {},
                    'after': {},
                    'window_error': outcome.error,
                }
            )
        return outcome

    def traced_apply_placement(questions, crops, anchors):
        window = list(getattr(tls, 'window', []) or [])
        raw_texts = list(getattr(tls, 'raw_texts', []) or [])
        before = {i: (q.section, q.number, list(q.figure_ids)) for i, q in enumerate(questions)}
        result = real_apply_placement(questions, crops, anchors)
        after = {i: (q.section, q.number, list(q.figure_ids)) for i, q in enumerate(result)}
        trace.append(
            {
                'window': window,
                'raw_texts': raw_texts,
                'crops': {cid: c.page for cid, c in crops.items()},
                'anchors': [(a.crop_id, a.after_question, a.before_question) for a in anchors],
                'before': before,
                'after': after,
            }
        )
        return result

    qee._run_one_window = traced_run_one_window
    qee._apply_figure_placement = traced_apply_placement

    def restore():
        qee._run_one_window = real_run_one_window
        qee._apply_figure_placement = real_apply_placement

    return trace, complete_window, restore


def crop_diff_lines(entry: dict) -> tuple[list[str], int, int, int]:
    """Per-crop lines for one window's trace entry, plus (mismatched, unclaimed, kept) counts."""
    lines: list[str] = []
    owner_before: dict[str, int] = {}
    owner_after: dict[str, int] = {}
    for idx, (_section, _number, figure_ids) in entry['before'].items():
        for crop_id in figure_ids:
            owner_before[crop_id] = idx
    for idx, (_section, _number, figure_ids) in entry['after'].items():
        for crop_id in figure_ids:
            owner_after[crop_id] = idx

    def label(idx: int | None) -> str:
        if idx is None:
            return 'KHÔNG CÓ (unclaimed)'
        section, number, _ = entry['after'].get(idx) or entry['before'].get(idx)
        section_part = f'Phần {section} ' if section else ''
        return f'{section_part}Câu {number or "?"}'

    anchors_by_crop = {a[0]: a for a in entry['anchors']}
    mismatched = unclaimed = kept = 0
    for crop_id in sorted(entry['crops']):
        before_idx = owner_before.get(crop_id)
        after_idx = owner_after.get(crop_id)
        anchor = anchors_by_crop.get(crop_id)
        anchor_txt = f'after={anchor[1] or "-"} before={anchor[2] or "-"}' if anchor else '(model không báo anchor)'
        if after_idx is None:
            unclaimed += 1
            flag = '⚠ KHÔNG GÁN ĐƯỢC'
        elif before_idx != after_idx:
            mismatched += 1
            flag = '⚠ ĐỔI CÂU'
        else:
            kept += 1
            flag = '✓ giữ nguyên'
        lines.append(
            f'    [{flag}] crop={crop_id} (trang {entry["crops"][crop_id]})'
            f' | model tự nhận (figure_ids): {label(before_idx)}'
            f' | figure_anchors: {anchor_txt}'
            f' | KẾT QUẢ CUỐI: {label(after_idx)}'
        )
    return lines, mismatched, unclaimed, kept


def render_report(pdf_path: Path, layout, page_count: int, result, trace, use_llm: bool) -> str:
    out: list[str] = []
    out.append('=== BÁO CÁO DEBUG: GHÉP HÌNH ẢNH VÀO CÂU HỎI (exam PDF extract) ===')
    out.append(f'File           : {pdf_path}')
    out.append(f'Chạy lúc       : {time.strftime("%Y-%m-%d %H:%M:%S")}')
    out.append(f'Số trang       : {page_count}')
    out.append('')

    total_mismatch = total_unclaimed = total_kept = 0
    window_errors = 0
    if use_llm and trace:
        for entry in trace:
            if 'window_error' in entry:
                window_errors += 1
                continue
            _lines, mismatched, unclaimed, kept = crop_diff_lines(entry)
            total_mismatch += mismatched
            total_unclaimed += unclaimed
            total_kept += kept

    out.append('--- TÓM TẮT NHANH ---')
    scanned = sorted(layout.scanned_pages)
    born_digital = sorted(set(range(1, page_count + 1)) - layout.scanned_pages)
    out.append(f'Trang scan (phải qua OCR)      : {scanned or "(không có)"}')
    out.append(f'Trang born-digital (đọc thẳng) : {born_digital or "(không có)"}')
    if layout.answer_pages_from:
        out.append(f'Bắt đầu phần ĐÁP ÁN/LỜI GIẢI ở trang: {layout.answer_pages_from}')
    if use_llm:
        if result is not None and not result.ok:
            out.append(f'*** TRÍCH XUẤT LỖI: {result.error} ***')
        out.append(f'Hình bị ĐỔI CÂU so với model tự nhận : {total_mismatch}')
        out.append(f'Hình KHÔNG GÁN ĐƯỢC (unclaimed)      : {total_unclaimed}')
        out.append(f'Hình giữ nguyên theo model tự nhận   : {total_kept}')
        if window_errors:
            out.append(f'Số window LLM lỗi (JSON không parse được): {window_errors}')
    else:
        out.append('(Chạy với --no-llm: chỉ kiểm tra hình học, chưa gọi LLM)')
    out.append('')

    out.append('--- 1. PHÂN LOẠI TRANG + HÌNH ĐỌC THẲNG TỪ PDF (không dùng LLM) ---')
    for page_no in range(1, page_count + 1):
        status = 'SCANNED -> đi qua OCR' if page_no in layout.scanned_pages else 'born-digital'
        out.append(f'  Trang {page_no}: {status}')
        for i, fig in enumerate(layout.figures.get(page_no, [])):
            section_part = f'Phần {fig.section} ' if fig.section else ''
            out.append(f'    - Hình #{i}: gán theo hình học cho {section_part}Câu {fig.number}')
    out.append('')

    if not use_llm:
        out.append('(Bỏ qua bước LLM — chạy lại KHÔNG có --no-llm để xem bước ghép hình đầy đủ)')
        return '\n'.join(out)

    out.append('--- 2. LỜI GỌI LLM CHÍNH (question_exam_extract) ---')
    if result is not None:
        out.append(f'Provider/model : {result.provider} / {result.model}')
        out.append(f'Trang xử lý    : {result.pages_processed} (bỏ qua {result.pages_skipped} trang trắng)')
        out.append(f'Token usage    : {result.usage}')
        out.append(f'Số câu hỏi thu được: {len(result.questions)}')
    out.append('')

    out.append('--- 3. GHÉP HÌNH VÀO CÂU (chỉ áp dụng cho crop KHÔNG có chủ hình học sẵn, tức đọc từ OCR) ---')
    out.append('    Ý nghĩa 3 cột: model tự nhận (field figure_ids model viết ra) so với')
    out.append('    figure_anchors (model nói hình nằm ngay trước/sau câu nào) so với quyết định cuối cùng.')
    if not trace:
        out.append('  (Không có crop nào cần trọng tài mô hình — mọi hình đều được gán bằng hình học,')
        out.append('   hoặc file không có hình nào ở các trang OCR.)')
    for entry in trace:
        window_label = f'Window trang {entry["window"]}'
        if 'window_error' in entry:
            out.append(f'  {window_label}: *** LỖI WINDOW: {entry["window_error"]} ***')
            for i, raw in enumerate(entry['raw_texts']):
                out.append(f'    raw output lần gọi #{i + 1} (rút gọn 500 ký tự đầu):')
                out.append('      ' + raw[:500].replace('\n', ' '))
            continue
        out.append(f'  {window_label} — {len(entry["crops"])} crop cần trọng tài, {len(entry["raw_texts"])} lần gọi model')
        lines, _m, _u, _k = crop_diff_lines(entry)
        out.extend(lines)
    out.append('')

    out.append('--- 4. DANH SÁCH CÂU HỎI CUỐI CÙNG (tóm tắt) ---')
    if result is not None:
        for q in result.questions:
            section_part = f'Phần {q.section} ' if q.section else ''
            out.append(
                f'  {section_part}Câu {q.number or "?"} | loại={q.question_type} | trang={q.pages}'
                f' | figure_ids cuối={q.figure_ids}'
            )
    out.append('')

    return '\n'.join(out)


def run_one(pdf_path: Path, *, use_llm: bool, max_pages: int | None, qee, get_settings, read_layout) -> str:
    import fitz

    pdf_bytes = pdf_path.read_bytes()
    pdf_bytes = truncate_pdf(pdf_bytes, max_pages)
    document = fitz.open(stream=pdf_bytes, filetype='pdf')
    page_count = document.page_count
    document.close()

    layout = read_layout(pdf_bytes)

    result = None
    trace: list[dict] = []
    if use_llm:
        settings = get_settings()
        trace_list, complete_window, restore = install_trace(qee)
        try:
            result = qee.extract_exam(pdf_bytes, settings=settings, complete_window=complete_window)
        finally:
            restore()
        trace = trace_list

    return render_report(pdf_path, layout, page_count, result, trace, use_llm)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('inputs', nargs='+', help='File .pdf hoặc thư mục chứa .pdf')
    parser.add_argument(
        '--no-llm',
        action='store_true',
        help='Chỉ chạy bước phân loại trang + hình đọc thẳng từ PDF (miễn phí, không gọi LLM).',
    )
    parser.add_argument(
        '--max-pages',
        type=int,
        default=None,
        help='Chỉ xử lý N trang đầu của mỗi file (để test nhanh/rẻ trên file dài).',
    )
    parser.add_argument('--out', default=str(OUT_DIR), help=f'Thư mục ghi báo cáo (mặc định: {OUT_DIR})')
    args = parser.parse_args()

    pdfs = iter_pdfs(args.inputs)
    if not pdfs:
        print('Không có file .pdf nào để xử lý.')
        return 1

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    qee = get_settings = read_layout = None
    if True:  # always need read_layout; only need qee/get_settings when use_llm
        qee, get_settings, read_layout = _import_backend()

    timestamp = time.strftime('%Y%m%d-%H%M%S')
    for pdf_path in pdfs:
        print(f'--- Đang xử lý: {pdf_path} ---')
        try:
            report = run_one(
                pdf_path,
                use_llm=not args.no_llm,
                max_pages=args.max_pages,
                qee=qee,
                get_settings=get_settings,
                read_layout=read_layout,
            )
        except Exception:
            report = (
                f'=== LỖI KHI XỬ LÝ {pdf_path} ===\n'
                f'{traceback.format_exc()}'
            )
            print(f'[LỖI] {pdf_path} — xem chi tiết trong file báo cáo')

        report_path = out_dir / f'{pdf_path.stem}__{timestamp}.txt'
        report_path.write_text(report, encoding='utf-8')
        print(f'  -> Báo cáo: {report_path}')

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
