"""
2025년 대비 2026년 그룹사 IT 용역 계약 변경사항 분석 PPT 생성 스크립트
- 데이터 출처: 그룹사 계약 data (A3:U1108), 요약 수치는 사용자 제공 분석 결과 기반
- 실행: python3 generate_ppt.py  ->  IT용역계약_2026_분석보고.pptx 생성
"""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION, XL_LABEL_POSITION
from pptx.oxml.ns import qn
import copy

# ---------------------------------------------------------------------------
# 색상 팔레트
# ---------------------------------------------------------------------------
BLUE = RGBColor(0x00, 0x78, 0xD4)
BLUE_DARK = RGBColor(0x00, 0x4C, 0x8C)
GREEN = RGBColor(0x10, 0x7C, 0x10)
RED = RGBColor(0xD8, 0x3B, 0x01)
ORANGE = RGBColor(0xFF, 0x8C, 0x00)
YELLOW = RGBColor(0xFF, 0xB9, 0x00)
PURPLE = RGBColor(0x87, 0x64, 0xB8)
DARK = RGBColor(0x25, 0x25, 0x26)
GRAY = RGBColor(0x66, 0x66, 0x66)
LIGHT_GRAY = RGBColor(0xF3, 0xF2, 0xF1)
MID_GRAY = RGBColor(0xD9, 0xD9, 0xD9)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

FONT = "맑은 고딕"
SW, SH = Inches(13.333), Inches(7.5)

SEV_COLOR = {"high": RED, "mid": ORANGE, "low": YELLOW}
SEV_LABEL = {"high": "🔴 높음", "mid": "🟠 중간", "low": "🟡 낮음"}

prs = Presentation()
prs.slide_width = SW
prs.slide_height = SH
BLANK = prs.slide_layouts[6]


# ---------------------------------------------------------------------------
# 공통 헬퍼
# ---------------------------------------------------------------------------
def new_slide():
    return prs.slides.add_slide(BLANK)


def set_bg(slide, color=WHITE):
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = color


def add_rect(slide, x, y, w, h, color, line_color=None, line_w=None, shadow=False):
    shp = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, h)
    shp.fill.solid()
    shp.fill.fore_color.rgb = color
    if line_color is None:
        shp.line.fill.background()
    else:
        shp.line.color.rgb = line_color
        shp.line.width = line_w or Pt(0.75)
    shp.shadow.inherit = False
    return shp


def add_round_rect(slide, x, y, w, h, color, radius=0.08):
    shp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h)
    try:
        shp.adjustments[0] = radius
    except Exception:
        pass
    shp.fill.solid()
    shp.fill.fore_color.rgb = color
    shp.line.fill.background()
    shp.shadow.inherit = False
    return shp


def add_text(slide, x, y, w, h, text, size=14, bold=False, color=DARK,
             align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, font=FONT,
             line_spacing=1.0, italic=False, wrap=True):
    box = slide.shapes.add_textbox(x, y, w, h)
    tf = box.text_frame
    tf.word_wrap = wrap
    tf.vertical_anchor = anchor
    tf.margin_left = 0
    tf.margin_right = 0
    tf.margin_top = 0
    tf.margin_bottom = 0
    lines = text.split("\n")
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = line_spacing
        r = p.add_run()
        r.text = line
        r.font.size = Pt(size)
        r.font.bold = bold
        r.font.italic = italic
        r.font.name = font
        r.font.color.rgb = color
    return box


def add_header(slide, section, title, accent=BLUE):
    set_bg(slide, WHITE)
    add_rect(slide, 0, 0, SW, Inches(0.08), accent)
    add_text(slide, Inches(0.55), Inches(0.28), Inches(10), Inches(0.35),
              section, size=13, bold=True, color=accent)
    add_text(slide, Inches(0.55), Inches(0.62), Inches(12.2), Inches(0.7),
              title, size=26, bold=True, color=DARK)
    add_rect(slide, Inches(0.55), Inches(1.32), Inches(1.1), Pt(3), accent)


def add_footer(slide, num):
    add_text(slide, Inches(12.4), Inches(7.15), Inches(0.7), Inches(0.3),
              str(num), size=10, color=GRAY, align=PP_ALIGN.RIGHT)


def add_table(slide, x, y, w, h, rows, col_widths=None, header=True,
              header_bg=BLUE, header_color=WHITE, font_size=12,
              body_bg=WHITE, alt_bg=LIGHT_GRAY, align_cols=None,
              highlight_rows=None, row_colors=None):
    nrows, ncols = len(rows), len(rows[0])
    gshape = slide.shapes.add_table(nrows, ncols, x, y, w, h)
    tbl = gshape.table
    # remove default banding style visuals via manual coloring
    if col_widths:
        for i, cw in enumerate(col_widths):
            tbl.columns[i].width = cw
    highlight_rows = highlight_rows or {}
    for r in range(nrows):
        row_h = h // nrows
        tbl.rows[r].height = row_h
        for c in range(ncols):
            cell = tbl.cell(r, c)
            cell.margin_left = Pt(6)
            cell.margin_right = Pt(6)
            cell.margin_top = Pt(2)
            cell.margin_bottom = Pt(2)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            tf = cell.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.alignment = (align_cols[c] if align_cols else
                            (PP_ALIGN.LEFT if c == 0 else PP_ALIGN.CENTER))
            run = p.add_run() if not p.runs else p.runs[0]
            run.text = str(rows[r][c])
            run.font.size = Pt(font_size if r > 0 or not header else font_size)
            run.font.name = FONT
            if header and r == 0:
                cell.fill.solid()
                cell.fill.fore_color.rgb = header_bg
                run.font.color.rgb = header_color
                run.font.bold = True
            else:
                if r in highlight_rows:
                    cell.fill.solid()
                    cell.fill.fore_color.rgb = highlight_rows[r]
                    run.font.color.rgb = DARK
                    run.font.bold = True
                else:
                    cell.fill.solid()
                    cell.fill.fore_color.rgb = (alt_bg if r % 2 == 0 else body_bg)
                    run.font.color.rgb = DARK
                if row_colors and r in row_colors:
                    run.font.color.rgb = row_colors[r]
                    run.font.bold = True
    return gshape


def style_chart_fonts(chart, size=11, color=DARK):
    try:
        chart.font.size = Pt(size)
        chart.font.name = FONT
        chart.font.color.rgb = color
    except Exception:
        pass


def add_clustered_bar(slide, x, y, cx, cy, categories, series_dict, colors,
                       number_format='0.0"억"', title=None, data_labels=True,
                       horizontal=False):
    data = CategoryChartData()
    data.categories = categories
    for name, vals in series_dict.items():
        data.add_series(name, vals)
    ctype = XL_CHART_TYPE.BAR_CLUSTERED if horizontal else XL_CHART_TYPE.COLUMN_CLUSTERED
    gframe = slide.shapes.add_chart(ctype, x, y, cx, cy, data)
    chart = gframe.chart
    chart.has_legend = len(series_dict) > 1
    if chart.has_legend:
        chart.legend.position = XL_LEGEND_POSITION.BOTTOM
        chart.legend.include_in_layout = False
        chart.legend.font.size = Pt(11)
        chart.legend.font.name = FONT
    chart.has_title = bool(title)
    if title:
        chart.chart_title.text_frame.text = title
        chart.chart_title.text_frame.paragraphs[0].runs[0].font.size = Pt(13)
        chart.chart_title.text_frame.paragraphs[0].runs[0].font.bold = True
    plot = chart.plots[0]
    plot.has_data_labels = data_labels
    if data_labels:
        dl = plot.data_labels
        dl.number_format = number_format
        dl.number_format_is_linked = False
        dl.font.size = Pt(10)
        dl.font.name = FONT
        if horizontal:
            dl.position = XL_LABEL_POSITION.OUTSIDE_END
    for i, series in enumerate(plot.series):
        series.format.fill.solid()
        series.format.fill.fore_color.rgb = colors[i % len(colors)]
    cat_ax = chart.category_axis
    cat_ax.tick_labels.font.size = Pt(11)
    cat_ax.tick_labels.font.name = FONT
    val_ax = chart.value_axis
    val_ax.tick_labels.font.size = Pt(10)
    val_ax.has_major_gridlines = False
    return chart


