# -*- coding: utf-8 -*-
"""동아그룹 4개사 Microsoft EA·SCE 갱신 제안서 PPTX 생성 스크립트 (v2).

디자인 시스템: 화이트 배경 + 헤어라인 + 액션 타이틀 (컨소시엄 회의록 2차 결정 사항)
"""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn

# ── 디자인 토큰 ──────────────────────────────────────────────
NAVY = RGBColor(0x1B, 0x2A, 0x4A)      # 잉크(타이틀·핵심 숫자)
BODY = RGBColor(0x3A, 0x43, 0x56)      # 본문
CAP = RGBColor(0x8A, 0x93, 0xA3)       # 캡션·보조
HAIR = RGBColor(0xE1, 0xE5, 0xEB)      # 헤어라인(옅음)
FILLG = RGBColor(0xF5, 0xF7, 0xFA)     # 옅은 면 채움
ORANGE = RGBColor(0xE8, 0x6C, 0x1A)    # 단일 액센트
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
FONT = "맑은 고딕"

SW, SH = Inches(13.333), Inches(7.5)
MX = Inches(0.7)                        # 좌우 마진
CW = Inches(11.933)                     # 콘텐츠 폭
TOTAL_PAGES = 14
DOC_FOOT = "동아그룹 Microsoft EA·SCE 라이선스 갱신 제안서  |  2026.03.31 ~ 2028.04.01"


def style_run(run, size, bold=False, color=BODY, italic=False):
    f = run.font
    f.size, f.bold, f.italic, f.name = Pt(size), bold, italic, FONT
    f.color.rgb = color
    rPr = run._r.get_or_add_rPr()
    ea = rPr.find(qn("a:ea"))
    if ea is None:
        ea = rPr.makeelement(qn("a:ea"), {})
        rPr.append(ea)
    ea.set("typeface", FONT)


def add_text(slide, x, y, w, h, lines, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP,
             wrap=True, space_after=4):
    """lines: [(text, size[, bold[, color]]), ...] — 한 줄에 여러 런이 필요하면
    text 자리에 [(txt, size, bold, color), ...] 리스트를 넣는다."""
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = wrap
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    for i, spec in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.space_after = Pt(space_after)
        runs = spec[0] if isinstance(spec[0], (list, tuple)) else [spec]
        for rs in runs:
            text, size = rs[0], rs[1]
            bold = rs[2] if len(rs) > 2 else False
            color = rs[3] if len(rs) > 3 else BODY
            r = p.add_run()
            r.text = text
            style_run(r, size, bold, color)
    return tb


def add_rect(slide, x, y, w, h, fill):
    sp = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, h)
    sp.fill.solid()
    sp.fill.fore_color.rgb = fill
    sp.line.fill.background()
    sp.shadow.inherit = False
    return sp


def hline(slide, x, y, w, weight=0.5, color=HAIR):
    return add_rect(slide, x, y, w, Pt(weight), color)


def vline(slide, x, y, h, weight=0.5, color=HAIR):
    return add_rect(slide, x, y, Pt(weight), h, color)


def header(slide, kicker, title, page_no, title_size=20):
    """액션 타이틀 헤더: 오렌지 킥커 + 결론형 타이틀 + 짧은 언더스코어."""
    add_text(slide, MX, Inches(0.42), CW, Inches(0.28),
             [(kicker, 10.5, True, ORANGE)])
    add_text(slide, MX, Inches(0.72), CW, Inches(0.55),
             [(title, title_size, True, NAVY)])
    add_rect(slide, MX, Inches(1.28), Inches(0.5), Pt(3), ORANGE)
    # footer
    hline(slide, MX, Inches(7.05), CW, 0.5, HAIR)
    add_text(slide, MX, Inches(7.12), Inches(9), Inches(0.28),
             [(DOC_FOOT, 8.5, False, CAP)])
    add_text(slide, Inches(11.6), Inches(7.12), Inches(1.03), Inches(0.28),
             [(f"{page_no} / {TOTAL_PAGES}", 8.5, False, CAP)], align=PP_ALIGN.RIGHT)


def set_cell(cell, text, size=10, bold=False, color=BODY, fill=WHITE,
             align=PP_ALIGN.LEFT):
    cell.fill.solid()
    cell.fill.fore_color.rgb = fill
    cell.vertical_anchor = MSO_ANCHOR.MIDDLE
    cell.margin_left, cell.margin_right = Inches(0.08), Inches(0.08)
    cell.margin_top = cell.margin_bottom = Inches(0.01)
    tf = cell.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    r = p.add_run()
    r.text = text
    style_run(r, size, bold, color)


