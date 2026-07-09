# -*- coding: utf-8 -*-
"""동아그룹 4개사 Microsoft EA 갱신 제안서 PPTX 생성 스크립트."""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn

# ── 색상/폰트 ────────────────────────────────────────────────
NAVY = RGBColor(0x12, 0x31, 0x4E)
BLUE = RGBColor(0x2E, 0x75, 0xB6)
LIGHT = RGBColor(0xDE, 0xEB, 0xF7)
LIGHTER = RGBColor(0xF2, 0xF7, 0xFC)
ORANGE = RGBColor(0xE8, 0x6C, 0x1A)
GRAY = RGBColor(0x59, 0x59, 0x59)
DARK = RGBColor(0x21, 0x21, 0x21)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
FONT = "맑은 고딕"

SW, SH = Inches(13.333), Inches(7.5)


def style_run(run, size, bold=False, color=DARK, italic=False):
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
    """lines: [(text, size, bold, color), ...] 또는 [("텍스트", size), ...]"""
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = wrap
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    for i, spec in enumerate(lines):
        text, size = spec[0], spec[1]
        bold = spec[2] if len(spec) > 2 else False
        color = spec[3] if len(spec) > 3 else DARK
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.space_after = Pt(space_after)
        r = p.add_run()
        r.text = text
        style_run(r, size, bold, color)
    return tb


def add_rect(slide, x, y, w, h, fill, line=None, shadow=False):
    sp = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, h)
    sp.fill.solid()
    sp.fill.fore_color.rgb = fill
    if line:
        sp.line.color.rgb = line
        sp.line.width = Pt(0.75)
    else:
        sp.line.fill.background()
    sp.shadow.inherit = False
    return sp


def header(slide, title, page_no=None, subtitle=None):
    add_rect(slide, 0, 0, SW, Inches(0.92), NAVY)
    add_rect(slide, 0, Inches(0.92), SW, Pt(3), ORANGE)
    add_text(slide, Inches(0.55), Inches(0.14), Inches(11), Inches(0.66),
             [(title, 22, True, WHITE)], anchor=MSO_ANCHOR.MIDDLE)
    if subtitle:
        add_text(slide, Inches(0.55), Inches(1.08), Inches(12.2), Inches(0.35),
                 [(subtitle, 12, False, GRAY)])
    # footer
    add_text(slide, Inches(0.55), Inches(7.12), Inches(8), Inches(0.3),
             [("동아그룹 Microsoft EA 라이선스 갱신 제안서  |  2026.02.06 ~ 2028.02.05", 9, False, GRAY)])
    if page_no is not None:
        add_text(slide, Inches(12.35), Inches(7.12), Inches(0.6), Inches(0.3),
                 [(str(page_no), 10, False, GRAY)], align=PP_ALIGN.RIGHT)


def set_cell(cell, text, size=11, bold=False, color=DARK, fill=None,
             align=PP_ALIGN.LEFT):
    if fill is not None:
        cell.fill.solid()
        cell.fill.fore_color.rgb = fill
    cell.vertical_anchor = MSO_ANCHOR.MIDDLE
    cell.margin_left, cell.margin_right = Inches(0.08), Inches(0.08)
    cell.margin_top = cell.margin_bottom = Inches(0.02)
    tf = cell.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    r = p.add_run()
    r.text = text
    style_run(r, size, bold, color)