def add_pie(slide, x, y, cx, cy, categories, values, colors, hole=55, title=None):
    data = CategoryChartData()
    data.categories = categories
    data.add_series("비용", values)
    gframe = slide.shapes.add_chart(XL_CHART_TYPE.DOUGHNUT, x, y, cx, cy, data)
    chart = gframe.chart
    chart.has_legend = True
    chart.legend.position = XL_LEGEND_POSITION.BOTTOM
    chart.legend.include_in_layout = False
    chart.legend.font.size = Pt(12)
    chart.legend.font.name = FONT
    chart.has_title = bool(title)
    if title:
        chart.chart_title.text_frame.text = title
    plot = chart.plots[0]
    plot.has_data_labels = True
    dl = plot.data_labels
    dl.number_format = '0.0"억"'
    dl.number_format_is_linked = False
    dl.font.size = Pt(13)
    dl.font.bold = True
    dl.font.name = FONT
    dl.font.color.rgb = WHITE
    series = plot.series
    points = series[0].points
    for i, pt in enumerate(points):
        pt.format.fill.solid()
        pt.format.fill.fore_color.rgb = colors[i % len(colors)]
    try:
        chart.plots[0].vary_by_categories = True
        donutHoleSize = chart._chartSpace.xpath('.//c:doughnutChart/c:holeSize')
        if donutHoleSize:
            donutHoleSize[0].set('val', str(hole))
    except Exception:
        pass
    return chart


def kpi_card(slide, x, y, w, h, label, value, delta, color):
    add_round_rect(slide, x, y, w, h, LIGHT_GRAY)
    add_rect(slide, x, y, Inches(0.07), h, color)
    add_text(slide, x + Inches(0.25), y + Inches(0.15), w - Inches(0.4), Inches(0.35),
              label, size=13, bold=True, color=GRAY)
    add_text(slide, x + Inches(0.25), y + Inches(0.5), w - Inches(0.4), Inches(0.55),
              value, size=28, bold=True, color=DARK)
    add_text(slide, x + Inches(0.25), y + h - Inches(0.5), w - Inches(0.4), Inches(0.4),
              delta, size=14, bold=True, color=color)


# ===========================================================================
# SECTION 1. 개요
# ===========================================================================

# --- 슬라이드 1: 표지 ---
s = new_slide()
set_bg(s, BLUE_DARK)
add_rect(s, 0, 0, SW, Inches(0.18), ORANGE)
add_text(s, Inches(1), Inches(2.4), Inches(11.3), Inches(0.5),
          "그룹사 IT 용역 계약 변경사항 분석", size=20, bold=True, color=RGBColor(0xBF, 0xE0, 0xFF))
add_text(s, Inches(1), Inches(2.9), Inches(11.3), Inches(1.3),
          "2025 → 2026 계약 구조 분석 및\n문제점 진단·개선 방법론", size=36, bold=True, color=WHITE)
add_text(s, Inches(1), Inches(4.35), Inches(11.3), Inches(0.5),
          "계약 데이터 기반 정량 분석  ·  구조적 문제점 8건 진단  ·  3-Phase 정상화 로드맵",
          size=15, color=RGBColor(0xD8, 0xE8, 0xF7))
add_rect(s, Inches(1), Inches(5.0), Inches(2.2), Pt(2), ORANGE)
add_text(s, Inches(1), Inches(6.6), Inches(6), Inches(0.4),
          "경영진 보고용  |  2026", size=13, color=RGBColor(0xB0, 0xC7, 0xDE))

# --- 슬라이드 2: Executive Summary ---
s = new_slide()
add_header(s, "SECTION 1 · 개요", "Executive Summary")
msgs = [
    ("01", "예산 증가는 전략적 투자",
     "총 계약 비용 83.3억 → 100.1억(+20.2%)으로 증가했으나, 증가분의 대부분은 정보보안·인프라 강화를 위한 신규 도입(+20.4억)에서 발생", BLUE),
    ("02", "계약 구조에 8가지 핵심 문제점 발견",
     "고부하 배정, TBD 미배정(148건), 소규모 배분(574건) 등 구조적 리스크 존재. 특히 등급별 단가 편차(최대 525%)가 가장 심각", RED),
    ("03", "3개월 정상화 로드맵으로 즉시 개선 착수",
     "Phase 1~3 단계적 실행을 통해 TBD 해소, 고부하 재배분, 단가 표준화를 완료하고 계약 효율성 30% 향상 목표", GREEN),
]
y = Inches(1.7)
for num, title, body, color in msgs:
    add_round_rect(s, Inches(0.55), y, Inches(12.25), Inches(1.55), LIGHT_GRAY)
    add_rect(s, Inches(0.55), y, Inches(0.09), Inches(1.55), color)
    add_text(s, Inches(0.95), y + Inches(0.15), Inches(1.0), Inches(1.0), num, size=34, bold=True, color=color)
    add_text(s, Inches(2.0), y + Inches(0.18), Inches(10.6), Inches(0.5), title, size=18, bold=True, color=DARK)
    add_text(s, Inches(2.0), y + Inches(0.68), Inches(10.6), Inches(0.75), body, size=13, color=GRAY, line_spacing=1.15)
    y += Inches(1.75)
add_footer(s, 2)

# --- 슬라이드 3: 목차 ---
s = new_slide()
add_header(s, "SECTION 1 · 개요", "목차 (Contents)")
toc = [
    ("01", "현황 분석", "2025→2026 계약 데이터 정량 분석", BLUE, "4 – 11"),
    ("02", "문제점 분석", "계약 구조 8대 문제점 진단", RED, "12 – 21"),
    ("03", "개선 방법론", "Framework · 표준 단가 · 로드맵", GREEN, "22 – 27"),
    ("04", "부록", "Top 10 · 용어 · 데이터 출처", GRAY, "28 – 30"),
]
y = Inches(1.85)
for num, title, desc, color, pages in toc:
    add_rect(s, Inches(0.55), y, Inches(0.09), Inches(1.15), color)
    add_text(s, Inches(0.9), y + Inches(0.05), Inches(1.0), Inches(0.8), num, size=30, bold=True, color=color)
    add_text(s, Inches(2.0), y + Inches(0.08), Inches(8.5), Inches(0.45), title, size=19, bold=True, color=DARK)
    add_text(s, Inches(2.0), y + Inches(0.58), Inches(8.5), Inches(0.4), desc, size=13, color=GRAY)
    add_text(s, Inches(11.0), y + Inches(0.3), Inches(1.7), Inches(0.5), pages, size=14, bold=True, color=color, align=PP_ALIGN.RIGHT)
    y += Inches(1.32)
add_footer(s, 3)

print("Section 1 (slides 1-3) built.")

# ===========================================================================
# SECTION 2. 현황 분석
# ===========================================================================
SEC2 = "SECTION 2 · 현황 분석"

# --- 슬라이드 4: 전체 요약 - 숫자로 보는 변화 ---
s = new_slide()
add_header(s, SEC2, "전체 요약 – 숫자로 보는 변화")
cards = [
    ("총 공수 (MM)", "68.93 MM", "▲ +13.30 MM (+23.9%)", BLUE),
    ("총 연간 비용", "100.1억", "▲ +16.8억 (+20.2%)", RED),
    ("공수 배정 건수", "916건", "▲ +365건 (+66.2%)", ORANGE),
]
x = Inches(0.55)
for label, value, delta, color in cards:
    kpi_card(s, x, Inches(1.75), Inches(3.95), Inches(1.8), label, value, delta, color)
    x += Inches(4.15)