def clean_table(slide, x, y, w, col_ratios, rows, row_h=Inches(0.36),
                total_rows=1, font_size=10, center_cols=()):
    """컨설팅식 헤어라인 표: 세로선·채움 없음, 가로 라인만.
    rows[0]=헤더, 마지막 total_rows개 행 = 합계(옅은 채움+볼드).
    셀: str 또는 (str, opts) — opts: bold/color/align/size"""
    n_r, n_c = len(rows), len(rows[0])
    gf = slide.shapes.add_table(n_r, n_c, x, y, w, row_h * n_r)
    table = gf.table
    total = sum(col_ratios)
    for i, ratio in enumerate(col_ratios):
        table.columns[i].width = Emu(int(int(w) * ratio / total))
    for ri, row in enumerate(rows):
        table.rows[ri].height = row_h
        is_total = ri >= n_r - total_rows and total_rows > 0
        for ci, spec in enumerate(row):
            text, opts = (spec if isinstance(spec, tuple) else (spec, {}))
            d_align = (PP_ALIGN.LEFT if ci == 0
                       else PP_ALIGN.CENTER if ci in center_cols
                       else PP_ALIGN.RIGHT)
            cell = table.cell(ri, ci)
            if ri == 0:
                set_cell(cell, text, font_size - 0.5, True, NAVY, WHITE,
                         opts.get("align", d_align))
            else:
                set_cell(cell, text, opts.get("size", font_size),
                         opts.get("bold", is_total),
                         opts.get("color", NAVY if is_total else BODY),
                         FILLG if is_total else WHITE,
                         opts.get("align", d_align))
    # 가로 라인 오버레이
    rh = int(row_h)
    hline(slide, x, y, w, 1.5, NAVY)                       # 표 상단
    hline(slide, x, Emu(int(y) + rh), w, 0.75, NAVY)       # 헤더 하단
    for b in range(2, n_r):                                # 본문 행 경계
        if total_rows and b == n_r - total_rows:
            hline(slide, x, Emu(int(y) + rh * b), w, 1.0, NAVY)   # 합계 위
        else:
            hline(slide, x, Emu(int(y) + rh * b), w, 0.5, HAIR)
    hline(slide, x, Emu(int(y) + rh * n_r), w, 1.0, NAVY)  # 표 하단
    return table


def stat_band(slide, x, y, w, stats, big=26, band_h=Inches(1.0)):
    """빅넘버 스탯 밴드: (label, value, color[, sub]) 목록, 세로 헤어라인 구분."""
    n = len(stats)
    cw = int(w) // n
    for i, st in enumerate(stats):
        label, value, color = st[0], st[1], st[2]
        sub = st[3] if len(st) > 3 else None
        sx = Emu(int(x) + cw * i + (0 if i == 0 else int(Inches(0.35))))
        lines = [(label, 9.5, False, CAP), (value, big, True, color)]
        if sub:
            lines.append((sub, 9, False, CAP))
        add_text(slide, sx, y, Emu(cw - int(Inches(0.4))), band_h, lines,
                 space_after=5)
        if i > 0:
            vline(slide, Emu(int(x) + cw * i), Emu(int(y) + int(Inches(0.05))),
                  Emu(int(band_h) - int(Inches(0.1))), 0.75, HAIR)


def accent_card(slide, x, y, w, h):
    """옅은 채움 + 좌측 오렌지 액센트 바 카드."""
    add_rect(slide, x, y, w, h, FILLG)
    add_rect(slide, x, y, Pt(3), h, ORANGE)


prs = Presentation()
prs.slide_width, prs.slide_height = SW, SH
BLANK = prs.slide_layouts[6]


def new_slide():
    return prs.slides.add_slide(BLANK)


# ══════════════════════════════════════════════════════════════
# 1. 표지 — 화이트, 좌정렬 텍스트 블록
# ══════════════════════════════════════════════════════════════
s = new_slide()
add_rect(s, Inches(10.5), Inches(-0.5), Inches(3.5), Inches(8.5), FILLG)  # 우측 배경 면
add_rect(s, MX, Inches(1.15), Inches(0.14), Inches(0.14), ORANGE)
add_text(s, Inches(0.95), Inches(1.09), Inches(10), Inches(0.3),
         [("MICROSOFT ENTERPRISE AGREEMENT  ·  SERVER & CLOUD ENROLLMENT",
           11, True, CAP)])
add_text(s, MX, Inches(1.85), Inches(11), Inches(1.9),
         [("동아그룹 주요 4개사", 34, True, NAVY),
          ("Microsoft EA·SCE 라이선스 갱신 제안서", 34, True, NAVY)], space_after=8)
hline(s, MX, Inches(3.75), Inches(9.0), 0.75, HAIR)
add_text(s, MX, Inches(4.05), Inches(10.5), Inches(1.7),
         [([("계약기간   ", 12, True, NAVY),
            ("2026. 03. 31 ~ 2028. 04. 01  (3년 차 갱신)", 12, False, BODY)],),
          ([("대상 법인   ", 12, True, NAVY),
            ("동아쏘시오홀딩스㈜ · 동아에스티㈜ · 동아제약㈜ · 에스티젠바이오㈜",
             12, False, BODY)],),
          ([("금액 기준   ", 12, True, NAVY),
            ("부가세(VAT) 별도", 12, False, BODY)],),
          ("2026년 7월", 10.5, False, CAP)], space_after=10)
