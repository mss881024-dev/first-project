#!/usr/bin/env python3
"""카카오뱅크 거래내역 엑셀 → 가계부 가져오기용 JSON.

사용법:
    python3 scripts/kakaobank_import.py --inspect 파일.xlsx
        시트를 그대로 찍어본다. 서식이 바뀌었을 때 먼저 이걸로 확인한다.
    python3 scripts/kakaobank_import.py 파일1.xlsx 파일2.xlsx > out.json
        앱의 ⚙️ → 가져오기에 붙여넣을 JSON을 만든다.

암호(생년월일 6자리)가 걸린 파일은 --password 로 넘긴다.
계좌는 파일명의 계좌번호로 자동 판별한다.
"""

import argparse
import io
import json
import re
import sys

import openpyxl

# 계좌번호 → 앱의 탭. app.js의 ACCOUNTS와 같아야 한다.
ACCOUNT_BY_NO = {
    'N0605513952': 'gongeum',   # 공금마통
    'N4776202988': 'car',       # 차마통
}

# 적요/거래내용에 이 말이 들어가면 그 카테고리로 본다. 위에서부터 먼저 맞는 것을 쓴다.
EXPENSE_RULES = [
    (r'카드대금|카드결제|[가-힣]{2,4}카드',        '카드대금'),
    (r'이자|대출이자',                             '대출·이자'),
    (r'대출|마이너스|한도',                        '대출·이자'),
    (r'보험|국민연금|건강보험|세금|지방세|자동차세', '보험·세금'),
    (r'관리비|관리사무소|전기|가스|수도|통신|SKT|KT|LG U\+', '주거·통신'),
    (r'주유|S-OIL|GS칼텍스|하이패스|주차|정비|톨', '교통·차량'),
    (r'병원|의원|약국|치과',                       '의료'),
    (r'쿠팡|무신사|ZARA|네이버페이|배민|요기요',   '쇼핑'),
    (r'이마트|홈플러스|롯데마트|GS25|CU|세븐일레븐','식비'),
    (r'증권|주식|ETF|적립식',                      '투자'),
]
INCOME_RULES = [
    (r'급여|상여|월급',              '월급·상여'),
    (r'대출|마이너스|한도|차입',     '대출·차입'),
    (r'이자|환급|정산|환불',         '환급·이자'),
]

SALARY_DAY = 25          # 월급일
SALARY_DAY_WINDOW = 2    # 주말이면 당겨지므로 23~25일 입금도 월급 후보로 본다


def load_sheet(path, password=None):
    if password:
        import msoffcrypto
        buf = io.BytesIO()
        with open(path, 'rb') as f:
            office = msoffcrypto.OfficeFile(f)
            office.load_key(password=password)
            office.decrypt(buf)
        buf.seek(0)
        return openpyxl.load_workbook(buf, data_only=True).worksheets[0]
    return openpyxl.load_workbook(path, data_only=True).worksheets[0]


def inspect(path, password=None):
    ws = load_sheet(path, password)
    print('시트:', ws.title, ws.dimensions)
    for i, row in enumerate(ws.iter_rows(values_only=True), 1):
        if i > 40:
            print('... (이하 생략)')
            break
        print(i, '|', ' | '.join('' if c is None else str(c) for c in row))


def find_header(ws):
    """헤더 행을 찾아 {열이름: 인덱스}를 돌려준다. 서식이 조금 바뀌어도 견디게 키워드로 찾는다."""
    for idx, row in enumerate(ws.iter_rows(values_only=True), 1):
        cells = ['' if c is None else str(c).strip() for c in row]
        joined = ' '.join(cells)
        if ('거래일' in joined or '거래 일' in joined) and ('금액' in joined):
            return idx, cells
    raise SystemExit('헤더 행을 찾지 못했습니다. --inspect 로 서식을 확인하세요.')


def col_of(header, *keywords):
    for i, name in enumerate(header):
        flat = name.replace(' ', '')
        if any(k in flat for k in keywords):
            return i
    return None


def parse_date(v):
    if v is None:
        return None
    if hasattr(v, 'strftime'):
        return v.strftime('%Y-%m-%d')
    m = re.search(r'(\d{4})[-./](\d{1,2})[-./](\d{1,2})', str(v))
    if not m:
        return None
    return '%s-%02d-%02d' % (m.group(1), int(m.group(2)), int(m.group(3)))