add_text(s, Inches(0.55), Inches(3.85), Inches(12.2), Inches(0.35),
          "2025년 vs 2026년 비교", size=15, bold=True, color=DARK)
rows = [
    ["구분", "2025년", "2026년", "증감", "증감률"],
    ["총 공수 (MM)", "55.63", "68.93", "+13.30", "+23.9%"],
    ["총 연간 비용", "83.3억", "100.1억", "+16.8억", "+20.2%"],
    ["공수 배정 건수", "551건", "916건", "+365건", "+66.2%"],
]
add_table(s, Inches(0.55), Inches(4.3), Inches(12.2), Inches(2.1), rows,
          col_widths=[Inches(3.4), Inches(2.2), Inches(2.2), Inches(2.2), Inches(2.2)])
add_footer(s, 4)

# --- 슬라이드 5: 비용 구조 변화 (Waterfall) ---
s = new_slide()
add_header(s, SEC2, "비용 구조 변화 – Waterfall 분석")
add_text(s, Inches(0.55), Inches(1.45), Inches(12.2), Inches(0.4),
          "2025년 83.3억 → 2026년 100.1억 (+16.8억, +20.2%) : 증가분의 121%가 신규 도입에서 발생",
          size=13, bold=True, color=GRAY)

wf_steps = [
    ("2025년\n총 비용", 83.3, 0, "base", BLUE),
    ("기존 계약\n변동", -3.6, 83.3, "down", RED),
    ("신규 도입\n증가", 20.4, 79.7, "up", PURPLE),
    ("2026년\n총 비용", 100.1, 0, "base", BLUE),
]
chart_x0, chart_y0 = Inches(1.1), Inches(2.3)
chart_w, chart_h = Inches(11.0), Inches(4.2)
max_val = 105.0
scale = chart_h / max_val
bar_w = Inches(2.1)
gap = (chart_w - bar_w * 4) / 3

# axis baseline
add_rect(s, chart_x0, chart_y0 + chart_h, chart_w, Pt(1.5), MID_GRAY)

cx = chart_x0
for label, val, base, kind, color in wf_steps:
    if kind == "base":
        h = Emu(int(val * scale))
        y = chart_y0 + chart_h - h
        add_rect(s, cx, y, bar_w, h, color)
        add_text(s, cx, y - Inches(0.42), bar_w, Inches(0.4), f"{val:.1f}억", size=15, bold=True, color=color, align=PP_ALIGN.CENTER)
    else:
        top_val = base + val if val > 0 else base
        bot_val = base if val > 0 else base + val
        h = Emu(int(abs(val) * scale))
        y = chart_y0 + chart_h - Emu(int(top_val * scale))
        add_rect(s, cx, y, bar_w, h, color)
        sign = "+" if val > 0 else ""
        add_text(s, cx, y - Inches(0.42), bar_w, Inches(0.4), f"{sign}{val:.1f}억", size=15, bold=True, color=color, align=PP_ALIGN.CENTER)
        # connector line from previous bar top
    add_text(s, cx, chart_y0 + chart_h + Inches(0.12), bar_w, Inches(0.6), label, size=12, bold=True, color=DARK, align=PP_ALIGN.CENTER)
    cx += bar_w + gap

add_footer(s, 5)

# --- 슬라이드 6: 회사별 분석 (비교) ---
s = new_slide()
add_header(s, SEC2, "회사별 분석 – 2025 vs 2026 비용 비교")
companies = ["ST", "YM", "PH", "STP", "OT", "STG", "HD", "에코팩", "기타4개사"]
c25 = [23.0, 16.2, 14.7, 8.8, 7.6, 4.8, 4.5, 1.9, 1.9]
c26 = [28.2, 17.9, 17.3, 10.0, 9.7, 7.6, 5.7, 1.5, 2.3]
add_clustered_bar(s, Inches(0.55), Inches(1.55), Inches(12.2), Inches(5.4),
                   companies, {"2025년": c25, "2026년": c26}, [BLUE, RGBColor(0x50, 0xB0, 0xF0)])
add_footer(s, 6)

# --- 슬라이드 7: 회사별 분석 - 증감 인사이트 ---
s = new_slide()
add_header(s, SEC2, "회사별 분석 – 비용 증감 Top")
rows7 = [
    ["회사", "25년 비용", "26년 비용", "비용 증감"],
    ["ST", "23.0억", "28.2억", "+5.1억"],
    ["STG", "4.8억", "7.6억", "+2.7억"],
    ["PH", "14.7억", "17.3억", "+2.6억"],
    ["OT", "7.6억", "9.7억", "+2.2억"],
    ["YM", "16.2억", "17.9억", "+1.8억"],
    ["STP", "8.8억", "10.0억", "+1.2억"],
    ["HD", "4.5억", "5.7억", "+1.2억"],
    ["기타4개사", "1.9억", "2.3억", "+0.4억"],
    ["에코팩", "1.9억", "1.5억", "-0.4억"],
]
add_table(s, Inches(0.55), Inches(1.6), Inches(7.2), Inches(5.1), rows7,
          col_widths=[Inches(1.9), Inches(1.75), Inches(1.75), Inches(1.8)],
          row_colors={1: RED, 9: GREEN})
add_round_rect(s, Inches(8.1), Inches(1.6), Inches(4.65), Inches(5.1), LIGHT_GRAY)
add_text(s, Inches(8.4), Inches(1.85), Inches(4.1), Inches(0.4), "💡 Insight", size=15, bold=True, color=BLUE)
add_text(s, Inches(8.4), Inches(2.35), Inches(4.1), Inches(4.1),
          "• ST社가 +5.1억으로 최대 증가, 전체 증가분의 30% 차지\n\n"
          "• STG社(+2.7억)는 IT운영지원 계약 신설 영향\n\n"
          "• 에코팩만 유일하게 비용 감소(-0.4억)\n\n"
          "• 상위 3개사(ST·YM·PH) 비중이 전체의 63% 로 편중",
          size=13, color=DARK, line_spacing=1.3)
add_footer(s, 7)

# --- 슬라이드 8: 팀별 분석 (비교) ---
s = new_slide()
add_header(s, SEC2, "팀별 분석 – 2025 vs 2026 비용 비교")
teams = ["ERP팀", "아키텍쳐\n인프라팀", "물류IT팀", "GXPIT팀", "데이터엑설런스팀",
         "정보보안팀", "GXP서비스\n파트", "AI워크\n플레이스팀", "헬프데스크", "경영기획팀", "AX개발팀"]
t25 = [25.0, 15.3, 12.2, 8.2, 7.5, 0.0, 3.2, 4.1, 4.6, 3.2, 0.0]
t26 = [25.5, 23.1, 10.9, 8.2, 7.4, 6.6, 5.3, 5.1, 4.3, 3.2, 0.4]
add_clustered_bar(s, Inches(0.4), Inches(1.55), Inches(12.5), Inches(5.4),
                   teams, {"2025년": t25, "2026년": t26}, [GREEN, RGBColor(0x6C, 0xC2, 0x4A)])
add_footer(s, 8)