add_rect(s, 0, Inches(7.34), SW, Inches(0.16), ORANGE)

# ══════════════════════════════════════════════════════════════
# 2. 목차
# ══════════════════════════════════════════════════════════════
s = new_slide()
header(s, "CONTENTS", "목차", 2, title_size=22)
toc = [
    ("01", "제안 개요 (Executive Summary)"),
    ("02", "계약 구조 및 갱신 원칙"),
    ("03", "주요 4사 총계 비교 (EA+SCE)"),
    ("04", "EA 라이선스 요약"),
    ("05", "SCE 라이선스 요약"),
    ("06", "회사별 상세 — 동아쏘시오홀딩스㈜"),
    ("07", "회사별 상세 — 동아에스티㈜"),
    ("08", "회사별 상세 — 동아제약㈜"),
    ("09", "회사별 상세 — 에스티젠바이오㈜"),
    ("10", "증감 요인 분석"),
    ("11", "계약 조건 및 향후 일정"),
]
for i, (no, title) in enumerate(toc):
    col, row = i // 6, i % 6
    x = Emu(int(MX) + col * int(Inches(6.2)))
    y = Emu(int(Inches(1.75)) + row * int(Inches(0.82)))
    add_text(s, x, y, Inches(0.6), Inches(0.5), [(no, 13, True, ORANGE)],
             anchor=MSO_ANCHOR.MIDDLE)
    add_text(s, Emu(int(x) + int(Inches(0.65))), y, Inches(5.2), Inches(0.5),
             [(title, 13, False, NAVY)], anchor=MSO_ANCHOR.MIDDLE)
    hline(s, x, Emu(int(y) + int(Inches(0.62))), Inches(5.7), 0.5, HAIR)

# ══════════════════════════════════════════════════════════════
# 3. 제안 개요
# ══════════════════════════════════════════════════════════════
s = new_slide()
header(s, "01  |  EXECUTIVE SUMMARY",
       "26Y 총 계약 1,308백만 원(+9.3%) — 증가분은 전액 사업 확장(True-up)에서 발생했습니다", 3,
       title_size=18)
stat_band(s, MX, Inches(1.6), CW, [
    ("26Y 총 계약 금액 (EA+SCE, VAT 별도)", "1,308,395,302원", NAVY, "25Y 1,196,718,702원"),
    ("전년 대비 증감", "+9.3%", ORANGE, "증가액 111,676,600원"),
    ("SCE 서버 라이선스 증감", "0%", NAVY, "5개 품목 × 4사 전 품목 동결"),
], big=24, band_h=Inches(1.15))
hline(s, MX, Inches(2.95), CW, 0.5, HAIR)

rows = [
    ["구분", "25Y", "26Y", "증감률"],
    ["EA 라이선스 (M365 E3)", "934,197,600", "1,045,874,200",
     ("+12%", {"color": ORANGE, "bold": True})],
    ["SCE 라이선스 (서버)", "262,521,102", "262,521,102", "0%"],
    ["총 합계", "1,196,718,702", "1,308,395,302",
     ("+9.3%", {"color": ORANGE, "bold": True})],
]
add_text(s, MX, Inches(3.2), Inches(6.3), Inches(0.25),
         [("전체 총계 (단위: 원, VAT 별도)", 10, True, NAVY)])
clean_table(s, MX, Inches(3.5), Inches(6.3), [2.0, 1.5, 1.5, 0.9], rows,
            row_h=Inches(0.42))

msgs = [
    ("기존 비용은 그대로", "EA Renewal과 SCE 서버 라이선스 전 품목이 4개사 모두 전년 금액 동결 — 단가 인상 요인 0원"),
    ("증가분 = 100% True-up", "증가액 111,676,600원은 전액 사용자 244EA 순증의 정산분 (인상이 아닌 사용 확대)"),
    ("성장 기업에 집중", "에스티젠바이오 +130EA(+47%) · 동아에스티 +92EA(+9%) — 사업 확장이 만든 자연스러운 결과"),
]
mx2 = Inches(7.5)
add_text(s, mx2, Inches(3.2), Inches(5.1), Inches(0.25),
         [("핵심 메시지", 10, True, NAVY)])
for i, (t, d) in enumerate(msgs):
    y = Emu(int(Inches(3.55)) + i * int(Inches(1.08)))
    add_text(s, mx2, y, Inches(0.3), Inches(0.3), [("—", 12, True, ORANGE)])
    add_text(s, Emu(int(mx2) + int(Inches(0.35))), y, Inches(4.8), Inches(1.0),
             [(t, 11.5, True, NAVY), (d, 9.5, False, BODY)], space_after=3)

