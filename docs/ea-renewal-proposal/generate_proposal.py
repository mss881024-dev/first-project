# -*- coding: utf-8 -*-
"""동아그룹 4개사 Microsoft 라이선스 갱신 제안서 PPTX 생성 스크립트 (v3).

v3: EA + SCE + 기타 라이선스(Copilot·Teams Pro·Easy Tree) 통합, 15페이지.
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
ORANGE = RGBColor(0xE8, 0x6C, 0x1A)    # 단일 액센트(증가)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
FONT = "맑은 고딕"

SW, SH = Inches(13.333), Inches(7.5)
MX = Inches(0.7)                        # 좌우 마진
CW = Inches(11.933)                     # 콘텐츠 폭
TOTAL_PAGES = 15
DOC_FOOT = "동아그룹 Microsoft 라이선스 갱신 제안서  |  2024.03.31 ~ 2027.04.01"


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
    hline(slide, MX, Inches(7.08), CW, 0.5, HAIR)
    add_text(slide, MX, Inches(7.15), Inches(9), Inches(0.28),
             [(DOC_FOOT, 8.5, False, CAP)])
    add_text(slide, Inches(11.6), Inches(7.15), Inches(1.03), Inches(0.28),
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


C = PP_ALIGN.CENTER
L = PP_ALIGN.LEFT

# ══════════════════════════════════════════════════════════════
# 1. 표지
# ══════════════════════════════════════════════════════════════
s = new_slide()
add_rect(s, Inches(10.5), Inches(-0.5), Inches(3.5), Inches(8.5), FILLG)
add_rect(s, MX, Inches(1.15), Inches(0.14), Inches(0.14), ORANGE)
add_text(s, Inches(0.95), Inches(1.09), Inches(10), Inches(0.3),
         [("MICROSOFT LICENSE RENEWAL  ·  EA / SCE / COPILOT & OTHERS",
           11, True, CAP)])
add_text(s, MX, Inches(1.85), Inches(11), Inches(1.9),
         [("동아그룹 주요 4개사", 34, True, NAVY),
          ("Microsoft 라이선스 갱신 제안서", 34, True, NAVY)], space_after=8)
hline(s, MX, Inches(3.75), Inches(9.0), 0.75, HAIR)
add_text(s, MX, Inches(4.05), Inches(10.5), Inches(1.7),
         [([("계약기간   ", 12, True, NAVY),
            ("2024. 03. 31 ~ 2027. 04. 01  (3년 차 갱신)", 12, False, BODY)],),
          ([("계약 구성   ", 12, True, NAVY),
            ("EA(M365 E3) · SCE(서버) · 기타 라이선스(Copilot 등)", 12, False, BODY)],),
          ([("대상 법인   ", 12, True, NAVY),
            ("동아쏘시오홀딩스㈜ · 동아에스티㈜ · 동아제약㈜ · 에스티젠바이오㈜",
             12, False, BODY)],),
          ([("금액 기준   ", 12, True, NAVY),
            ("부가세(VAT) 별도", 12, False, BODY)],),
          ("2026년 7월", 10.5, False, CAP)], space_after=9)
add_rect(s, 0, Inches(7.34), SW, Inches(0.16), ORANGE)

# ══════════════════════════════════════════════════════════════
# 2. 목차
# ══════════════════════════════════════════════════════════════
s = new_slide()
header(s, "CONTENTS", "목차", 2, title_size=22)
toc = [
    ("01", "제안 개요 (Executive Summary)"),
    ("02", "계약 구조 및 갱신 원칙"),
    ("03", "주요 4사 총계 비교"),
    ("04", "EA 라이선스 요약"),
    ("05", "SCE 라이선스 요약"),
    ("06", "기타 라이선스 요약"),
    ("07", "회사별 상세 — 동아쏘시오홀딩스㈜"),
    ("08", "회사별 상세 — 동아에스티㈜"),
    ("09", "회사별 상세 — 동아제약㈜"),
    ("10", "회사별 상세 — 에스티젠바이오㈜"),
    ("11", "증감 요인 분석"),
    ("12", "계약 조건 및 향후 일정"),
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
       "26Y 총 계약 1,317백만 원(+3.9%) — 성장 비용을 라이선스 최적화로 상쇄했습니다", 3,
       title_size=18)
stat_band(s, MX, Inches(1.6), CW, [
    ("26Y 총 계약 금액 (VAT 별도)", "1,316,794,600원", NAVY, "25Y 1,267,881,200원"),
    ("전년 대비 증감", "+3.9%", ORANGE, "순증 48,913,400원"),
    ("기타 라이선스 최적화", "-88%", NAVY, "Copilot 조정 · Easy Tree 종료"),
], big=24, band_h=Inches(1.15))
hline(s, MX, Inches(2.95), CW, 0.5, HAIR)

rows = [
    ["구분", "25Y", "26Y", "증감률"],
    ["EA 라이선스 (M365 E3)", "934,197,600", "1,045,874,200",
     ("+12%", {"color": ORANGE, "bold": True, "align": C})],
    ["SCE 라이선스 (서버)", "262,521,102", "262,521,102", ("0%", {"align": C})],
    ["기타 라이선스", "71,164,800", "8,404,200",
     ("-88%", {"color": NAVY, "bold": True, "align": C})],
    ["단수 조정", "-2,302", "-4,902", ("—", {"align": C})],
    ["총 합계", "1,267,881,200", "1,316,794,600",
     ("+3.9%", {"align": C, "bold": True, "color": ORANGE})],
]
add_text(s, MX, Inches(3.15), Inches(6.3), Inches(0.25),
         [("전체 총계 (단위: 원, VAT 별도)", 10, True, NAVY)])
clean_table(s, MX, Inches(3.45), Inches(6.3), [2.0, 1.5, 1.5, 0.9], rows,
            row_h=Inches(0.4))

msgs = [
    ("기존 비용은 그대로", "EA Renewal과 SCE 서버 라이선스 전 품목이 4개사 모두 전년 금액 동결 — 단가 인상 요인 0원"),
    ("증가분 = 100% True-up", "EA 증가액 111,676,600원은 전액 사용자 244EA 순증 정산분 (인상이 아닌 사용 확대)"),
    ("최적화로 증가 상쇄", "Copilot 실사용 조정·Easy Tree 종료로 62,760,600원 절감 → 총 증가율을 +3.9%로 방어"),
]
mx2 = Inches(7.5)
add_text(s, mx2, Inches(3.15), Inches(5.1), Inches(0.25),
         [("핵심 메시지", 10, True, NAVY)])
for i, (t, d) in enumerate(msgs):
    y = Emu(int(Inches(3.5)) + i * int(Inches(1.08)))
    add_text(s, mx2, y, Inches(0.3), Inches(0.3), [("—", 12, True, ORANGE)])
    add_text(s, Emu(int(mx2) + int(Inches(0.35))), y, Inches(4.8), Inches(1.0),
             [(t, 11.5, True, NAVY), (d, 9.5, False, BODY)], space_after=3)

# ══════════════════════════════════════════════════════════════
# 4. 계약 구조 및 갱신 원칙
# ══════════════════════════════════════════════════════════════
s = new_slide()
header(s, "02  |  CONTRACT STRUCTURE",
       "동결·정산·최적화 — 세 갈래 원칙으로 총소유비용을 관리합니다", 4)

cards = [
    ("EA — M365 E3", ["전사 사용자 대상 볼륨 라이선스",
                      "Renewal(기존 인원) + True-up(연중 증가분 연 1회 정산)",
                      "금회: Renewal 4사 전액 동결"]),
    ("SCE — Server & Cloud", ["서버·개발 인프라 3년 약정 Enrollment",
                              "SQL·Windows Server Core, Visual Studio, MS Unified Support",
                              "금회: 5개 품목 × 4사 전 품목 동결"]),
    ("기타 라이선스", ["Copilot · Teams Pro · Easy Tree 등 부가 라이선스",
                       "실사용 기준으로 수량을 매년 재조정",
                       "금회: Copilot 축소, Easy Tree 종료 → -88%"]),
]
for i, (t, items) in enumerate(cards):
    x = Emu(int(MX) + i * int(Inches(4.05)))
    accent_card(s, x, Inches(1.65), Inches(3.85), Inches(2.55))
    add_text(s, Emu(int(x) + int(Inches(0.25))), Inches(1.9), Inches(3.4), Inches(0.4),
             [(t, 12.5, True, NAVY)])
    add_text(s, Emu(int(x) + int(Inches(0.25))), Inches(2.4), Inches(3.4), Inches(1.7),
             [("·  " + it, 9.5, False, BODY) for it in items], space_after=7)

add_text(s, MX, Inches(4.55), CW, Inches(0.3), [("금회 갱신 3원칙", 11, True, NAVY)])
principles = [
    ("01", "단가 전면 동결", "EA Renewal·SCE 서버 라이선스 모두 전년 계약 조건 그대로 유지"),
    ("02", "증가분만 정산", "비용 변동은 True-up(사용 인원 순증)에만 연동 — 선구매·과잉 구매 없음"),
    ("03", "실사용 최적화", "사용률이 낮은 부가 라이선스는 축소·종료해 총소유비용 절감"),
]
for i, (no, t, d) in enumerate(principles):
    x = Emu(int(MX) + i * int(Inches(4.05)))
    y = Inches(4.95)
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
       "4사 합계 +3.9% — 사용자 증가(에스티젠·에스티)와 비용 절감(쏘시오·제약)이 균형을 이룹니다", 5,
       title_size=17)
rows = [
    ["회사", "25Y", "26Y", "증감액", "증감률"],
    ["동아쏘시오홀딩스㈜", "70,779,400", "42,631,000", "-28,148,400",
     ("-39.8%", {"color": NAVY, "bold": True, "align": C})],
    ["동아에스티㈜", "650,000,000", "677,940,000", "+27,940,000",
     ("+4.3%", {"color": ORANGE, "bold": True, "align": C})],
    ["동아제약㈜", "385,707,200", "380,481,000", "-5,226,200",
     ("-1.4%", {"color": NAVY, "align": C})],
    ["에스티젠바이오㈜", "161,394,600", "215,742,600", "+54,348,000",
     ("+33.7%", {"color": ORANGE, "bold": True, "align": C})],
    ["합계", "1,267,881,200", "1,316,794,600", "+48,913,400",
     ("+3.9%", {"align": C, "bold": True, "color": ORANGE})],
]
add_text(s, MX, Inches(1.6), CW, Inches(0.25),
         [("회사별 전체계 — EA+SCE+기타, 단수 조정 반영 (단위: 원, VAT 별도)", 10, True, NAVY)])
clean_table(s, MX, Inches(1.95), CW, [2.2, 1.7, 1.7, 1.6, 1.0], rows,
            row_h=Inches(0.5), font_size=11)

add_text(s, MX, Inches(5.15), CW, Inches(1.6),
         [([("읽는 법  ", 10, True, ORANGE),
            ("증가는 사업 확장 2개사(에스티젠바이오·동아에스티)의 EA True-up에서만 발생하고, 동아쏘시오홀딩스·동아제약은 Copilot 조정과 Easy Tree 종료로 총비용이 오히려 감소합니다. ",
             10.5, False, BODY)],),
          ("SCE(서버)와 EA Renewal(기존 인원)은 4사 모두 동결로, 그룹 전체 증가율은 +3.9%에 그칩니다.",
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
     ("0%", {"align": C}), ("변동 없음", {"align": C, "size": 9})],
    ["동아에스티㈜", "494,797,800", "539,788,200", "+44,990,400",
     ("+9%", {"color": ORANGE, "bold": True, "align": C}),
     ("1,249 → 1,341", {"align": C, "size": 9})],
    ["동아제약㈜", "275,801,400", "282,973,600", "+7,172,200",
     ("+2.6%", {"align": C}), ("687 → 709", {"align": C, "size": 9})],
    ["에스티젠바이오㈜", "127,394,400", "186,908,400", "+59,514,000",
     ("+47%", {"color": ORANGE, "bold": True, "align": C}),
     ("300 → 430", {"align": C, "size": 9})],
    ["EA 합계", "934,197,600", "1,045,874,200", "+111,676,600",
     ("+12%", {"align": C, "bold": True, "color": ORANGE}),
     ("+244EA", {"align": C, "size": 9})],
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
# 8. 기타 라이선스 요약
# ══════════════════════════════════════════════════════════════
s = new_slide()
header(s, "06  |  OTHER LICENSES",
       "기타 라이선스 -88% — Copilot 실사용 조정과 Easy Tree 종료로 62.8백만 원을 절감합니다", 8,
       title_size=18)
rows = [
    ["회사", "품목", "25Y", "26Y", "증감률", "비고"],
    ["동아쏘시오홀딩스㈜", "Copilot 라이선스", "12,398,400", "0",
     ("-100%", {"color": NAVY, "align": C}), ("26Y 갱신 종료", {"size": 9, "align": C})],
    ["", "Easy Tree", "15,750,000", "0",
     ("-100%", {"color": NAVY, "align": C}), ("유지보수 종료", {"size": 9, "align": C})],
    ["동아에스티㈜", "Copilot 라이선스", "21,697,200", "4,649,400",
     ("-79%", {"color": NAVY, "align": C}), ("42 → 9 Copy 조정", {"size": 9, "align": C})],
    ["", "Teams Pro", "655,200", "655,200",
     ("0%", {"align": C}), ("갱신 유지", {"size": 9, "align": C})],
    ["동아제약㈜", "Copilot 라이선스", "15,498,000", "3,099,600",
     ("-80%", {"color": NAVY, "align": C}), ("30 → 6 Copy 조정", {"size": 9, "align": C})],
    ["에스티젠바이오㈜", "Copilot 라이선스", "5,166,000", "0",
     ("-100%", {"color": NAVY, "align": C}), ("10 → 0 Copy 조정", {"size": 9, "align": C})],
    ["기타 합계", "", "71,164,800", "8,404,200",
     ("-88%", {"align": C, "bold": True, "color": NAVY}), ""],
]
add_text(s, MX, Inches(1.6), CW, Inches(0.25),
         [("기타 라이선스 — Copilot · Teams Pro · Easy Tree (단위: 원, VAT 별도)", 10, True, NAVY)])
clean_table(s, MX, Inches(1.95), CW, [1.9, 1.6, 1.4, 1.4, 0.9, 1.5], rows,
            row_h=Inches(0.4), font_size=10)

stat_band(s, MX, Inches(5.5), CW, [
    ("연간 절감 효과", "-62,760,600원", NAVY, "25Y 71,164,800 → 26Y 8,404,200"),
    ("Copilot 운영 원칙", "실사용 기준", ORANGE, "3사 82→15 Copy 재산정, 쏘시오는 갱신 종료"),
    ("절감분의 활용", "56% 상쇄", NAVY, "True-up 증가분 대비 기타 라이선스 절감액 비중"),
], big=17, band_h=Inches(0.95))

# ══════════════════════════════════════════════════════════════
# 9~12. 회사별 상세
# ══════════════════════════════════════════════════════════════
companies = [
    dict(
        no="07", name="동아쏘시오홀딩스㈜", page=9,
        title="동아쏘시오홀딩스 -39.8% — Copilot·Easy Tree 종료로 연 28백만 원을 절감합니다",
        v26="42,631,000원", v25="25Y 70,779,400원",
        rate="-39.8%", rate_color=NAVY, badge="비용 절감", ea_qty="EA 수량 변동 없음",
        ea=[["MS EA Renewal", "34,372,800", "34,372,800", ("동결", {"align": C})],
            ["MS EA True-up", "1,831,200", "1,831,200", ("동결", {"align": C})],
            ["EA 소계", "36,204,000", "36,204,000", ("0%", {"align": C})]],
        sce_total="6,427,042",
        etc=[["Copilot 라이선스", "12,398,400", "0", ("-100%", {"align": C, "color": NAVY})],
             ["Easy Tree", "15,750,000", "0", ("-100%", {"align": C, "color": NAVY})],
             ["기타 소계", "28,148,400", "0", ("-100%", {"align": C, "color": NAVY})]],
        note="EA·SCE 전 항목 동결에 더해 Copilot 갱신 종료·Easy Tree 유지보수 종료로 연 28,148,400원이 절감됩니다. ※ 전체계는 단수 조정 반영 금액",
    ),
    dict(
        no="08", name="동아에스티㈜", page=10,
        title="동아에스티 +4.3% — True-up 92EA 증가를 Copilot 실사용 조정으로 상쇄했습니다",
        v26="677,940,000원", v25="25Y 650,000,000원",
        rate="+4.3%", rate_color=ORANGE, badge="사업 확장 반영", ea_qty="1,249EA → 1,341EA",
        ea=[["MS EA Renewal", "430,831,800", "430,831,800", ("동결", {"align": C})],
            ["MS EA True-up", "63,966,000", "108,956,400",
             ("+70%", {"color": ORANGE, "bold": True, "align": C})],
            ["EA 소계", "494,797,800", "539,788,200", ("+9%", {"color": ORANGE, "align": C})]],
        sce_total="132,852,060",
        etc=[["Copilot 라이선스", "21,697,200", "4,649,400", ("-79%", {"align": C, "color": NAVY})],
             ["Teams Pro", "655,200", "655,200", ("0%", {"align": C})],
             ["기타 소계", "22,352,400", "5,304,600", ("-76%", {"align": C, "color": NAVY})]],
        note="EA 증가액 44,990,400원(True-up 92EA)을 Copilot 조정 -17,047,800원(42→9 Copy)으로 상쇄해 총 증가율을 +4.3%로 낮췄습니다. ※ 전체계는 단수 조정(-4,860원) 반영 금액",
    ),
    dict(
        no="09", name="동아제약㈜", page=11,
        title="동아제약 -1.4% — EA 증가에도 Copilot 최적화로 총비용이 감소합니다",
        v26="380,481,000원", v25="25Y 385,707,200원",
        rate="-1.4%", rate_color=NAVY, badge="총비용 감소", ea_qty="687EA → 709EA",
        ea=[["MS EA Renewal", "224,985,600", "224,985,600", ("동결", {"align": C})],
            ["MS EA True-up", "50,815,800", "57,988,000",
             ("+14%", {"color": ORANGE, "bold": True, "align": C})],
            ["EA 소계", "275,801,400", "282,973,600", ("+2.6%", {"color": ORANGE, "align": C})]],
        sce_total="94,407,800",
        etc=[["Copilot 라이선스", "15,498,000", "3,099,600", ("-80%", {"align": C, "color": NAVY})],
             ["기타 소계", "15,498,000", "3,099,600", ("-80%", {"align": C, "color": NAVY})]],
        note="EA 증가액 7,172,200원(True-up 22EA)보다 Copilot 조정 절감액 -12,398,400원(30→6 Copy)이 커서, 총비용은 전년보다 5,226,200원 감소합니다.",
    ),
    dict(
        no="10", name="에스티젠바이오㈜", page=12,
        title="에스티젠바이오 +33.7% — 증가분은 전액 True-up 130EA(사용자 순증)에서 발생했습니다",
        v26="215,742,600원", v25="25Y 161,394,600원",
        rate="+33.7%", rate_color=ORANGE, badge="사업 확장 대폭 반영", ea_qty="300EA → 430EA",
        ea=[["MS EA Renewal", "57,808,800", "57,808,800", ("동결", {"align": C})],
            ["MS EA True-up", "69,585,600", "129,099,600",
             ("+86%", {"color": ORANGE, "bold": True, "align": C})],
            ["EA 소계", "127,394,400", "186,908,400", ("+47%", {"color": ORANGE, "align": C})]],
        sce_total="28,834,200",
        etc=[["Copilot 라이선스", "5,166,000", "0", ("-100%", {"align": C, "color": NAVY})],
             ["기타 소계", "5,166,000", "0", ("-100%", {"align": C, "color": NAVY})]],
        note="증가액 59,514,000원은 전액 True-up 130EA의 정산분으로 바이오 사업 확장에 따른 인력 확충을 반영하며, Copilot 종료(-5,166,000원)로 부가 비용은 정리했습니다.",
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
COLS = [2.2, 1.5, 1.5, 0.9]

for co in companies:
    s = new_slide()
    header(s, f"{co['no']}  |  COMPANY DETAIL — {co['name']}", co["title"], co["page"],
           title_size=17)

    # 좌측 요약 카드
    accent_card(s, MX, Inches(1.55), Inches(3.1), Inches(5.3))
    cx = Emu(int(MX) + int(Inches(0.3)))
    add_text(s, cx, Inches(1.82), Inches(2.6), Inches(3.1),
             [("26Y 전체계 (VAT 별도)", 9.5, False, CAP),
              (co["v26"], 19, True, NAVY),
              (co["v25"], 9, False, CAP),
              ("", 5),
              ("전년 대비 증감", 9.5, False, CAP),
              (co["rate"], 28, True, co["rate_color"]),
              (co["badge"], 11, True, co["rate_color"]),
              ("", 5),
              ("EA 수량", 9.5, False, CAP),
              (co["ea_qty"], 11.5, True, NAVY)], space_after=4)
    add_text(s, cx, Inches(5.25), Inches(2.55), Inches(1.5),
             [(co["note"], 8.5, False, BODY)], space_after=3)

    # 우측: EA 표
    tx = Inches(4.1)
    tw = Inches(8.53)
    add_text(s, tx, Inches(1.5), tw, Inches(0.22),
             [("EA 라이선스 (M365 E3)  —  단위: 원, VAT 별도", 9.5, True, NAVY)])
    clean_table(s, tx, Inches(1.76), tw, COLS,
                [["품목", "25Y", "26Y", "증감"]] + co["ea"],
                row_h=Inches(0.31), font_size=9.5)

    # 우측: SCE 표
    add_text(s, tx, Inches(3.08), tw, Inches(0.22),
             [("SCE 라이선스  —  전 품목 동결 (25Y = 26Y)", 9.5, True, NAVY)])
    vals = SCE_DATA[co["name"]]
    sce_rows = ([["품목", "25Y", "26Y", "증감"]]
                + [[SCE_ITEMS[i], vals[i], vals[i], ("0%", {"align": C})]
                   for i in range(5)]
                + [["SCE 소계", co["sce_total"], co["sce_total"], ("0%", {"align": C})]])
    clean_table(s, tx, Inches(3.34), tw, COLS, sce_rows,
                row_h=Inches(0.29), font_size=9)

    # 우측: 기타 표
    add_text(s, tx, Inches(5.5), tw, Inches(0.22),
             [("기타 라이선스", 9.5, True, NAVY)])
    clean_table(s, tx, Inches(5.76), tw, COLS,
                [["품목", "25Y", "26Y", "증감"]] + co["etc"],
                row_h=Inches(0.29), font_size=9)

# ══════════════════════════════════════════════════════════════
# 13. 증감 요인 분석
# ══════════════════════════════════════════════════════════════
s = new_slide()
header(s, "11  |  GROWTH ANALYSIS",
       "순증 +48.9백만 원 = True-up +111.7 − 최적화 절감 62.8 — 단가 인상은 없습니다", 13,
       title_size=18)
rows = [
    ["구분", "25Y", "26Y", "증감액", "성격"],
    ["EA Renewal 합계 (4사)", "747,999,000", "747,999,000",
     ("동결", {"align": C}), ("변동 없음", {"align": C, "size": 9})],
    ["EA True-up 합계 (4사)", "186,198,600", "297,875,200",
     ("+111,676,600", {"color": ORANGE, "bold": True}),
     ("사용자 +244EA", {"align": C, "size": 9})],
    ["SCE 합계 (4사)", "262,521,102", "262,521,102",
     ("동결", {"align": C}), ("변동 없음", {"align": C, "size": 9})],
    ["기타 라이선스 합계 (4사)", "71,164,800", "8,404,200",
     ("-62,760,600", {"color": NAVY, "bold": True}),
     ("실사용 최적화", {"align": C, "size": 9})],
    ["단수 조정", "-2,302", "-4,902", ("-2,600", {"align": PP_ALIGN.RIGHT}),
     ("—", {"align": C, "size": 9})],
    ["총계", "1,267,881,200", "1,316,794,600", "+48,913,400",
     ("+3.9%", {"align": C, "bold": True, "color": ORANGE})],
]
add_text(s, MX, Inches(1.6), CW, Inches(0.25),
         [("증가 요인 분해 (단위: 원, VAT 별도)", 10, True, NAVY)])
clean_table(s, MX, Inches(1.9), CW, [2.3, 1.7, 1.7, 1.7, 1.1], rows,
            row_h=Inches(0.42), font_size=10)

add_text(s, MX, Inches(4.85), CW, Inches(0.28),
         [("증감 구성 요소", 11, True, NAVY)])
tu = [("True-up 순증", "+111,676,600", "에스티젠 130 · 에스티 92 · 제약 22 (+244EA)", ORANGE),
      ("Copilot 조정", "-47,010,600", "3사 82→15 Copy 재산정 + 쏘시오 갱신 종료", NAVY),
      ("Easy Tree 종료", "-15,750,000", "유지보수 계약 종료 (쏘시오홀딩스)", NAVY),
      ("순 증감", "+48,913,400", "전년 대비 +3.9%", ORANGE)]
cw4 = int(CW) // 4
for i, (nm, n, d, c) in enumerate(tu):
    x = Emu(int(MX) + cw4 * i + (0 if i == 0 else int(Inches(0.3))))
    add_text(s, x, Inches(5.25), Emu(cw4 - int(Inches(0.35))), Inches(1.5),
             [(nm, 10, True, NAVY), (n, 19, True, c), (d, 8.5, False, CAP)],
             space_after=4)
    if i > 0:
        vline(s, Emu(int(MX) + cw4 * i), Inches(5.3), Inches(1.25), 0.75, HAIR)

# ══════════════════════════════════════════════════════════════
# 14. 계약 조건 및 향후 일정
# ══════════════════════════════════════════════════════════════
s = new_slide()
header(s, "12  |  TERMS & NEXT STEPS", "계약 조건 요약 및 진행 일정", 14, title_size=20)
rows = [
    ["항목", ("내용", {"align": L})],
    ["계약기간", ("2024. 03. 31 ~ 2027. 04. 01  (3년 차 갱신)", {"align": L})],
    ["계약 구성", ("EA(M365 E3) + SCE(서버) + 기타 라이선스", {"align": L})],
    ["단가 조건", ("EA Renewal·SCE 전 품목 전년 동결", {"align": L})],
    ["부가세", ("별도 (VAT 미포함 금액 기준)", {"align": L})],
    ["26Y 계약 총액", ("1,316,794,600원 (4사 합계, 단수 조정 반영)",
                       {"align": L, "bold": True, "color": NAVY})],
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
    ("STEP 3", "3년 차(26Y) 갱신 물량 확정"),
    ("STEP 4", "확정분 반영 및 연중 True-up 관리 지원"),
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
            ("계약 기간 중 라이선스 컴플라이언스 점검, True-up 수량 관리, Copilot 등 부가 라이선스의 실사용 모니터링, SecureON MS Unified Support 기반 기술 지원 및 전담 담당자를 통한 구매 문의 대응을 제공합니다.",
             10.5, False, BODY)],)])

# ══════════════════════════════════════════════════════════════
# 15. 맺음말
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
            ("기존 비용은 동결로 지키고, 쓰지 않는 것은 덜어내고, 성장에 필요한 만큼만 더하는 갱신을 제안드립니다.", 13, True, NAVY)],),
          ([("—  ", 12, True, ORANGE),
            ("동아그룹 4개사의 안정적인 Microsoft 업무·서버 환경과 사업 확장을 계속 지원하겠습니다.", 12, False, BODY)],),
          ([("—  ", 12, True, ORANGE),
            ("제안서 검토 후 수량 확정을 요청드리며, 2026년 3월 31일 계약 발효를 목표로 진행하겠습니다.", 12, False, BODY)],)],
         space_after=12)
add_text(s, MX, Inches(5.6), Inches(9.8), Inches(0.5),
         [("본 제안서의 금액은 부가세 별도 기준이며, 최종 수량 확정 시 일부 조정될 수 있습니다.",
           9, False, CAP)])
add_rect(s, 0, Inches(7.34), SW, Inches(0.16), ORANGE)

out = "동아그룹_Microsoft_라이선스_갱신제안서_2026.pptx"
prs.save(out)
print(f"saved: {out}, slides: {len(prs.slides._sldIdLst)}")