# --- 슬라이드 9: 팀별 분석 - 인사이트 ---
s = new_slide()
add_header(s, SEC2, "팀별 분석 – 신설 조직 및 주요 증감")
rows9 = [
    ["팀", "25년 비용", "26년 비용", "비용 증감"],
    ["아키텍쳐인프라팀", "15.3억", "23.1억", "+7.8억"],
    ["정보보안팀 (신설)", "0.0억", "6.6억", "+6.6억"],
    ["GXP서비스파트", "3.2억", "5.3억", "+2.1억"],
    ["AI워크플레이스팀", "4.1억", "5.1억", "+1.0억"],
    ["ERP팀", "25.0억", "25.5억", "+0.6억"],
    ["AX개발팀 (신설)", "0.0억", "0.4억", "+0.4억"],
    ["물류 IT팀", "12.2억", "10.9억", "-1.4억"],
]
add_table(s, Inches(0.55), Inches(1.6), Inches(7.4), Inches(4.4), rows9,
          col_widths=[Inches(2.4), Inches(1.65), Inches(1.65), Inches(1.7)],
          row_colors={1: RED, 2: PURPLE, 7: BLUE})
add_round_rect(s, Inches(8.25), Inches(1.6), Inches(4.5), Inches(4.4), LIGHT_GRAY)
add_text(s, Inches(8.55), Inches(1.85), Inches(4.0), Inches(0.4), "💡 Insight", size=15, bold=True, color=GREEN)
add_text(s, Inches(8.55), Inches(2.35), Inches(4.0), Inches(3.6),
          "• 아키텍쳐인프라팀이 +7.8억으로 전체 팀 중 최대 증가\n\n"
          "• 정보보안팀·AX개발팀은 2026년 신설 → 신규 투자 영역\n\n"
          "• 물류 IT팀만 비용 감소(-1.4억), 업무 효율화 추정",
          size=13, color=DARK, line_spacing=1.3)
add_footer(s, 9)

# --- 슬라이드 10: 도입구분별 분석 (핵심) ---
s = new_slide()
add_header(s, SEC2, "도입구분별 분석 – 기존 vs 신규 (핵심)", accent=PURPLE)
rows10 = [
    ["도입구분", "25년 비용", "26년 비용", "비용 증감"],
    ["기존", "82.3억", "78.7억", "-3.6억"],
    ["신규", "1.0억", "21.4억", "+20.4억"],
]
add_table(s, Inches(0.55), Inches(1.6), Inches(6.3), Inches(1.7), rows10,
          col_widths=[Inches(1.7), Inches(1.55), Inches(1.55), Inches(1.5)],
          row_colors={1: RED, 2: PURPLE})
add_pie(s, Inches(7.1), Inches(1.5), Inches(5.7), Inches(4.3),
        ["기존", "신규"], [78.7, 21.4], [BLUE, PURPLE], title="2026년 비용 비중")
add_round_rect(s, Inches(0.55), Inches(3.55), Inches(6.3), Inches(2.2), RGBColor(0xF3, 0xEC, 0xFA))
add_text(s, Inches(0.85), Inches(3.75), Inches(5.7), Inches(0.4), "🚨 핵심 발견", size=15, bold=True, color=PURPLE)
add_text(s, Inches(0.85), Inches(4.2), Inches(5.7), Inches(1.4),
          "신규 도입 항목이 전체 증가분(+16.8억)의\n121%를 차지 → 예산 증가의 실질적 원인은\n신규 투자(주로 보안·인프라)이며, 기존 계약은\n오히려 3.6억 절감됨",
          size=14, color=DARK, line_spacing=1.3)
add_footer(s, 10)

# --- 슬라이드 11: 등급별 인력 구성 ---
s = new_slide()
add_header(s, SEC2, "등급별 인력 구성 – 고급/중급/초급")
grades = ["고급", "중급", "초급"]
mm25 = [16.02, 22.33, 16.57]
mm26 = [19.06, 27.81, 22.06]
cost25 = [24.9, 32.8, 24.5]
cost26 = [30.8, 39.9, 29.4]
add_text(s, Inches(0.55), Inches(1.45), Inches(5.8), Inches(0.35), "공수 (MM)", size=14, bold=True, color=DARK)
add_clustered_bar(s, Inches(0.4), Inches(1.85), Inches(6.0), Inches(4.9),
                   grades, {"2025 MM": mm25, "2026 MM": mm26}, [BLUE, RGBColor(0x50, 0xB0, 0xF0)],
                   number_format='0.00')
add_text(s, Inches(6.9), Inches(1.45), Inches(5.8), Inches(0.35), "비용 (억원)", size=14, bold=True, color=DARK)
add_clustered_bar(s, Inches(6.75), Inches(1.85), Inches(6.0), Inches(4.9),
                   grades, {"2025 비용": cost25, "2026 비용": cost26}, [ORANGE, YELLOW])
add_footer(s, 11)

print("Section 2 (slides 4-11) built.")

# ===========================================================================
# SECTION 3. 문제점 분석
# ===========================================================================
SEC3 = "SECTION 3 · 문제점 분석"


def problem_badge(slide, x, y, num, sev):
    color = SEV_COLOR[sev]
    circ = slide.shapes.add_shape(MSO_SHAPE.OVAL, x, y, Inches(0.55), Inches(0.55))
    circ.fill.solid(); circ.fill.fore_color.rgb = color
    circ.line.fill.background(); circ.shadow.inherit = False
    tf = circ.text_frame
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    r = p.add_run(); r.text = str(num)
    r.font.size = Pt(20); r.font.bold = True; r.font.color.rgb = WHITE; r.font.name = FONT


def add_problem_header(s, num, sev, title):
    add_header(s, SEC3, "")
    problem_badge(s, Inches(0.55), Inches(0.5), num, sev)
    add_text(s, Inches(1.3), Inches(0.5), Inches(9.5), Inches(0.55), title, size=24, bold=True, color=DARK)
    add_text(s, Inches(1.3), Inches(1.06), Inches(4), Inches(0.35), SEV_LABEL[sev], size=13, bold=True, color=SEV_COLOR[sev])
    add_rect(s, Inches(0.55), Inches(1.32), Inches(1.1), Pt(3), SEV_COLOR[sev])


# --- 슬라이드 12: 문제점 Overview ---
s = new_slide()
add_header(s, SEC3, "계약 구조 문제점 Overview")
rows12 = [
    ["#", "문제 유형", "건수", "심각도", "영향 금액"],
    ["1", "고부하 배정 (0.8MM 이상)", "7건", "🔴 높음", "10.2억"],
    ["2", "다중 항목 담당 (10개+)", "17명", "🟠 중간", "25.7억"],
    ["3", "다중 담당자 항목 (5명+)", "30건", "🟠 중간", "-"],
    ["4", "TBD/미배정 담당자", "148건", "🔴 높음", "3.5억+"],
    ["5", "단가 급변동 (±30%+)", "45건", "🟠 중간", "-"],
    ["6", "등급별 단가 불일치", "3등급 전부", "🔴 높음", "전체 영향"],
    ["7", "소규모 배분 (0.05MM↓)", "574건", "🟡 낮음", "관리비용"],
    ["8", "담당자+항목 1MM 초과", "3건", "🔴 높음", "4.8억"],
]
add_table(s, Inches(0.55), Inches(1.6), Inches(12.2), Inches(5.0), rows12,
          col_widths=[Inches(0.6), Inches(4.3), Inches(2.1), Inches(2.1), Inches(3.1)],
          highlight_rows={1: RGBColor(0xFC, 0xE4, 0xE4), 4: RGBColor(0xFC, 0xE4, 0xE4),
                            6: RGBColor(0xFC, 0xE4, 0xE4), 8: RGBColor(0xFC, 0xE4, 0xE4)})
add_footer(s, 12)

# --- 슬라이드 13: 문제점1 고부하 배정 ---
s = new_slide()
add_problem_header(s, 1, "high", "고부하 배정 (0.8MM 이상)")
add_text(s, Inches(0.55), Inches(1.5), Inches(12.2), Inches(0.4),
          "문제: 한 사람이 한 시스템에 월 80% 이상 투입 → 휴가·이직 시 업무 공백 리스크", size=14, color=GRAY)