# ══════════════════════════════════════════════════════════════
# 4. 계약 구조 및 갱신 원칙
# ══════════════════════════════════════════════════════════════
s = new_slide()
header(s, "02  |  CONTRACT STRUCTURE",
       "단가는 전면 동결 — 비용 변동은 오직 사용 규모(True-up)에만 연동됩니다", 4)

cards = [
    ("EA — Enterprise Agreement (M365 E3)",
     ["전사 사용자 대상 Microsoft 365 E3 볼륨 라이선스",
      "Renewal(기존 인원 갱신) + True-up(연중 증가 인원 연 1회 정산) 구조",
      "금회 갱신: Renewal 4사 전액 동결, True-up만 실사용 증가분 반영"]),
    ("SCE — Server & Cloud Enrollment",
     ["서버·개발 인프라 대상 3년 약정 Enrollment",
      "SQL Server(Ent/Std Core) · Windows Server Core · Visual Studio Ent with GitHub · SecureON MS Unified Support",
      "금회 갱신: 5개 품목 × 4사 전 품목 전년 동결 (0%)"]),
]
for i, (t, items) in enumerate(cards):
    x = Emu(int(MX) + i * int(Inches(6.1)))
    accent_card(s, x, Inches(1.65), Inches(5.85), Inches(2.6))
    add_text(s, Emu(int(x) + int(Inches(0.3))), Inches(1.92), Inches(5.3), Inches(0.4),
             [(t, 13.5, True, NAVY)])
    add_text(s, Emu(int(x) + int(Inches(0.3))), Inches(2.45), Inches(5.3), Inches(1.7),
             [("·  " + it, 10.5, False, BODY) for it in items], space_after=8)

add_text(s, MX, Inches(4.6), CW, Inches(0.3), [("금회 갱신 3원칙", 11, True, NAVY)])
principles = [
    ("01", "단가 전면 동결", "EA Renewal·SCE 서버 라이선스 모두 전년 계약 조건 그대로 유지"),
    ("02", "증가분만 정산", "비용 변동은 True-up(사용 인원 순증)에만 연동 — 선구매·과잉 구매 없음"),
    ("03", "예산 예측 가능성", "3년 약정 단가로 계약 기간 내 안정적인 IT 예산 수립 가능"),
]
for i, (no, t, d) in enumerate(principles):
    x = Emu(int(MX) + i * int(Inches(4.05)))
    y = Inches(5.0)
    add_text(s, x, y, Inches(0.55), Inches(0.5), [(no, 18, True, ORANGE)])
    add_text(s, Emu(int(x) + int(Inches(0.6))), y, Inches(3.2), Inches(1.4),
             [(t, 12, True, NAVY), (d, 9.5, False, BODY)], space_after=4)
    if i > 0:
        vline(s, Emu(int(x) - int(Inches(0.25))), y, Inches(1.3), 0.75, HAIR)

# ══════════════════════════════════════════════════════════════
# 5. 4사 총계 비교
# ══════════════════════════════════════════════════════════════
s = new_slide()
header(s, "03  |  GROUP SUMMARY",
       "4사 합계 +9.3% — 증가는 성장 중인 2개사(동아에스티·에스티젠바이오)에 집중되어 있습니다", 5,
       title_size=18)
rows = [
    ["회사", "25Y", "26Y", "증감액", "증감률"],
    ["동아쏘시오홀딩스㈜", "42,631,042", "42,631,042", "—", ("0%", {"align": PP_ALIGN.CENTER})],
    ["동아에스티㈜", "627,649,860", "672,640,260", "+44,990,400",
     ("+7.2%", {"color": ORANGE, "bold": True, "align": PP_ALIGN.CENTER})],
    ["동아제약㈜", "370,209,200", "377,381,400", "+7,172,200",
     ("+1.9%", {"align": PP_ALIGN.CENTER})],
    ["에스티젠바이오㈜", "156,228,600", "215,742,600", "+59,514,000",
     ("+38%", {"color": ORANGE, "bold": True, "align": PP_ALIGN.CENTER})],
    ["합계", "1,196,718,702", "1,308,395,302", "+111,676,600",
     ("+9.3%", {"align": PP_ALIGN.CENTER, "bold": True, "color": ORANGE})],
]
add_text(s, MX, Inches(1.6), CW, Inches(0.25),
         [("회사별 EA+SCE 합계 (단위: 원, VAT 별도)", 10, True, NAVY)])
clean_table(s, MX, Inches(1.95), CW, [2.2, 1.7, 1.7, 1.6, 1.0], rows,
            row_h=Inches(0.5), font_size=11)

add_text(s, MX, Inches(5.15), CW, Inches(1.5),
         [([("읽는 법  ", 10, True, ORANGE),
            ("증가액 전액이 EA True-up(사용자 순증)에서 발생 — SCE(서버)와 EA Renewal(기존 인원)은 4사 모두 동결입니다. ",
             10.5, False, BODY)],),
          ("에스티젠바이오·동아에스티의 증가율은 사업 확장에 따른 인력 확충이 라이선스 수요로 이어진 결과이며, 지주회사인 동아쏘시오홀딩스는 전 항목 변동이 없습니다.",
           10.5, False, BODY)], space_after=6)