def add_table(slide, x, y, w, col_ratios, rows, header_fill=NAVY,
              row_h=Inches(0.42), font_size=11):
    """rows[0]은 헤더. rows: [[(text, opts), ...] or [text, ...]]"""
    n_r, n_c = len(rows), len(rows[0])
    gf = slide.shapes.add_table(n_r, n_c, x, y, w, row_h * n_r)
    table = gf.table
    total = sum(col_ratios)
    for i, ratio in enumerate(col_ratios):
        table.columns[i].width = Emu(int(int(w) * ratio / total))
    for ri, row in enumerate(rows):
        table.rows[ri].height = row_h
        for ci, spec in enumerate(row):
            if isinstance(spec, tuple):
                text, opts = spec
            else:
                text, opts = spec, {}
            cell = table.cell(ri, ci)
            if ri == 0:
                set_cell(cell, text, font_size, True, WHITE, header_fill,
                         PP_ALIGN.CENTER)
            else:
                fill = opts.get("fill", WHITE if ri % 2 else LIGHTER)
                set_cell(cell, text, opts.get("size", font_size),
                         opts.get("bold", False), opts.get("color", DARK),
                         fill, opts.get("align",
                                        PP_ALIGN.RIGHT if ci >= 2 else PP_ALIGN.CENTER))
    return table


prs = Presentation()
prs.slide_width, prs.slide_height = SW, SH
BLANK = prs.slide_layouts[6]


def new_slide():
    return prs.slides.add_slide(BLANK)


# ══════════════════════════════════════════════════════════════
# 1. 표지
# ══════════════════════════════════════════════════════════════
s = new_slide()
add_rect(s, 0, 0, SW, SH, NAVY)
add_rect(s, 0, Inches(4.55), SW, Pt(3), ORANGE)
add_text(s, Inches(1.0), Inches(2.0), Inches(11.3), Inches(0.5),
         [("Microsoft Enterprise Agreement", 20, True, RGBColor(0x9D, 0xC3, 0xE6))])
add_text(s, Inches(1.0), Inches(2.55), Inches(11.3), Inches(1.8),
         [("동아그룹 주요 4개사", 40, True, WHITE),
          ("Microsoft EA 라이선스 갱신 제안서", 40, True, WHITE)], space_after=8)
add_text(s, Inches(1.0), Inches(3.95), Inches(11.3), Inches(0.5),
         [("지난 3년간 쌓아온 신뢰를 바탕으로, 다음 성장 단계까지 함께하겠습니다.",
           14, False, RGBColor(0xBD, 0xD7, 0xEE))])
add_text(s, Inches(1.0), Inches(4.85), Inches(11.3), Inches(1.6),
         [("계약기간  |  2026. 02. 06 ~ 2028. 02. 05 (3년 차 갱신)", 16, True, WHITE),
          ("대상  |  동아쏘시오홀딩스㈜ · 동아에스티㈜ · 동아제약㈜ · 에스티젠바이오㈜",
           14, False, RGBColor(0xBD, 0xD7, 0xEE)),
          ("2026년 7월", 12, False, RGBColor(0x8E, 0xA9, 0xC1))], space_after=10)