rows13 = [
    ["회사", "항목", "담당자", "MM", "비용"],
    ["YM", "규제 준수 및 인증 심사 지원", "오성범", "1.00", "1.1억"],
    ["HD", "빅데이터포털", "김민호", "1.00", "1.5억"],
    ["STP", "CS Admin", "이승현", "1.00", "1.6억"],
    ["STP", "CS Admin", "마수빈", "1.00", "1.6억"],
    ["ST", "SAP B1 ERP 생산(BM)", "우승원", "1.00", "1.5억"],
    ["STP", "에스티팜 QMS", "정소희", "0.95", "1.5억"],
    ["STG", "IT운영지원 계약", "이민형", "0.92", "1.4억"],
]
add_table(s, Inches(0.55), Inches(2.05), Inches(12.2), Inches(3.85), rows13,
          col_widths=[Inches(1.4), Inches(4.6), Inches(2.2), Inches(1.7), Inches(2.3)])
add_footer(s, 13)

# --- 슬라이드 14: 문제점2 다중 항목 담당자 ---
s = new_slide()
add_problem_header(s, 2, "mid", "다중 항목 담당자 Top 10")
add_text(s, Inches(0.55), Inches(1.5), Inches(12.2), Inches(0.4),
          "문제: 한 사람이 너무 많은 시스템 담당 → 집중도 저하, 품질 리스크", size=14, color=GRAY)
names14 = ["정혜일", "조원재", "심현호", "TBD(PM)", "TBD(Cl)", "맹호빈", "이주렬", "임만수", "TBD(S)", "윤종호"]
counts14 = [24, 16, 15, 13, 13, 13, 13, 13, 12, 12]
add_clustered_bar(s, Inches(0.55), Inches(2.0), Inches(7.1), Inches(4.9),
                   names14, {"담당 항목수": counts14}, [ORANGE], number_format='0"개"',
                   horizontal=True)
add_round_rect(s, Inches(7.9), Inches(2.0), Inches(4.85), Inches(4.9), LIGHT_GRAY)
add_text(s, Inches(8.2), Inches(2.25), Inches(4.3), Inches(0.4), "💡 Insight", size=15, bold=True, color=ORANGE)
add_text(s, Inches(8.2), Inches(2.75), Inches(4.3), Inches(3.9),
          "• 정혜일(물류IT팀): 24개 항목, 0.62MM, 1.0억\n\n"
          "• 조원재: 16개 항목, 1.37MM, 2.4억 (최고비용)\n\n"
          "• Top 10 중 8명이 아키텍쳐인프라팀 소속\n  → 문제 집중\n\n"
          "• TBD 3건 포함 → 미배정 상태로 다항목 관리",
          size=13, color=DARK, line_spacing=1.25)
add_footer(s, 14)

# --- 슬라이드 15: 문제점3 다중 담당자 항목 ---
s = new_slide()
add_problem_header(s, 3, "mid", "다중 담당자 항목 Top")
add_text(s, Inches(0.55), Inches(1.5), Inches(12.2), Inches(0.4),
          "문제: 한 항목에 너무 많은 담당자 → 책임 분산, 커뮤니케이션 복잡도 증가", size=14, color=GRAY)
rows15 = [
    ["항목", "담당자 수", "총 MM", "총 비용"],
    ["EAI", "9명", "2.30", "2.7억"],
    ["운용 서버 규모 279.5대", "8명", "1.29", "2.1억"],
    ["운용 서버 규모 146.8대", "8명", "0.62", "0.8억"],
    ["운용 서버 규모 76.5대", "8명", "0.28", "0.4억"],
    ["(기타 서버 운용 항목)", "8명씩", "-", "-"],
]
add_table(s, Inches(0.55), Inches(2.05), Inches(7.6), Inches(3.4), rows15,
          col_widths=[Inches(3.5), Inches(1.4), Inches(1.3), Inches(1.4)],
          row_colors={1: RED})
add_round_rect(s, Inches(8.4), Inches(2.05), Inches(4.35), Inches(3.4), LIGHT_GRAY)
add_text(s, Inches(8.7), Inches(2.3), Inches(3.8), Inches(0.4), "💡 Insight", size=15, bold=True, color=ORANGE)
add_text(s, Inches(8.7), Inches(2.8), Inches(3.8), Inches(2.5),
          "서버 운용 관련 항목에\n8명씩 균일 배정\n→ 비효율적 세분화\n\n"
          "EAI는 9명 배정, 2.7억 규모로\n가장 복잡한 책임 구조",
          size=13, color=DARK, line_spacing=1.3)
add_footer(s, 15)

# --- 슬라이드 16: 문제점4 TBD/미배정 담당자 ---
s = new_slide()
add_problem_header(s, 4, "high", "TBD / 미배정 담당자 (148건)")
add_text(s, Inches(0.55), Inches(1.5), Inches(12.2), Inches(0.4),
          "문제: 담당자 미확정 상태로 계약 체결 → 실행력 저하", size=14, color=GRAY)
rows16 = [
    ["담당자 유형", "건수", "주요 팀", "총 비용(추정)"],
    ["TBD2", "다수", "정보보안팀", "1.5억+"],
    ["TBD(PM)", "13건", "아키텍쳐인프라팀", "1.4억"],
    ["TBD(Cl)", "13건", "아키텍쳐인프라팀", "1.7억"],
    ["TBD(S)", "12건", "아키텍쳐인프라팀", "1.1억"],
]
add_table(s, Inches(0.55), Inches(2.05), Inches(7.6), Inches(2.9), rows16,
          col_widths=[Inches(2.0), Inches(1.3), Inches(2.5), Inches(1.8)],
          row_colors={1: RED})
add_round_rect(s, Inches(8.4), Inches(2.05), Inches(4.35), Inches(2.9), RGBColor(0xFC, 0xE4, 0xE4))
add_text(s, Inches(8.7), Inches(2.25), Inches(3.8), Inches(0.4), "🚨 핵심", size=15, bold=True, color=RED)
add_text(s, Inches(8.7), Inches(2.7), Inches(3.8), Inches(2.1),
          "정보보안팀(신설)의 신규 업무에\nTBD가 집중되어 있어,\n조직 신설과 동시에\n담당자 확정이 필요함",
          size=13, color=DARK, line_spacing=1.3)
add_text(s, Inches(0.55), Inches(5.2), Inches(12.2), Inches(0.6),
          "총 148건 중 TBD(PM/Cl/S) 38건은 아키텍쳐인프라팀에 집중 — 조직 개편 이후 후속 인력 배치 지연 추정",
          size=13, italic=True, color=GRAY)
add_footer(s, 16)

# --- 슬라이드 17: 문제점5 단가 급변동 ---
s = new_slide()
add_problem_header(s, 5, "mid", "단가 급변동 (±30% 이상, 45건)")
add_text(s, Inches(0.55), Inches(1.5), Inches(12.2), Inches(0.4),
          "문제: 전년 대비 단가 급등/급락 → 예산 예측 어려움", size=14, color=GRAY)
rows17 = [
    ["대표 사례", "25년 단가", "26년 단가", "변동률"],
    ["헬프데스크 중급", "777만원", "1,284만원", "+65%"],
    ["YM 초급", "777만원", "480만원", "-38%"],
]
add_table(s, Inches(0.55), Inches(2.1), Inches(8.2), Inches(1.7), rows17,
          col_widths=[Inches(2.8), Inches(1.8), Inches(1.8), Inches(1.8)],
          row_colors={1: RED, 2: BLUE})