# ══════════════════════════════════════════════════════════════
# 6. EA 요약
# ══════════════════════════════════════════════════════════════
s = new_slide()
header(s, "04  |  EA SUMMARY",
       "EA +12%는 사용자 244EA 증가의 결과이며, 단가 인상분은 0원입니다", 6)
rows = [
    ["회사", "25Y", "26Y", "증감액", "증감률", "EA 수량"],
    ["동아쏘시오홀딩스㈜", "36,204,000", "36,204,000", "—",
     ("0%", {"align": PP_ALIGN.CENTER}), ("변동 없음", {"align": PP_ALIGN.CENTER, "size": 9})],
    ["동아에스티㈜", "494,797,800", "539,788,200", "+44,990,400",
     ("+9%", {"color": ORANGE, "bold": True, "align": PP_ALIGN.CENTER}),
     ("1,249 → 1,341", {"align": PP_ALIGN.CENTER, "size": 9})],
    ["동아제약㈜", "275,801,400", "282,973,600", "+7,172,200",
     ("+2.6%", {"align": PP_ALIGN.CENTER}),
     ("687 → 709", {"align": PP_ALIGN.CENTER, "size": 9})],
    ["에스티젠바이오㈜", "127,394,400", "186,908,400", "+59,514,000",
     ("+47%", {"color": ORANGE, "bold": True, "align": PP_ALIGN.CENTER}),
     ("300 → 430", {"align": PP_ALIGN.CENTER, "size": 9})],
    ["EA 합계", "934,197,600", "1,045,874,200", "+111,676,600",
     ("+12%", {"align": PP_ALIGN.CENTER, "bold": True, "color": ORANGE}),
     ("+244EA", {"align": PP_ALIGN.CENTER, "size": 9})],
]
add_text(s, MX, Inches(1.6), CW, Inches(0.25),
         [("EA 라이선스 — M365 E3 (단위: 원, VAT 별도)", 10, True, NAVY)])
clean_table(s, MX, Inches(1.95), CW, [2.1, 1.6, 1.6, 1.5, 0.9, 1.3], rows,
            row_h=Inches(0.48), font_size=10.5)

stat_band(s, MX, Inches(5.3), CW, [
    ("Renewal (기존 인원)", "4사 전액 동결", NAVY, "기존 라이선스 비용 부담 변동 없음"),
    ("True-up 순증", "+244EA", ORANGE, "에스티젠 130 · 에스티 92 · 제약 22"),
    ("증가분의 성격", "사용 확대", NAVY, "단가 인상이 아닌 사업 확장 반영"),
], big=17, band_h=Inches(1.0))

# ══════════════════════════════════════════════════════════════
# 7. SCE 요약
# ══════════════════════════════════════════════════════════════
s = new_slide()
header(s, "05  |  SCE SUMMARY",
       "SCE 서버 라이선스는 5개 품목 × 4사 전체가 전년 동결입니다", 7)
rows = [
    ["품목", "동아쏘시오홀딩스", "동아에스티", "동아제약", "에스티젠바이오"],
    ["SQL Server Enterprise Core", "3,123,184", "59,588,929", "36,661,930", "13,521,969"],
    ["SQL Server Standard Core", "1,651,058", "38,704,440", "34,816,200", "7,148,332"],
    ["Win Server Standard Core", "536,797", "13,265,847", "9,829,270", "3,332,100"],
    ["Visual Studio Ent with GitHub", "41,247", "786,981", "484,200", "178,590"],
    ["SecureON - MS Unified Support", "1,074,756", "20,505,863", "12,616,200", "4,653,210"],
    ["SCE 소계", "6,427,042", "132,852,060", "94,407,800", "28,834,200"],
]
add_text(s, MX, Inches(1.6), CW, Inches(0.25),
         [("SCE 라이선스 — 25Y·26Y 동일 금액 (단위: 원, VAT 별도)", 10, True, NAVY)])
clean_table(s, MX, Inches(1.95), CW, [2.6, 1.5, 1.5, 1.5, 1.5], rows,
            row_h=Inches(0.42), font_size=10)

stat_band(s, MX, Inches(5.35), CW, [
    ("SCE 4사 합계 (25Y = 26Y)", "262,521,102원", NAVY, "전 품목 증감 0%"),
    ("비용 안정성", "3년 약정 동결", ORANGE, "서버 인프라 예산의 예측 가능성 확보"),
], big=20, band_h=Inches(1.0))