def parse_amount(v):
    if v is None or v == '':
        return 0
    if isinstance(v, (int, float)):
        return int(abs(v))
    digits = re.sub(r'[^0-9-]', '', str(v))
    return int(abs(int(digits))) if digits not in ('', '-') else 0


def classify(kind, note, date):
    rules = INCOME_RULES if kind == 'income' else EXPENSE_RULES
    # 체크카드·직불은 통장에서 바로 빠지는 실제 소비다. 신용카드 결제대금이 아니므로
    # '카드대금' 규칙을 빼고 가맹점 기준으로 분류한다(안 그러면 지출 집계에서 빠져버린다).
    if kind == 'expense' and re.search(r'체크카드|직불', note):
        rules = [r for r in rules if r[1] != '카드대금']
    for pattern, cat in rules:
        if re.search(pattern, note, re.IGNORECASE):
            return cat
    if kind == 'income':
        day = int(date[8:10])
        if SALARY_DAY - SALARY_DAY_WINDOW <= day <= SALARY_DAY:
            return '월급·상여'
        return '기타수입'
    return '기타'


def convert(path, password=None):
    m = re.search(r'(N\d{10})', path)
    if not m or m.group(1) not in ACCOUNT_BY_NO:
        raise SystemExit('파일명에서 계좌를 판별할 수 없습니다: %s' % path)
    account = ACCOUNT_BY_NO[m.group(1)]

    ws = load_sheet(path, password)
    header_idx, header = find_header(ws)
    c_date   = col_of(header, '거래일시', '거래일자', '거래일')
    c_type   = col_of(header, '구분', '입출금')
    c_in     = col_of(header, '입금액', '입금')
    c_out    = col_of(header, '출금액', '출금')
    c_amount = col_of(header, '거래금액', '금액')
    # 적요가 '거래구분/상대방/메모'로 흩어져 있어서(카카오뱅크 서식) 텍스트 열을 모두 모아야
    # 분류가 제대로 된다. 한 열만 읽으면 '대출이자', '관리비' 같은 단서를 놓친다.
    used = {c_date, c_type, c_in, c_out, c_amount}
    note_cols = [i for i, name in enumerate(header)
                 if i not in used
                 and any(k in name.replace(' ', '')
                         for k in ('거래내용', '적요', '상대방', '내용', '메모', '거래구분', '구분'))]

    rows, skipped = [], 0
    for row in ws.iter_rows(min_row=header_idx + 1, values_only=True):
        get = lambda i: (row[i] if i is not None and i < len(row) else None)
        date = parse_date(get(c_date))
        if not date:
            skipped += 1
            continue
        parts, note = [], ''
        for i in note_cols:
            v = str(get(i) or '').strip()
            if v and v not in parts:
                parts.append(v)
        note = ' '.join(parts)

        # 입금/출금 열이 따로 있으면 그걸 쓰고, 없으면 '구분' 열로 판단한다.
        amt_in, amt_out = parse_amount(get(c_in)), parse_amount(get(c_out))
        if amt_in or amt_out:
            kind, amount = ('income', amt_in) if amt_in else ('expense', amt_out)
        else:
            amount = parse_amount(get(c_amount))
            kind = 'income' if '입금' in str(get(c_type) or '') else 'expense'
        if amount <= 0:
            skipped += 1
            continue

        rows.append({
            'date': date, 'type': kind, 'amount': amount,
            'category': classify(kind, note, date), 'note': note,
        })

    sys.stderr.write('%s → %s: %d건 (건너뜀 %d)\n' % (path, ACCOUNTS_LABEL.get(account, account), len(rows), skipped))
    return account, rows


ACCOUNTS_LABEL = {'gongeum': '공금마통', 'car': '차마통', 'card': '카드'}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('files', nargs='+')
    ap.add_argument('--password', help='암호 걸린 파일의 비밀번호 (생년월일 6자리)')
    ap.add_argument('--inspect', action='store_true', help='변환하지 않고 시트를 그대로 출력')
    args = ap.parse_args()

    if args.inspect:
        for path in args.files:
            inspect(path, args.password)
        return

    accounts = {}
    for path in args.files:
        account, rows = convert(path, args.password)
        accounts.setdefault(account, []).extend(rows)
    print(json.dumps({'version': 1, 'accounts': accounts}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