add_round_rect(s, Inches(0.55), Inches(4.1), Inches(12.2), Inches(1.9), LIGHT_GRAY)
add_text(s, Inches(0.85), Inches(4.35), Inches(11.6), Inches(0.4), "💡 Insight", size=15, bold=True, color=ORANGE)
add_text(s, Inches(0.85), Inches(4.8), Inches(11.6), Inches(1.0),
          "45건의 단가가 전년 대비 ±30% 이상 변동 — 등급·시장단가 기준 없이 개별 협상된 결과로 추정되며,\n"
          "예산 수립 시 전년 대비 예측 신뢰도를 저하시킴",
          size=13, color=DARK, line_spacing=1.3)
add_footer(s, 17)

# --- 슬라이드 18: 문제점6 등급별 단가 불일치 (가장 심각) ---
s = new_slide()
add_problem_header(s, 6, "high", "등급별 단가 불일치 (가장 심각)")
add_text(s, Inches(0.55), Inches(1.5), Inches(12.2), Inches(0.4),
          "문제: 같은 등급인데 단가가 크게 다름 → 계약 형평성 문제", size=14, color=GRAY)
rows18 = [
    ["등급", "최소 단가", "최대 단가", "편차율", "단가 종류"],
    ["중급", "640만원", "4,000만원", "525%", "11종"],
    ["초급", "480만원", "1,484만원", "209%", "11종"],
    ["고급", "1,009만원", "1,640만원", "62%", "9종"],
]
add_table(s, Inches(0.55), Inches(2.05), Inches(7.7), Inches(2.5), rows18,
          col_widths=[Inches(1.3), Inches(1.7), Inches(1.7), Inches(1.5), Inches(1.5)],
          row_colors={1: RED})
add_round_rect(s, Inches(8.5), Inches(2.05), Inches(4.25), Inches(4.6), RGBColor(0xFC, 0xE4, 0xE4))
add_text(s, Inches(8.8), Inches(2.3), Inches(3.7), Inches(0.7), "6.25배", size=34, bold=True, color=RED)
add_text(s, Inches(8.8), Inches(3.05), Inches(3.7), Inches(1.5),
          "중급 등급 내 최소 640만원 vs\n최대 4,000만원 — 동일 등급임에도\n6.25배 단가 차이 발생",
          size=13, color=DARK, line_spacing=1.3)
add_clustered_bar(s, Inches(0.55), Inches(4.85), Inches(7.7), Inches(2.15),
                   ["고급", "중급", "초급"], {"최소단가(만원)": [1009, 640, 480], "최대단가(만원)": [1640, 4000, 1484]},
                   [BLUE, RED], number_format='0"만"')
add_footer(s, 18)

# --- 슬라이드 19: 문제점7 소규모 배분 ---
s = new_slide()
add_problem_header(s, 7, "low", "소규모 배분 (0.05MM 이하, 574건)")
add_text(s, Inches(0.55), Inches(1.5), Inches(12.2), Inches(0.4),
          "문제: 월 4시간 이하의 미미한 업무 세분화 → 관리 오버헤드 발생", size=14, color=GRAY)
rows19 = [
    ["현황", "건수", "문제점"],
    ["0.05MM 이하 배분", "574건", "계약서 복잡, 관리비 > 가치"],
    ["0.01MM (월 1시간) 배분", "다수", "실질적 업무 수행 불가"],
]
add_table(s, Inches(0.55), Inches(2.1), Inches(8.5), Inches(2.0), rows19,
          col_widths=[Inches(3.0), Inches(1.6), Inches(3.9)],
          row_colors={1: YELLOW})
kpi_card(s, Inches(9.3), Inches(2.1), Inches(3.45), Inches(2.0), "전체 배정 대비", "62.7%", "574건 / 916건", YELLOW)
add_round_rect(s, Inches(0.55), Inches(4.4), Inches(12.2), Inches(1.9), LIGHT_GRAY)
add_text(s, Inches(0.85), Inches(4.6), Inches(11.6), Inches(0.4), "💡 Insight", size=15, bold=True, color=YELLOW)
add_text(s, Inches(0.85), Inches(5.05), Inches(11.6), Inches(1.0),
          "전체 916건 중 574건(62.7%)이 0.05MM 이하의 초소규모 배분 — 유사 업무 통합 시\n"
          "계약 건수를 대폭 축소하고 관리 효율을 높일 수 있음",
          size=13, color=DARK, line_spacing=1.3)
add_footer(s, 19)

# --- 슬라이드 20: 문제점8 담당자+항목 1MM 초과 ---
s = new_slide()
add_problem_header(s, 8, "high", "담당자+항목 조합 1MM 초과 (3건)")
add_text(s, Inches(0.55), Inches(1.5), Inches(12.2), Inches(0.4),
          "문제: 여러 회사에 동일 업무로 배분되어 합계가 1MM 초과 → 과다 배분", size=14, color=GRAY)
rows20 = [
    ["담당자", "항목", "합계 MM", "배정 회사"],
    ["김현주", "D-Portal", "1.04", "HD, ST, PH, STG, OT (5개사)"],
    ["황현서", "전산자산관리 등", "1.00", "HD, ST, PH, STG (4개사)"],
    ["권창순", "계약/권한관리 등", "1.00", "HD, ST, PH, STG (4개사)"],
]
add_table(s, Inches(0.55), Inches(2.1), Inches(12.2), Inches(2.3), rows20,
          col_widths=[Inches(1.8), Inches(2.7), Inches(1.7), Inches(6.0)],
          row_colors={1: RED})
add_round_rect(s, Inches(0.55), Inches(4.7), Inches(12.2), Inches(1.7), RGBColor(0xFC, 0xE4, 0xE4))
add_text(s, Inches(0.85), Inches(4.9), Inches(11.6), Inches(0.4), "🚨 핵심", size=15, bold=True, color=RED)
add_text(s, Inches(0.85), Inches(5.3), Inches(11.6), Inches(1.0),
          "명목상 총 투입 MM이 1.0(100%)을 넘는 것은 물리적으로 불가능 — 계약서상 중복·과다 산정이거나\n"
          "실제 업무량과 계약 배분이 불일치함을 의미. 즉시 검증 필요",
          size=13, color=DARK, line_spacing=1.3)
add_footer(s, 20)

# --- 슬라이드 21: 문제점 종합 Impact 분석 (Heatmap) ---
s = new_slide()
add_header(s, SEC3, "문제점 종합 Impact 분석", accent=RED)
problems = [
    ("1. 고부하 배정", "high", "10.2억", "7건"),
    ("2. 다중 항목 담당", "mid", "25.7억", "17명"),
    ("3. 다중 담당자 항목", "mid", "-", "30건"),
    ("4. TBD 미배정", "high", "3.5억+", "148건"),
    ("5. 단가 급변동", "mid", "-", "45건"),
    ("6. 등급별 단가 불일치", "high", "전체 영향", "3등급"),
    ("7. 소규모 배분", "low", "관리비용", "574건"),
    ("8. 1MM 초과 배정", "high", "4.8억", "3건"),
]
cols = 4
cw, ch = Inches(2.98), Inches(2.15)
x0, y0 = Inches(0.55), Inches(1.6)
for i, (name, sev, amt, cnt) in enumerate(problems):
    col = i % cols
    row = i // cols
    x = x0 + col * (cw + Inches(0.12))
    y = y0 + row * (ch + Inches(0.15))
    add_round_rect(s, x, y, cw, ch, SEV_COLOR[sev])
    add_text(s, x + Inches(0.18), y + Inches(0.15), cw - Inches(0.35), Inches(0.6), name, size=14, bold=True, color=WHITE, line_spacing=1.1)
    add_text(s, x + Inches(0.18), y + Inches(0.95), cw - Inches(0.35), Inches(0.5), amt, size=20, bold=True, color=WHITE)
    add_text(s, x + Inches(0.18), y + Inches(1.55), cw - Inches(0.35), Inches(0.4), cnt, size=13, color=RGBColor(0xFF, 0xFF, 0xFF))