# ══════════════════════════════════════════════════════════════
# 8~11. 회사별 상세
# ══════════════════════════════════════════════════════════════
companies = [
    dict(
        no="06", name="동아쏘시오홀딩스㈜", page=8,
        title="동아쏘시오홀딩스 — EA·SCE 전 항목 동결로 전년과 동일한 42,631,042원입니다",
        stat_label="26Y EA+SCE 합계", stat_value="42,631,042원",
        rate="0%", rate_color=NAVY, badge="전 항목 동결", ea_qty="EA 수량 변동 없음",
        ea=[["MS EA Renewal", "34,372,800", "34,372,800", "동결"],
            ["MS EA True-up", "1,831,200", "1,831,200", "동결"],
            ["EA 소계", "36,204,000", "36,204,000", "0%"]],
        sce_total="6,427,042",
        note="그룹 지주회사로 인원 변동이 없어, EA·SCE 전 항목이 전년 계약 조건 그대로 유지됩니다.",
    ),
    dict(
        no="07", name="동아에스티㈜", page=9,
        title="동아에스티 +7.2%는 True-up 92EA 반영분 — 기존 라이선스·서버 비용은 동결입니다",
        stat_label="26Y EA+SCE 합계", stat_value="672,640,260원",
        rate="+7.2%", rate_color=ORANGE, badge="사업 확장 반영", ea_qty="1,249EA → 1,341EA",
        ea=[["MS EA Renewal", "430,831,800", "430,831,800", "동결"],
            ["MS EA True-up", "63,966,000", "108,956,400",
             ("+70%", {"color": ORANGE, "bold": True})],
            ["EA 소계", "494,797,800", "539,788,200",
             ("+9%", {"color": ORANGE})]],
        sce_total="132,852,060",
        note="증가액 44,990,400원은 전액 True-up 92EA의 정산분으로, 임직원 증가 등 사업 확장에 따른 사용 규모 확대를 반영합니다. Renewal·SCE는 전액 동결입니다.",
    ),
    dict(
        no="08", name="동아제약㈜", page=10,
        title="동아제약 +1.9% — True-up 22EA 외 모든 항목이 동결입니다",
        stat_label="26Y EA+SCE 합계", stat_value="377,381,400원",
        rate="+1.9%", rate_color=NAVY, badge="소폭 증가", ea_qty="687EA → 709EA",
        ea=[["MS EA Renewal", "224,985,600", "224,985,600", "동결"],
            ["MS EA True-up", "50,815,800", "57,988,000",
             ("+14%", {"color": ORANGE, "bold": True})],
            ["EA 소계", "275,801,400", "282,973,600",
             ("+2.6%", {"color": ORANGE})]],
        sce_total="94,407,800",
        note="증가액 7,172,200원은 True-up 22EA의 정산분으로, 실사용 증가분만 반영된 최소 수준의 조정입니다. Renewal·SCE는 전액 동결입니다.",
    ),
    dict(
        no="09", name="에스티젠바이오㈜", page=11,
        title="에스티젠바이오 +38%는 사업 확장(+130EA)이 만든 성장의 지표입니다",
        stat_label="26Y EA+SCE 합계", stat_value="215,742,600원",
        rate="+38%", rate_color=ORANGE, badge="사업 확장 대폭 반영", ea_qty="300EA → 430EA",
        ea=[["MS EA Renewal", "57,808,800", "57,808,800", "동결"],
            ["MS EA True-up", "69,585,600", "129,099,600",
             ("+86%", {"color": ORANGE, "bold": True})],
            ["EA 소계", "127,394,400", "186,908,400",
             ("+47%", {"color": ORANGE})]],
        sce_total="28,834,200",
        note="증가액 59,514,000원은 전액 True-up 130EA의 정산분입니다. 바이오 사업 확장에 따른 대규모 인력 확충이 그대로 반영된 결과로, Renewal·SCE는 전액 동결입니다.",
    ),
]
SCE_ITEMS = ["SQL Server Enterprise Core", "SQL Server Standard Core",
             "Win Server Standard Core", "Visual Studio Ent with GitHub",
             "SecureON - MS Unified Support"]
SCE_DATA = {
    "동아쏘시오홀딩스㈜": ["3,123,184", "1,651,058", "536,797", "41,247", "1,074,756"],
    "동아에스티㈜": ["59,588,929", "38,704,440", "13,265,847", "786,981", "20,505,863"],
    "동아제약㈜": ["36,661,930", "34,816,200", "9,829,270", "484,200", "12,616,200"],
    "에스티젠바이오㈜": ["13,521,969", "7,148,332", "3,332,100", "178,590", "4,653,210"],
}