# ══════════════════════════════════════════════════════════════
# 2. 목차
# ══════════════════════════════════════════════════════════════
s = new_slide()
header(s, "목차 (Contents)", 2)
toc = [
    ("01", "제안 개요 (Executive Summary)"),
    ("02", "EA 계약 구조 및 단가 기준"),
    ("03", "주요 4사 요약 비교"),
    ("04", "회사별 제안 — 동아쏘시오홀딩스㈜"),
    ("05", "회사별 제안 — 동아에스티㈜"),
    ("06", "회사별 제안 — 동아제약㈜"),
    ("07", "회사별 제안 — 에스티젠바이오㈜"),
    ("08", "증감 요인 분석"),
    ("09", "계약 조건 및 향후 일정"),
]
for i, (no, title) in enumerate(toc):
    col = i // 5
    row = i % 5
    x = Inches(0.9 + col * 6.3)
    y = Inches(1.7 + row * 1.0)
    add_rect(s, x, y, Inches(0.75), Inches(0.75), LIGHT)
    add_text(s, x, y, Inches(0.75), Inches(0.75), [(no, 18, True, BLUE)],
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    add_text(s, x + Inches(1.0), y, Inches(5.0), Inches(0.75),
             [(title, 15, True, DARK)], anchor=MSO_ANCHOR.MIDDLE)

# ══════════════════════════════════════════════════════════════
# 3. 제안 개요
# ══════════════════════════════════════════════════════════════
s = new_slide()
header(s, "01. 제안 개요 (Executive Summary)", 3,
       "Microsoft EA 3년 차 갱신 — Renewal 전액 동결, 증가분은 전액 사업 성장(True-up)에 기인")

# 좌: 계약 개요
add_rect(s, Inches(0.55), Inches(1.55), Inches(5.6), Inches(0.5), NAVY)
add_text(s, Inches(0.75), Inches(1.55), Inches(5.2), Inches(0.5),
         [("계약 개요", 13, True, WHITE)], anchor=MSO_ANCHOR.MIDDLE)
rows = [
    ["구분", "내용"],
    [("계약 유형", {"align": PP_ALIGN.CENTER}),
     ("Microsoft EA (Enterprise Agreement) 3년 차 갱신", {"align": PP_ALIGN.LEFT})],
    [("계약기간", {"align": PP_ALIGN.CENTER}),
     ("2026. 02. 06 ~ 2028. 02. 05", {"align": PP_ALIGN.LEFT})],
    [("대상 법인", {"align": PP_ALIGN.CENTER}),
     ("동아쏘시오홀딩스, 동아에스티, 동아제약, 에스티젠바이오", {"align": PP_ALIGN.LEFT, "size": 10})],
    [("단가 기준", {"align": PP_ALIGN.CENTER}),
     ("Renewal 390,600원/명 · True-up 457,800원/명 (VAT 별도)", {"align": PP_ALIGN.LEFT, "size": 10})],
]
add_table(s, Inches(0.55), Inches(2.05), Inches(5.6), [1, 3], rows,
          row_h=Inches(0.52), font_size=11)

# 우: 26Y 총액 하이라이트
add_rect(s, Inches(6.55), Inches(1.55), Inches(6.2), Inches(3.1), LIGHTER, line=LIGHT)
add_text(s, Inches(6.95), Inches(1.85), Inches(5.5), Inches(2.6),
         [("주요 4사 EA 합계 (VAT 별도)", 13, True, GRAY),
          ("25Y  934,197,600원", 20, False, GRAY),
          ("26Y  1,045,874,200원", 28, True, NAVY),
          ("전년 대비 +12.0%  (증가액 111,676,600원)", 14, True, ORANGE)],
         space_after=12)

# 하단: 핵심 포인트 3개
points = [
    ("Renewal 100% 동결", "4개사 전 인원의 갱신 단가·금액이\n전년과 동일 — 예산 변동 리스크 없음"),
    ("증가분 = 100% True-up", "26Y 증가액 1.1억원은 전액 신규 인원 정산분,\n계약 단가 인상 요인은 전혀 없음"),
    ("성장이 만든 증가", "동아에스티 +168명 · 에스티젠바이오 +214명,\n사업 확장이 낳은 자연스러운 결과"),
]
for i, (t, d) in enumerate(points):
    x = Inches(0.55 + i * 4.18)
    add_rect(s, x, Inches(4.95), Inches(3.95), Inches(1.85), WHITE, line=BLUE)
    add_rect(s, x, Inches(4.95), Inches(3.95), Inches(0.5), BLUE)
    add_text(s, x + Inches(0.2), Inches(4.95), Inches(3.55), Inches(0.5),
             [(t, 13, True, WHITE)], anchor=MSO_ANCHOR.MIDDLE)
    add_text(s, x + Inches(0.2), Inches(5.6), Inches(3.55), Inches(1.1),
             [(line, 10.5, False, DARK) for line in d.split("\n")], space_after=2)

# ══════════════════════════════════════════════════════════════
# 4. EA 계약 구조 및 단가
# ══════════════════════════════════════════════════════════════
s = new_slide()
header(s, "02. EA 계약 구조 및 단가 기준", 4,
       "Enterprise Agreement — 3년 약정 볼륨 라이선스, 연 단위 정산 구조")

boxes = [
    ("Renewal (기존 갱신)", "390,600원 / 명 (VAT 별도)",
     ["EA 등록 기준 인원에 대한 연간 갱신 금액",
      "약정 단가로 3년간 안정적 예산 운영 가능",
      "금회 갱신 시 4개사 전체 단가·금액 동결"]),
    ("True-up (추가 구매)", "457,800원 / 명 (VAT 별도)",
     ["연중 증가한 사용 인원을 연 1회 일괄 정산",
      "선구매 부담 없이 실제 증가분만 사후 반영",
      "차년도부터 Renewal 기준 수량에 편입"]),
]
for i, (t, price, items) in enumerate(boxes):
    x = Inches(0.55 + i * 6.45)
    add_rect(s, x, Inches(1.75), Inches(6.2), Inches(3.3), WHITE, line=BLUE)
    add_rect(s, x, Inches(1.75), Inches(6.2), Inches(0.62), NAVY)
    add_text(s, x + Inches(0.25), Inches(1.75), Inches(5.7), Inches(0.62),
             [(t, 15, True, WHITE)], anchor=MSO_ANCHOR.MIDDLE)
    add_text(s, x + Inches(0.25), Inches(2.55), Inches(5.7), Inches(0.5),
             [(price, 17, True, BLUE)])
    add_text(s, x + Inches(0.25), Inches(3.2), Inches(5.7), Inches(1.7),
             [("·  " + it, 12, False, DARK) for it in items], space_after=8)

add_rect(s, Inches(0.55), Inches(5.45), Inches(12.2), Inches(1.3), LIGHTER, line=LIGHT)
add_text(s, Inches(0.85), Inches(5.65), Inches(11.6), Inches(0.95),
         [("EA 정산 사이클", 12, True, NAVY),
          ("계약 발효 (매년 2/6)  →  연중 사용 인원 증가  →  연 1회 True-up 정산  →  차기 연도 Renewal 수량 반영",
           12, False, DARK)], space_after=6)

# ══════════════════════════════════════════════════════════════
# 5. 주요 4사 요약 비교
# ══════════════════════════════════════════════════════════════
s = new_slide()
header(s, "03. 주요 4사 요약 비교", 5,
       "25Y 대비 26Y EA 비용 비교 — 증가분은 전액 True-up(신규 인원) 반영분 (단위: 원, VAT 별도)")

R = PP_ALIGN.RIGHT
C = PP_ALIGN.CENTER
rows = [
    ["구분", "25Y 금액", "26Y 금액", "증감액", "증감률", "주요 사유"],
    [("동아쏘시오홀딩스㈜", {"align": C}), "36,204,000", "36,204,000",
     ("—", {"align": C}), ("0%", {"align": C, "bold": True}),
     ("전년 동결 (인원 변동 없음)", {"align": PP_ALIGN.LEFT, "size": 10})],
    [("동아에스티㈜", {"align": C}), "494,797,800",
     ("539,788,200", {"bold": True}), "+44,990,400",
     ("+9.1%", {"align": C, "bold": True, "color": ORANGE}),
     ("25년 True-up 168명 추가", {"align": PP_ALIGN.LEFT, "size": 10})],
    [("동아제약㈜", {"align": C}), "275,801,400",
     ("282,973,600", {"bold": True}), "+7,172,200",
     ("+2.6%", {"align": C, "bold": True, "color": ORANGE}),
     ("25년 True-up 22명 추가", {"align": PP_ALIGN.LEFT, "size": 10})],
    [("에스티젠바이오㈜", {"align": C}), "127,394,400",
     ("186,908,400", {"bold": True}), "+59,514,000",
     ("+46.7%", {"align": C, "bold": True, "color": ORANGE}),
     ("사업 확장, True-up 214명 대폭 추가", {"align": PP_ALIGN.LEFT, "size": 10})],
    [("합계", {"align": C, "bold": True, "fill": LIGHT}),
     ("934,197,600", {"bold": True, "fill": LIGHT}),
     ("1,045,874,200", {"bold": True, "fill": LIGHT, "color": NAVY}),
     ("+111,676,600", {"bold": True, "fill": LIGHT}),
     ("+12.0%", {"align": C, "bold": True, "fill": LIGHT, "color": ORANGE}),
     ("", {"fill": LIGHT})],
]
add_table(s, Inches(0.55), Inches(1.75), Inches(12.2),
          [2.1, 1.7, 1.7, 1.6, 1.0, 2.6], rows, row_h=Inches(0.56), font_size=12)

add_rect(s, Inches(0.55), Inches(5.5), Inches(12.2), Inches(1.25), LIGHTER, line=LIGHT)
add_text(s, Inches(0.85), Inches(5.68), Inches(11.6), Inches(0.95),
         [("핵심 요약", 12, True, NAVY),
          ("· 4개사 모두 Renewal(기존 인원)은 전년 금액 그대로 동결되었으며, 증가액 111,676,600원은 전액 25년 True-up 404명(동아에스티 168 · 동아제약 22 · 에스티젠바이오 214)의 신규 정산분입니다.",
           11, False, DARK)], space_after=5)

# ══════════════════════════════════════════════════════════════
# 6~9. 회사별 페이지
# ══════════════════════════════════════════════════════════════
companies = [
    dict(
        no="04", name="동아쏘시오홀딩스㈜", page=6, rate="0%", rate_color=BLUE,
        badge="전년 동결",
        sub="그룹 지주회사 — 인원 변동 없이 기존 계약 조건 그대로 유지 (단위: 원, VAT 별도)",
        renewal=("88명", "34,372,800", "34,372,800", "동결"),
        trueup=("24Y 4명 · 25Y 0명", "1,831,200", "1,831,200", "동결"),
        total=("—", "36,204,000", "36,204,000", "0%"),
        reasons=[
            "Renewal 88명과 기존 True-up 4명(24년) 모두 전년과 동일한 조건으로 유지되어 26Y 금액이 100% 동결됩니다.",
            "25년 한 해 신규 True-up 인원이 발생하지 않아, 지주회사의 안정적인 조직 운영 기조를 그대로 보여줍니다.",
            "3년 차 갱신에도 단가 인상 없이 기존 조건이 이어져, 예측 가능한 IT 예산 운영이 가능합니다.",
        ],
    ),
    dict(
        no="05", name="동아에스티㈜", page=7, rate="+9.1%", rate_color=ORANGE,
        badge="사업 확장 반영",
        sub="전문의약품 사업 성장 — 25년 True-up 168명 추가 반영 (단위: 원, VAT 별도)",
        renewal=("1,103명", "430,831,800", "430,831,800", "동결"),
        trueup=("24Y 70명 · 25Y 168명", "63,966,000", "108,956,400", "+70.3%"),
        total=("1,249EA → 1,341EA", "494,797,800", "539,788,200", "+9.1%"),
        reasons=[
            "Renewal 1,103명 금액은 전년과 동일하게 전액 동결되어, 기존 라이선스 비용 부담은 그대로입니다.",
            "26Y 증가액 44,990,400원은 100% 25년 True-up 168명의 신규 정산분 — 비용 인상이 아니라 임직원 증가에 따른 사업 확장의 결과입니다.",
            "26Y 기준 총 1,341EA로 확대되어, 성장하는 조직 전체에 전사 표준 협업 환경을 빠짐없이 확장 적용합니다.",
        ],
    ),
    dict(
        no="06", name="동아제약㈜", page=8, rate="+2.6%", rate_color=ORANGE,
        badge="소폭 증가",
        sub="일반의약품·컨슈머헬스케어 — 25년 True-up 22명 추가 반영 (단위: 원, VAT 별도)",
        renewal=("576명", "224,985,600", "224,985,600", "동결"),
        trueup=("24Y 111명 · 25Y 22명", "50,815,800", "57,988,000", "+14.1%"),
        total=("687EA → 709EA", "275,801,400", "282,973,600", "+2.6%"),
        reasons=[
            "Renewal 576명 금액은 전년과 동일하게 전액 동결되어, 기존 계약 조건에는 변동이 없습니다.",
            "26Y 증가액 7,172,200원은 25년 True-up 22명의 신규 정산분으로, 실사용 증가분만 최소 수준으로 반영되었습니다.",
            "26Y 기준 총 709EA로, 전년 대비 2.6%의 안정적인 증가 흐름을 유지합니다.",
        ],
    ),
    dict(
        no="07", name="에스티젠바이오㈜", page=9, rate="+46.7%", rate_color=ORANGE,
        badge="사업 확장 대폭 반영",
        sub="바이오의약품 사업 확장 — 25년 True-up 214명 대폭 추가 (단위: 원, VAT 별도)",
        renewal=("148명", "57,808,800", "57,808,800", "동결"),
        trueup=("24Y 68명 · 25Y 214명", "69,585,600", "129,099,600", "+85.5%"),
        total=("300EA → 430EA", "127,394,400", "186,908,400", "+46.7%"),
        reasons=[
            "Renewal 148명 금액은 전년과 동일하게 전액 동결되어, 기존 계약 조건에는 변동이 없습니다.",
            "26Y 증가액 59,514,000원은 100% 25년 True-up 214명의 신규 정산분 — 바이오의약품 사업의 본격적인 확장과 대규모 채용이 만들어낸 결과입니다.",
            "26Y 기준 총 430EA로 전년 대비 43% 이상 확대되어, 4개사 중 가장 가파른 성장세를 보여줍니다.",
        ],
    ),
]

for co in companies:
    s = new_slide()
    header(s, f"{co['no']}. 회사별 제안 — {co['name']}", co["page"], co["sub"])

    # 좌측 상단: 증감률 스탯 + 배지
    add_rect(s, Inches(0.55), Inches(1.7), Inches(3.5), Inches(1.9), NAVY)
    add_text(s, Inches(0.85), Inches(1.95), Inches(2.9), Inches(1.45),
             [("26Y 증감률 (전년比)", 11, False, RGBColor(0xBD, 0xD7, 0xEE)),
              (co["rate"], 34, True, WHITE),
              (co["badge"], 12, True, RGBColor(0xFF, 0xC0, 0x7A))], space_after=6)

    # 우측 상단: 내역 테이블
    r_qty, r25, r26, r_note = co["renewal"]
    t_qty, t25, t26, t_note = co["trueup"]
    g_qty, g25, g26, g_rate = co["total"]
    rows = [
        ["구분", "수량", "25Y 금액", "26Y 금액", "증감"],
        [("Renewal (기존 갱신)", {"align": PP_ALIGN.LEFT}), (r_qty, {"align": C, "size": 10}),
         r25, r26, (r_note, {"align": C})],
        [("True-up (추가 구매)", {"align": PP_ALIGN.LEFT}), (t_qty, {"align": C, "size": 10}),
         t25, t26, (t_note, {"align": C, "bold": t_note != "동결",
                             "color": ORANGE if t_note != "동결" else DARK})],
        [("EA 소계", {"align": PP_ALIGN.LEFT, "bold": True, "fill": LIGHT}),
         (g_qty, {"align": C, "size": 10, "fill": LIGHT}),
         (g25, {"bold": True, "fill": LIGHT}),
         (g26, {"bold": True, "fill": LIGHT, "color": NAVY}),
         (g_rate, {"align": C, "bold": True, "fill": LIGHT, "color": co["rate_color"]})],
    ]
    add_table(s, Inches(4.35), Inches(1.7), Inches(8.4),
              [2.2, 2.0, 1.7, 1.7, 1.0], rows, row_h=Inches(0.55), font_size=11)

    # 하단: 비용 변동 사유
    add_rect(s, Inches(0.55), Inches(4.3), Inches(12.2), Inches(0.5), BLUE)
    add_text(s, Inches(0.8), Inches(4.3), Inches(11.7), Inches(0.5),
             [("25Y → 26Y 비용 변동 사유", 13, True, WHITE)], anchor=MSO_ANCHOR.MIDDLE)
    add_rect(s, Inches(0.55), Inches(4.8), Inches(12.2), Inches(2.05), LIGHTER, line=LIGHT)
    add_text(s, Inches(0.85), Inches(5.0), Inches(11.6), Inches(1.7),
             [("·  " + r, 12, False, DARK) for r in co["reasons"]], space_after=8)

# ══════════════════════════════════════════════════════════════
# 10. 증감 요인 분석
# ══════════════════════════════════════════════════════════════
s = new_slide()
header(s, "08. 증감 요인 분석", 10,
       "26Y 증가액 111,676,600원의 구성 — Renewal 0원, True-up 100% (단위: 원, VAT 별도)")

rows = [
    ["구분", "25Y", "26Y", "증감액", "비중"],
    [("Renewal 합계 (4사)", {"align": PP_ALIGN.LEFT}), "747,999,000", "747,999,000",
     ("동결 (0)", {"align": C, "bold": True, "color": BLUE}), ("0%", {"align": C})],
    [("True-up 합계 (4사)", {"align": PP_ALIGN.LEFT}), "186,198,600",
     ("297,875,200", {"bold": True}),
     ("+111,676,600", {"bold": True, "color": ORANGE}),
     ("100%", {"align": C, "bold": True, "color": ORANGE})],
    [("합계", {"align": PP_ALIGN.LEFT, "bold": True, "fill": LIGHT}),
     ("934,197,600", {"bold": True, "fill": LIGHT}),
     ("1,045,874,200", {"bold": True, "fill": LIGHT, "color": NAVY}),
     ("+111,676,600", {"bold": True, "fill": LIGHT}),
     ("+12.0%", {"align": C, "bold": True, "fill": LIGHT, "color": ORANGE})],
]
add_table(s, Inches(0.55), Inches(1.75), Inches(12.2), [2.4, 1.9, 1.9, 1.9, 1.1],
          rows, row_h=Inches(0.58), font_size=12)

# 25년 True-up 인원 구성
add_rect(s, Inches(0.55), Inches(4.35), Inches(12.2), Inches(0.5), NAVY)
add_text(s, Inches(0.8), Inches(4.35), Inches(11.7), Inches(0.5),
         [("25년 True-up 신규 인원 구성 — 총 404명", 13, True, WHITE)],
         anchor=MSO_ANCHOR.MIDDLE)
tu = [("에스티젠바이오", "214명", "사업 확장에 따른 대규모 인력 확충"),
      ("동아에스티", "168명", "사업 성장에 따른 임직원 증가"),
      ("동아제약", "22명", "실사용 증가분 반영"),
      ("동아쏘시오홀딩스", "0명", "인원 변동 없음")]
for i, (nm, n, d) in enumerate(tu):
    x = Inches(0.55 + i * 3.11)
    add_rect(s, x, Inches(5.0), Inches(2.9), Inches(1.75), WHITE, line=BLUE)
    add_text(s, x + Inches(0.15), Inches(5.15), Inches(2.6), Inches(1.5),
             [(nm, 11.5, True, NAVY), (n, 22, True, ORANGE if n != "0명" else GRAY),
              (d, 9.5, False, GRAY)], space_after=4)

# ══════════════════════════════════════════════════════════════
# 11. 계약 조건 및 향후 일정
# ══════════════════════════════════════════════════════════════
s = new_slide()
header(s, "09. 계약 조건 및 향후 일정", 11)

add_rect(s, Inches(0.55), Inches(1.6), Inches(6.0), Inches(0.5), NAVY)
add_text(s, Inches(0.8), Inches(1.6), Inches(5.5), Inches(0.5),
         [("계약 조건 요약", 13, True, WHITE)], anchor=MSO_ANCHOR.MIDDLE)
rows = [
    ["항목", "내용"],
    [("계약기간", {"align": C}), ("2026. 02. 06 ~ 2028. 02. 05 (3년 차 갱신)", {"align": PP_ALIGN.LEFT})],
    [("Renewal 단가", {"align": C}), ("390,600원/명 — 전년 동결", {"align": PP_ALIGN.LEFT})],
    [("True-up 단가", {"align": C}), ("457,800원/명 — 연 1회 정산", {"align": PP_ALIGN.LEFT})],
    [("부가세", {"align": C}), ("별도 (VAT 미포함 금액 기준)", {"align": PP_ALIGN.LEFT})],
    [("26Y 계약 총액", {"align": C}), ("1,045,874,200원 (4사 합계)", {"align": PP_ALIGN.LEFT, "bold": True})],
]
add_table(s, Inches(0.55), Inches(2.1), Inches(6.0), [1, 2.4], rows,
          row_h=Inches(0.5), font_size=11)

add_rect(s, Inches(7.05), Inches(1.6), Inches(5.7), Inches(0.5), NAVY)
add_text(s, Inches(7.3), Inches(1.6), Inches(5.2), Inches(0.5),
         [("향후 진행 일정 (제안)", 13, True, WHITE)], anchor=MSO_ANCHOR.MIDDLE)
steps = [
    ("STEP 1", "제안서 검토 및 회사별 수량 확정"),
    ("STEP 2", "견적 확정 및 내부 품의"),
    ("STEP 3", "계약 체결 (2026. 02. 06 발효)"),
    ("STEP 4", "라이선스 갱신 적용 및 연중 True-up 관리"),
]
for i, (st, d) in enumerate(steps):
    y = Inches(2.25 + i * 0.78)
    add_rect(s, Inches(7.05), y, Inches(1.1), Inches(0.6), LIGHT)
    add_text(s, Inches(7.05), y, Inches(1.1), Inches(0.6), [(st, 10, True, BLUE)],
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    add_text(s, Inches(8.35), y, Inches(4.4), Inches(0.6), [(d, 11.5, False, DARK)],
             anchor=MSO_ANCHOR.MIDDLE)

add_rect(s, Inches(0.55), Inches(5.55), Inches(12.2), Inches(1.2), LIGHTER, line=LIGHT)
add_text(s, Inches(0.85), Inches(5.72), Inches(11.6), Inches(0.9),
         [("지원 사항", 12, True, NAVY),
          ("· 계약 기간 중 라이선스 컴플라이언스 점검, True-up 수량 관리, 전담 담당자를 통한 기술·구매 문의 대응을 지원합니다.",
           11, False, DARK)], space_after=5)

# ══════════════════════════════════════════════════════════════
# 12. 맺음말
# ══════════════════════════════════════════════════════════════
s = new_slide()
add_rect(s, 0, 0, SW, SH, NAVY)
add_rect(s, 0, Inches(3.4), SW, Pt(3), ORANGE)
add_text(s, Inches(1.0), Inches(2.3), Inches(11.3), Inches(1.0),
         [("감사합니다", 40, True, WHITE)])
add_text(s, Inches(1.0), Inches(3.7), Inches(11.3), Inches(2.0),
         [("지난 3년간 쌓아온 신뢰를 바탕으로, 동아그룹의 다음 성장 단계까지 함께하겠습니다.",
           16, True, RGBColor(0xBD, 0xD7, 0xEE)),
          ("안정적인 Microsoft 업무 환경으로 4개사의 지속적인 사업 성장을 뒷받침하겠습니다.",
           13, False, RGBColor(0x9D, 0xC3, 0xE6)),
          ("본 제안서의 금액은 부가세 별도 기준이며, 최종 수량 확정 시 일부 조정될 수 있습니다.",
           11, False, RGBColor(0x8E, 0xA9, 0xC1))], space_after=10)

out = "동아그룹_Microsoft_EA_갱신제안서_2026.pptx"
prs.save(out)
print(f"saved: {out}, slides: {len(prs.slides.__iter__.__self__._sldIdLst)}")