add_text(s, Inches(0.55), Inches(6.25), Inches(12.2), Inches(0.4),
          "🔴 높음 4건  ·  🟠 중간 3건  ·  🟡 낮음 1건   —   정량 영향 확인분만 합산 시 최소 44.2억 규모",
          size=13, bold=True, color=GRAY)
add_footer(s, 21)

print("Section 3 (slides 12-21) built.")

# ===========================================================================
# SECTION 4. 개선 방법론
# ===========================================================================
SEC4 = "SECTION 4 · 개선 방법론"

# --- 슬라이드 22: MM 배분 정상화 5단계 Framework ---
s = new_slide()
add_header(s, SEC4, "MM 배분 정상화 5단계 Framework", accent=GREEN)
steps22 = [
    ("Step 1", "기준 수립", "개인별 단일시스템 상한 0.8MM · 연간 총상한 12MM · 항목별 최소 0.1MM"),
    ("Step 2", "이상치 탐지(자동화)", "0.8MM 초과 자동 플래그 · 다중회사 합산 1MM 초과 탐지 · 소규모 배분 알림"),
    ("Step 3", "업무 재분배", "고부하 담당자 → 팀내 분산 · 다중항목 담당자 → 핵심 5개 + 나머지 이관"),
    ("Step 4", "단가 표준화", "등급별 단일 단가 체계 · ±10% 밴드 설정 · 예외 사유 문서화 필수"),
    ("Step 5", "모니터링 체계", "월별 배분 대시보드 · 이상치 자동 알림 · 분기별 정합성 검증"),
]
y = Inches(1.55)
for i, (step, title, desc) in enumerate(steps22):
    add_round_rect(s, Inches(0.55), y, Inches(12.2), Inches(1.02), LIGHT_GRAY)
    add_round_rect(s, Inches(0.55), y, Inches(1.55), Inches(1.02), GREEN)
    add_text(s, Inches(0.55), y + Inches(0.28), Inches(1.55), Inches(0.5), step, size=15, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    add_text(s, Inches(2.35), y + Inches(0.1), Inches(3.0), Inches(0.85), title, size=15, bold=True, color=DARK, anchor=MSO_ANCHOR.MIDDLE)
    add_text(s, Inches(5.4), y + Inches(0.1), Inches(7.15), Inches(0.85), desc, size=12, color=GRAY, anchor=MSO_ANCHOR.MIDDLE, line_spacing=1.1)
    y += Inches(1.12)
add_footer(s, 22)

# --- 슬라이드 23: 등급별 표준 단가 체계(안) ---
s = new_slide()
add_header(s, SEC4, "등급별 표준 단가 체계 (안)", accent=GREEN)
rows23 = [
    ["등급", "표준 단가", "허용 범위 (±10%)", "현재 범위"],
    ["고급", "15,500,000원", "14.0 ~ 17.0백만원", "10.1 ~ 16.4백만원"],
    ["중급", "12,800,000원", "11.5 ~ 14.0백만원", "6.4 ~ 40.0백만원 (문제!)"],
    ["초급", "9,900,000원", "9.0 ~ 11.0백만원", "4.8 ~ 14.8백만원 (문제!)"],
]
add_table(s, Inches(0.55), Inches(1.55), Inches(12.2), Inches(2.1), rows23,
          col_widths=[Inches(1.5), Inches(2.7), Inches(3.5), Inches(4.5)],
          row_colors={2: RED, 3: ORANGE})
add_round_rect(s, Inches(0.55), Inches(3.95), Inches(12.2), Inches(2.6), LIGHT_GRAY)
add_text(s, Inches(0.85), Inches(4.15), Inches(11.6), Inches(0.4), "적용 규칙", size=15, bold=True, color=GREEN)
add_text(s, Inches(0.85), Inches(4.65), Inches(11.6), Inches(1.75),
          "① 범위 초과 시 사유서 필수 (특수기술, 시장단가 등)\n"
          "② 전년 대비 ±15% 초과 변동 시 별도 승인 필요\n"
          "③ 신규 계약 시 표준 단가 우선 적용",
          size=14, color=DARK, line_spacing=1.5)
add_footer(s, 23)

# --- 슬라이드 24: 담당자 배정 최적화 Matrix ---
s = new_slide()
add_header(s, SEC4, "담당자 배정 최적화 Matrix", accent=GREEN)
rows24 = [
    ["상황", "현재 문제", "개선 방향", "기대 효과"],
    ["1인 다중시스템", "24개 시스템 담당", "핵심 5개 + 나머지 이관", "집중도↑, 품질↑"],
    ["1시스템 다중담당", "9명이 1개 담당", "주담당 1명 + 백업 1명", "책임 명확화"],
    ["고부하 배정", "1.0 MM 배정", "0.6~0.8 MM로 분산", "리스크↓"],
    ["TBD 미배정", "148건 미확정", "계약 전 담당자 확정 필수", "실행력↑"],
    ["소규모 배분", "574건(0.05MM↓)", "유사 업무 통합 → 100건↓", "관리효율↑"],
]
add_table(s, Inches(0.55), Inches(1.6), Inches(12.2), Inches(5.0), rows24,
          col_widths=[Inches(2.4), Inches(3.0), Inches(3.6), Inches(3.2)])
add_footer(s, 24)

# --- 슬라이드 25: 계약 정상화 로드맵 (3 Phase) ---
s = new_slide()
add_header(s, SEC4, "계약 정상화 로드맵 (3 Phase)", accent=GREEN)
phases = [
    ("Phase 1", "1개월", "현황 정리", ["TBD 148건 담당자 확정", "고부하 7건 재배분 계획 수립", "단가 불일치 사유 조사"], BLUE),
    ("Phase 2", "2개월", "구조 개선", ["다중 항목 담당자 업무 재조정", "소규모 배분 통합 (574건→100건 목표)", "등급별 표준 단가 적용 시작"], ORANGE),
    ("Phase 3", "3개월", "시스템화", ["자동 이상치 탐지 대시보드 구축", "배분 기준 위반 시 알림 체계", "분기별 정합성 검증 프로세스 정착"], GREEN),
]
timeline_y = Inches(1.7)
add_rect(s, Inches(0.9), timeline_y + Inches(0.28), Inches(11.5), Pt(3), MID_GRAY)
seg_w = Inches(11.5) / 3
for i, (name, dur, title, items, color) in enumerate(phases):
    x = Inches(0.9) + i * seg_w
    dot = s.shapes.add_shape(MSO_SHAPE.OVAL, x, timeline_y + Inches(0.14), Inches(0.35), Inches(0.35))
    dot.fill.solid(); dot.fill.fore_color.rgb = color; dot.line.color.rgb = WHITE; dot.line.width = Pt(2); dot.shadow.inherit = False
    add_text(s, x - Inches(0.3), timeline_y - Inches(0.55), seg_w + Inches(0.3), Inches(0.5),
              f"{name} ({dur})", size=15, bold=True, color=color)
    card_y = timeline_y + Inches(0.85)
    add_round_rect(s, x, card_y, seg_w - Inches(0.25), Inches(3.8), LIGHT_GRAY)
    add_rect(s, x, card_y, seg_w - Inches(0.25), Inches(0.55), color)
    add_text(s, x + Inches(0.2), card_y + Inches(0.08), seg_w - Inches(0.6), Inches(0.4), title, size=15, bold=True, color=WHITE)
    body = "\n\n".join(f"• {it}" for it in items)
    add_text(s, x + Inches(0.2), card_y + Inches(0.75), seg_w - Inches(0.6), Inches(2.9), body, size=12, color=DARK, line_spacing=1.2)
add_footer(s, 25)

# --- 슬라이드 26: 기대 효과 및 KPI ---
s = new_slide()
add_header(s, SEC4, "기대 효과 및 KPI", accent=GREEN)
kpis = [
    ("계약 효율성", "+30%", "정상화 로드맵 완료 후 목표", GREEN),
    ("TBD 미배정", "148건 → 0건", "Phase 1 내 전건 확정", BLUE),
    ("소규모 배분 건수", "574건 → 100건", "유사 업무 통합", ORANGE),
    ("등급별 단가 편차", "525% → ±10%", "표준 단가 체계 적용", RED),
]
x = Inches(0.55); y = Inches(1.65)
for i, (label, value, note, color) in enumerate(kpis):
    if i == 2:
        x = Inches(0.55); y += Inches(2.15)
    kpi_card(s, x, y, Inches(5.95), Inches(1.9), label, value, note, color)
    x += Inches(6.25)
add_footer(s, 26)

# --- 슬라이드 27: 권장 액션 아이템 (우선순위별) ---
s = new_slide()
add_header(s, SEC4, "권장 액션 아이템 (우선순위별)", accent=GREEN)
actions = [
    ("긴급", RED, [
        "TBD 148건 담당자 즉시 확정 (정보보안팀 우선)",
        "1MM 초과 배정 3건 검증 및 정정",
        "등급별 단가 불일치 사유 전수 조사",
    ]),
    ("단기 (1~2개월)", ORANGE, [
        "고부하 배정 7건 팀내 재분산",
        "다중 항목 담당자(17명) 업무 재조정",
        "단가 급변동 45건 근거 문서화",
    ]),
    ("중장기 (3개월+)", GREEN, [
        "소규모 배분 574건 통합 (목표 100건)",
        "등급별 표준 단가 체계 시행",
        "이상치 자동 탐지 대시보드 구축",
    ]),
]
y = Inches(1.6)
for label, color, items in actions:
    add_round_rect(s, Inches(0.55), y, Inches(2.1), Inches(1.55), color)
    add_text(s, Inches(0.55), y + Inches(0.5), Inches(2.1), Inches(0.6), label, size=15, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    body = "\n".join(f"• {it}" for it in items)
    add_text(s, Inches(2.85), y + Inches(0.1), Inches(9.9), Inches(1.4), body, size=13, color=DARK, line_spacing=1.35, anchor=MSO_ANCHOR.MIDDLE)
    y += Inches(1.75)
add_footer(s, 27)

print("Section 4 (slides 22-27) built.")

# ===========================================================================
# SECTION 5. 부록
# ===========================================================================
SEC5 = "SECTION 5 · 부록"

# --- 슬라이드 28: Top 10 담당자 / 주요 고비용 세부 항목 ---
s = new_slide()
add_header(s, SEC5, "Top 10 담당자 / 주요 고비용 세부 항목", accent=GRAY)
rows28a = [
    ["담당자", "팀", "담당 항목수", "총 MM", "총 비용"],
    ["정혜일", "물류 IT팀", "24개", "0.62", "1.0억"],
    ["조원재", "아키텍쳐인프라팀", "16개", "1.37", "2.4억"],
    ["심현호", "아키텍쳐인프라팀", "15개", "1.28", "1.8억"],
    ["맹호빈", "아키텍쳐인프라팀", "13개", "1.18", "2.0억"],
    ["임만수", "아키텍쳐인프라팀", "13개", "1.00", "1.6억"],
]
add_table(s, Inches(0.55), Inches(1.55), Inches(6.2), Inches(2.9), rows28a,
          col_widths=[Inches(1.2), Inches(2.1), Inches(1.1), Inches(0.9), Inches(0.9)], font_size=11)
rows28b = [
    ["세부 항목", "관련 지표", "비용"],
    ["EAI (다중담당 9명)", "2.30 MM", "2.7억"],
    ["STP CS Admin ×2인", "2.00 MM", "3.2억"],
    ["운용 서버 279.5대", "1.29 MM", "2.1억"],
    ["에스티팜 QMS", "0.95 MM", "1.5억"],
    ["빅데이터포털", "1.00 MM", "1.5억"],
]
add_table(s, Inches(6.95), Inches(1.55), Inches(5.8), Inches(2.9), rows28b,
          col_widths=[Inches(2.6), Inches(1.6), Inches(1.6)], font_size=11)
add_text(s, Inches(0.55), Inches(4.65), Inches(12.2), Inches(0.35),
          "※ 고비용 세부 항목은 본문에서 언급된 항목 기준이며, 전체 항목 기준 정식 순위는 원본 데이터 재조회가 필요함",
          size=11, italic=True, color=GRAY)
add_footer(s, 28)

# --- 슬라이드 29: 용어 설명 ---
s = new_slide()
add_header(s, SEC5, "용어 설명", accent=GRAY)
terms = [
    ("MM (Man-Month)", "1인이 1개월간 100% 투입하는 공수 단위. 1.0MM = 해당월 전체 공수 투입"),
    ("TBD (To Be Determined)", "담당자가 아직 확정되지 않은 배정 상태 (PM/Cl/S 등은 역할 구분 코드)"),
    ("도입구분(기존/신규)", "기존: 2025년 이전부터 유지된 계약 / 신규: 2026년 신규 도입 항목"),
    ("등급", "고급 / 중급 / 초급으로 구분되는 투입 인력의 숙련도·단가 등급"),
    ("단가 편차율", "동일 등급 내 (최대단가－최소단가) ÷ 최소단가 × 100 으로 계산한 격차 지표"),
]
y = Inches(1.65)
for term, desc in terms:
    add_text(s, Inches(0.55), y, Inches(3.3), Inches(0.8), term, size=15, bold=True, color=BLUE)
    add_text(s, Inches(4.0), y, Inches(8.75), Inches(0.8), desc, size=13, color=DARK, line_spacing=1.2)
    y += Inches(1.0)
add_footer(s, 29)

# --- 슬라이드 30: 데이터 출처 및 기준 / Q&A ---
s = new_slide()
add_header(s, SEC5, "데이터 출처 및 기준", accent=GRAY)
add_text(s, Inches(0.55), Inches(1.6), Inches(12.2), Inches(2.4),
          "• 원본 데이터: 그룹사 계약 data (Excel), 범위 A3:U1108 (1,106개 행 × 21개 열)\n\n"
          "• 주요 컬럼: A(회사명) · E(대분류) · F(도입구분) · G(항목) · I(팀명) · J(담당자) · "
          "K(등급) · L(25년MM) · O(25년비용) · P(26년MM) · R(26년단가) · T(26년비용)\n\n"
          "• 분석 기준일: 2026년 계약 확정 데이터 기준, 억원 단위 반올림 표기",
          size=14, color=DARK, line_spacing=1.4)
add_rect(s, Inches(0.55), Inches(4.3), Inches(12.2), Pt(1.5), MID_GRAY)
add_text(s, Inches(0.55), Inches(4.7), Inches(12.2), Inches(1.2),
          "Q & A", size=40, bold=True, color=BLUE, align=PP_ALIGN.CENTER)
add_text(s, Inches(0.55), Inches(5.6), Inches(12.2), Inches(0.5),
          "감사합니다", size=16, color=GRAY, align=PP_ALIGN.CENTER)
add_footer(s, 30)

print("Section 5 (slides 28-30) built.")

OUT_PATH = "/home/user/first-project/it-contract-analysis-2026/IT용역계약_2026_분석보고.pptx"
prs.save(OUT_PATH)
print(f"Saved: {OUT_PATH}  ({len(prs.slides.__iter__.__self__._sldIdLst)} slides)")