for co in companies:
    s = new_slide()
    header(s, f"{co['no']}  |  COMPANY DETAIL — {co['name']}", co["title"], co["page"],
           title_size=17)

    # 좌측 요약 카드
    accent_card(s, MX, Inches(1.6), Inches(3.1), Inches(4.55))
    cx = Emu(int(MX) + int(Inches(0.3)))
    add_text(s, cx, Inches(1.9), Inches(2.6), Inches(4.0),
             [(co["stat_label"] + " (VAT 별도)", 9.5, False, CAP),
              (co["stat_value"], 19, True, NAVY),
              ("", 6),
              ("전년 대비 증감", 9.5, False, CAP),
              (co["rate"], 30, True, co["rate_color"]),
              (co["badge"], 11, True, ORANGE if co["rate_color"] is ORANGE else NAVY),
              ("", 6),
              ("EA 수량", 9.5, False, CAP),
              (co["ea_qty"], 12, True, NAVY)], space_after=4)

    # 우측: EA 표
    tx = Inches(4.1)
    tw = Inches(8.53)
    add_text(s, tx, Inches(1.6), tw, Inches(0.24),
             [("EA 라이선스 (M365 E3)  —  단위: 원, VAT 별도", 9.5, True, NAVY)])
    ea_rows = [["품목", "25Y", "26Y", "증감"]] + co["ea"]
    clean_table(s, tx, Inches(1.9), tw, [2.2, 1.5, 1.5, 0.9], ea_rows,
                row_h=Inches(0.36), font_size=10, center_cols=(3,))

    # 우측: SCE 표
    sce_y = Inches(3.55)
    add_text(s, tx, sce_y, tw, Inches(0.24),
             [("SCE 라이선스  —  전 품목 동결 (25Y = 26Y)", 9.5, True, NAVY)])
    vals = SCE_DATA[co["name"]]
    sce_rows = ([["품목", "25Y", "26Y", "증감"]]
                + [[SCE_ITEMS[i], vals[i], vals[i], "0%"] for i in range(5)]
                + [["SCE 소계", co["sce_total"], co["sce_total"], "0%"]])
    clean_table(s, tx, Emu(int(sce_y) + int(Inches(0.3))), tw,
                [2.2, 1.5, 1.5, 0.9], sce_rows, row_h=Inches(0.325),
                font_size=9.5, center_cols=(3,))

    # 하단 노트
    add_text(s, MX, Inches(6.35), CW, Inches(0.6),
             [([("비용 변동 사유  ", 9.5, True, ORANGE),
                (co["note"], 9.5, False, BODY)],)])

# ══════════════════════════════════════════════════════════════
# 12. 증감 요인 분석
# ══════════════════════════════════════════════════════════════
s = new_slide()
header(s, "10  |  GROWTH ANALYSIS",
       "증가액 111,676,600원 = True-up 100% — Renewal·SCE 인상은 없습니다", 12)
rows = [
    ["구분", "25Y", "26Y", "증감액", "기여도"],
    ["EA Renewal 합계 (4사)", "747,999,000", "747,999,000",
     ("동결", {"align": PP_ALIGN.CENTER}), ("0%", {"align": PP_ALIGN.CENTER})],
    ["EA True-up 합계 (4사)", "186,198,600", "297,875,200",
     ("+111,676,600", {"color": ORANGE, "bold": True}),
     ("100%", {"align": PP_ALIGN.CENTER, "color": ORANGE, "bold": True})],
    ["SCE 합계 (4사)", "262,521,102", "262,521,102",
     ("동결", {"align": PP_ALIGN.CENTER}), ("0%", {"align": PP_ALIGN.CENTER})],
    ["총계", "1,196,718,702", "1,308,395,302", "+111,676,600",
     ("+9.3%", {"align": PP_ALIGN.CENTER, "bold": True, "color": ORANGE})],
]
add_text(s, MX, Inches(1.6), CW, Inches(0.25),
         [("증가 요인 분해 (단위: 원, VAT 별도)", 10, True, NAVY)])
clean_table(s, MX, Inches(1.95), CW, [2.3, 1.7, 1.7, 1.7, 0.9], rows,
            row_h=Inches(0.48), font_size=10.5)

add_text(s, MX, Inches(4.75), CW, Inches(0.28),
         [("26Y True-up 순증 구성 — 총 +244EA", 11, True, NAVY)])
tu = [("에스티젠바이오㈜", "+130EA", "300 → 430  ·  사업 확장에 따른 대규모 확충", ORANGE),
      ("동아에스티㈜", "+92EA", "1,249 → 1,341  ·  임직원 증가 반영", ORANGE),
      ("동아제약㈜", "+22EA", "687 → 709  ·  실사용 증가분 반영", NAVY),
      ("동아쏘시오홀딩스㈜", "0EA", "변동 없음", CAP)]
cw4 = int(CW) // 4
for i, (nm, n, d, c) in enumerate(tu):
    x = Emu(int(MX) + cw4 * i + (0 if i == 0 else int(Inches(0.3))))
    add_text(s, x, Inches(5.15), Emu(cw4 - int(Inches(0.35))), Inches(1.5),
             [(nm, 10, True, NAVY), (n, 22, True, c), (d, 8.5, False, CAP)],
             space_after=4)
    if i > 0:
        vline(s, Emu(int(MX) + cw4 * i), Inches(5.2), Inches(1.25), 0.75, HAIR)

# ══════════════════════════════════════════════════════════════
# 13. 계약 조건 및 향후 일정
# ══════════════════════════════════════════════════════════════
s = new_slide()
header(s, "11  |  TERMS & NEXT STEPS", "계약 조건 요약 및 진행 일정", 13, title_size=20)
rows = [
    ["항목", ("내용", {"align": PP_ALIGN.LEFT})],
    ["계약기간", ("2026. 03. 31 ~ 2028. 04. 01  (3년 차 갱신)", {"align": PP_ALIGN.LEFT})],
    ["계약 구성", ("EA(M365 E3) + SCE(서버·개발 인프라)", {"align": PP_ALIGN.LEFT})],
    ["단가 조건", ("EA Renewal·SCE 전 품목 전년 동결", {"align": PP_ALIGN.LEFT})],
    ["부가세", ("별도 (VAT 미포함 금액 기준)", {"align": PP_ALIGN.LEFT})],
    ["26Y 계약 총액", ("1,308,395,302원 (4사 합계)", {"align": PP_ALIGN.LEFT, "bold": True, "color": NAVY})],
]
add_text(s, MX, Inches(1.6), Inches(5.9), Inches(0.25),
         [("계약 조건", 10, True, NAVY)])
clean_table(s, MX, Inches(1.95), Inches(5.9), [1.0, 2.6], rows,
            row_h=Inches(0.46), total_rows=0)

sx = Inches(7.1)
add_text(s, sx, Inches(1.6), Inches(5.5), Inches(0.25),
         [("진행 일정 (제안)", 10, True, NAVY)])
steps = [
    ("STEP 1", "제안서 검토 및 회사별 수량 확정"),
    ("STEP 2", "견적 확정 및 내부 품의"),
    ("STEP 3", "계약 체결 (2026. 03. 31 발효)"),
    ("STEP 4", "갱신 적용 및 연중 True-up 관리 지원"),
]
for i, (st, d) in enumerate(steps):
    y = Emu(int(Inches(2.0)) + i * int(Inches(0.72)))
    add_text(s, sx, y, Inches(0.9), Inches(0.5), [(st, 10.5, True, ORANGE)],
             anchor=MSO_ANCHOR.MIDDLE)
    add_text(s, Emu(int(sx) + int(Inches(1.0))), y, Inches(4.4), Inches(0.5),
             [(d, 11, False, BODY)], anchor=MSO_ANCHOR.MIDDLE)
    hline(s, sx, Emu(int(y) + int(Inches(0.58))), Inches(5.5), 0.5, HAIR)

add_text(s, MX, Inches(5.5), CW, Inches(1.2),
         [([("지원 사항  ", 10, True, ORANGE),
            ("계약 기간 중 라이선스 컴플라이언스 점검, True-up 수량 관리, SecureON MS Unified Support 기반 기술 지원 및 전담 담당자를 통한 구매 문의 대응을 제공합니다.",
             10.5, False, BODY)],)])

# ══════════════════════════════════════════════════════════════
# 14. 맺음말
# ══════════════════════════════════════════════════════════════
s = new_slide()
add_rect(s, Inches(10.5), Inches(-0.5), Inches(3.5), Inches(8.5), FILLG)
add_rect(s, MX, Inches(1.6), Inches(0.14), Inches(0.14), ORANGE)
add_text(s, Inches(0.95), Inches(1.54), Inches(9), Inches(0.3),
         [("CLOSING", 11, True, CAP)])
add_text(s, MX, Inches(2.2), Inches(10.5), Inches(0.8),
         [("감사합니다", 32, True, NAVY)])
add_text(s, MX, Inches(3.25), Inches(9.8), Inches(2.2),
         [([("—  ", 12, True, ORANGE),
            ("기존 비용은 동결로 지키고, 성장에 필요한 만큼만 더하는 갱신을 제안드립니다.", 13, True, NAVY)],),
          ([("—  ", 12, True, ORANGE),
            ("동아그룹 4개사의 안정적인 Microsoft 업무·서버 환경과 사업 확장을 계속 지원하겠습니다.", 12, False, BODY)],),
          ([("—  ", 12, True, ORANGE),
            ("제안서 검토 후 수량 확정을 요청드리며, 2026년 3월 31일 계약 발효를 목표로 진행하겠습니다.", 12, False, BODY)],)],
         space_after=12)
add_text(s, MX, Inches(5.6), Inches(9.8), Inches(0.5),
         [("본 제안서의 금액은 부가세 별도 기준이며, 최종 수량 확정 시 일부 조정될 수 있습니다.",
           9, False, CAP)])
add_rect(s, 0, Inches(7.34), SW, Inches(0.16), ORANGE)

out = "동아그룹_Microsoft_EA_SCE_갱신제안서_2026.pptx"
prs.save(out)
print(f"saved: {out}, slides: {len(prs.slides._sldIdLst)}")
