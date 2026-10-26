'use strict';

const ACCOUNTS = {
  gongeum: { key: 'fintrack_gongeum', label: '공금마통' },
  car:     { key: 'fintrack_car',     label: '차마통' },
  card:    { key: 'fintrack_card',    label: '카드' },
};

// 카테고리는 이 배열만 고치면 전체에 반영된다.
const CATEGORIES = [
  '식비', '생활비', '교통·차량', '주거·통신', '보험·세금', '의료',
  '경조사', '여행', '쇼핑', '취미·여가', '교육',
  '대출·이자', '투자', '대차(빌림·빌려줌)', '카드대금',
  '대납·타인부담', '차마통 대체청구', '기타',
];
// 입금 카테고리. '남은 금액'의 총액이 되는 것과, 총액에서 빼는 것을 구분한다.
const INCOME_CATEGORIES = ['월급·상여', '사업·부수입', '환급·이자', '대차 회수', '대출·차입', '기타수입'];
// 빌린 돈·돌려받은 돈은 벌어서 쓸 수 있는 돈이 아니므로 월 예산 총액에서 뺀다.
const INCOME_EXCLUDED_FROM_BUDGET = ['대출·차입', '대차 회수'];
const TRANSFER_CATEGORY = '계좌이동';
const SETTINGS_KEY = 'fintrack_settings';
// 월급은 코드에 적지 않는다(이 저장소는 public). 각자 브라우저에서 '수정'으로 넣으면
// localStorage에만 저장된다.
const DEFAULT_SALARY = 0;
const DEBT_CATEGORY = '대차(빌림·빌려줌)';
const BANK_ACCOUNTS = ['gongeum', 'car'];   // 잔액이 있는 계좌
// '이번 달 남은 금액'은 생활비 계좌 기준으로 낸다. 차마통은 차·대출·목돈이 오가는
// 계좌라 같이 더하면 생활비가 얼마 남았는지 안 보인다(차마통 탭에서 따로 본다).
const BUDGET_ACCOUNT = 'gongeum';

// 가계(월급 기준 정리)는 이 달부터 시작한다. 그 이전 달은 마통 추적 기록만 남아 있고
// 카드 명세서가 갖춰져 있지 않아, 가계 숫자로 보여주면 틀린 값이 된다.
const HOUSEHOLD_START_MONTH = '2026-11';

// 가계 탭(월급 기준)에 넣는 지출 카테고리. 마통 운용·대출·지인 대차는 들어가지 않는다.
// 범위는 화면에 그대로 적어 보여준다.
// 카드 명세서에는 찍혔지만 월급에서 나가지 않는 것. 기록은 남기되 가계 집계에서만 뺀다.
// 지우지 않는 이유: 지우면 카드 명세서 합계와 대조가 안 된다.
//  - 대납·타인부담: 남이 현금으로 메워준 건
//  - 차마통 대체청구: 카드 할부 중 일부를 차마통에서 따로 결제하는 건(임의단품 선결제 등)
const NON_HOUSEHOLD_CATEGORIES = ['대납·타인부담', '차마통 대체청구'];

const HOUSEHOLD_CATEGORIES = [
  '식비', '생활비', '주거·통신', '보험·세금', '의료',
  '경조사', '여행', '쇼핑', '취미·여가', '교육', '교통·차량', '기타',
];
const CARD_ACCOUNT  = 'card';
// 현금 흐름 기준이다. 나간 돈은 소비든 대차든 자산이든 전부 '나간 돈'으로 센다.
// 집계에서 빼는 것은 '같은 돈을 두 번 세게 되는 것'뿐이다.
//  - 카드대금: 통장에서 빠진 이 금액을 카드 명세서 상세가 대체한다 (둘 다 세면 이중)
//  - 계좌이동(transfer): 내 계좌끼리 옮긴 돈은 전체로 보면 늘지도 줄지도 않는다
const EXCLUDED_AS_DOUBLE_COUNT = ['카드대금'];
// 가계(월급 기준 생활비) 범위 밖. 마통 운용·빚·투자는 성격이 달라 따로 본다.
// 화면의 '이 정산이 다루는 범위' 문구와 같은 기준이어야 한다.
const OUT_OF_HOUSEHOLD_EXPENSE = ['대차(빌림·빌려줌)', '대출·이자', '투자'];
const OUT_OF_HOUSEHOLD_INCOME  = ['대차 회수', '대출·차입'];

let currentAccount = 'gongeum';
let currentYear    = new Date().getFullYear();
let currentMonth   = new Date().getMonth() + 1;
let selectedType   = 'expense';
let selectedDir    = 'out';
let pendingDelete  = null;
let undoTimer      = null;

function loadSettings() {
  try {
    const raw = JSON.parse(localStorage.getItem(SETTINGS_KEY)) || {};
    return {
      salary: raw.salary || DEFAULT_SALARY,
      topup: raw.topup || 0,          // 마통에서 끌어와 생활비에 보태는 돈
      fixed: raw.fixed || [],         // 매달 고정 지출 (인터넷·모바일·보험 등)
      etc: raw.etc || [],             // 기타 (밥값·용돈 등)
      separate: raw.separate || [],   // 별도 결제 건 — 참고만, 총계에 넣지 않음
      overrides: raw.overrides || {}, // 월별 월급 덮어쓰기
      income: raw.income || [],       // 월급·마통 외에 매달 들어오는 돈 (예: 자사주 보전)
      extraIn: raw.extraIn || {},     // 그 달에만 들어온 돈 — {"2026-11":[{name,amount}]}
    };
  } catch {
    return { salary: DEFAULT_SALARY, topup: 0, income: [], fixed: [], etc: [], separate: [], overrides: {}, extraIn: {} };
  }
}
function saveSettings(s) { localStorage.setItem(SETTINGS_KEY, JSON.stringify(s)); }
// 설정에 적어둔 월급. 그 달 통장에 급여 입금이 찍혀 있으면 그 실제 금액을 쓰고,
// 이건 내역이 아직 없는 달의 '예정' 값으로만 쓴다. (급여는 급여계좌에서 공금마통으로
// 자기이체로 넘어오므로 '계좌이동'으로 찍힌다 — 짝이 없는 입금이 그것이다.)
function salaryFor(mKey) {
  const s = loadSettings();
  return mKey in s.overrides ? s.overrides[mKey] : s.salary;
}
// 차마통에서 공금마통으로 실제로 옮겨온 돈. 고정값이 아니라 그 달 실제 이동액을 쓴다.
// 짝이 확인된 이동만 센다 — 짝 없는 자기이체는 급여계좌에서 온 돈이라 월급과 중복된다.
function topupFor(mKey) {
  return getMonthlyTxns(BUDGET_ACCOUNT, mKey)
    .filter(t => t.type === 'transfer' && t.peerAcct && t.peerAcct !== BUDGET_ACCOUNT)
    .reduce((s,t) => s + (t.dir === 'in' ? t.amount : -t.amount), 0);
}

function loadData(account) {
  try {
    const raw = JSON.parse(localStorage.getItem(ACCOUNTS[account].key)) || [];
    return raw.map(normalize);
  } catch { return []; }
}
function saveData(account, data) { localStorage.setItem(ACCOUNTS[account].key, JSON.stringify(data)); }
function getTransactions(account) { return loadData(account); }
function addTransaction(account, txn) { const data = loadData(account); data.push(txn); saveData(account, data); }
function removeTransaction(account, id) { saveData(account, loadData(account).filter(t => t.id !== id)); }

// 카테고리가 없던 기존 데이터도 깨지지 않게 보정한다.
function normalize(t) {
  const type = t.type === 'income' || t.type === 'transfer' ? t.type : 'expense';
  return {
    id: t.id || uid(),
    type,
    date: t.date,
    // 카드 할인·환불은 음수로 들어온다. abs를 씌우면 할인이 지출로 더해진다.
    amount: Number(t.amount) || 0,
    category: t.category || (type === 'transfer' ? TRANSFER_CATEGORY : type === 'income' ? '기타수입' : '기타'),
    dir: type === 'transfer' ? (t.dir === 'in' ? 'in' : 'out') : null,
    // 카드는 '언제 긁었나'(date)와 '언제 빠지나'(bm, 청구월)가 다르다. 집계는 bm 기준.
    bm: /^\d{4}-\d{2}$/.test(String(t.bm || '')) ? t.bm : String(t.date || '').slice(0,7),
    bal: typeof t.bal === 'number' ? t.bal : null,  // 명세서의 '거래 후 잔액'
    peerAcct: t.peerAcct || '',  // 계좌이동의 상대 계좌
    issuer: t.issuer || '',   // 카드 거래: 국민/BC/현대
    peer: t.peer || '',       // 대차 거래: 상대방
    note: t.note || '',
    createdAt: t.createdAt || 0,
  };
}

function uid() { return Date.now().toString(36) + Math.random().toString(36).slice(2); }
function fmtWon(n) { return '₩' + Math.abs(n).toLocaleString('ko-KR'); }
function fmtDate(iso) { const p = iso.split('-'); return parseInt(p[1],10) + '.' + p[2]; }
function escHtml(s) { return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'); }
function monthKey(y, m) { return y + '-' + String(m).padStart(2,'0'); }
function prevMonthKey() { return currentMonth === 1 ? monthKey(currentYear-1, 12) : monthKey(currentYear, currentMonth-1); }
function lastDayOf(y, m) { return new Date(y, m, 0).getDate(); }
function monthEnd(y, m) { return monthKey(y, m) + '-' + String(lastDayOf(y, m)).padStart(2,'0'); }
function isInflow(t)  { return t.type === 'income'  || (t.type === 'transfer' && t.dir === 'in');  }
function isOutflow(t) { return t.type === 'expense' || (t.type === 'transfer' && t.dir === 'out'); }
// 해당 날짜까지의 잔액. 마이너스통장은 개시 잔액이 커서 거래 합계만 더하면 틀린다.
// 명세서가 실어준 '거래 후 잔액'이 있으면 그 날짜 이전 마지막 값을 그대로 쓴다.
function balanceAsOf(account, dateStr) {
  const txns = getTransactions(account).filter(t => t.date <= dateStr);
  const withBal = txns.filter(t => t.bal !== null)
                      .sort((a,b) => a.date.localeCompare(b.date) || a.createdAt - b.createdAt);
  if (withBal.length) {
    const last = withBal[withBal.length - 1];
    // 잔액이 적힌 마지막 거래 이후에 손으로 넣은 거래가 있으면 그것만 더한다.
    const after = txns.filter(t => t.bal === null &&
      (t.date > last.date || (t.date === last.date && t.createdAt > last.createdAt)));
    return after.reduce((s,t) => s + (isInflow(t) ? t.amount : -t.amount), last.bal);
  }
  return txns.reduce((s,t) => s + (isInflow(t) ? t.amount : -t.amount), 0);
}
function isSpending(t) { return t.type === 'expense' && EXCLUDED_AS_DOUBLE_COUNT.indexOf(t.category) === -1; }
function txnKey(t) { return [t.date, t.bm, t.type, t.dir, t.amount, t.category, t.note].join('|'); }

const el = id => document.getElementById(id);
const elMonthLabel   = el('monthLabel');
const elTabs         = el('accountTabs');
const elOvLeft       = el('ovLeft');
const elOvBar        = el('ovBar');
const elOvDaily      = el('ovDaily');
const elOvDelta      = el('ovDelta');
const elOvWarn       = el('ovWarn');
const elOverview     = el('overview');
const elHouseNote    = el('houseNote');
const elHouseStart   = el('houseStart');
const elHouseFlow    = el('houseFlow');
const elHsIn         = el('hsIn');
const elHsFixed      = el('hsFixed');
const elHsCard       = el('hsCard');
const elHsEtc        = el('hsEtc');
const elHsSep        = el('hsSep');
const elHsSepBox     = el('hsSepBox');
const elHsFormula    = el('hsFormula');
const elDebtPanel    = el('debtPanel');
const elDebtList     = el('debtList');
const elDebtEmpty    = el('debtEmpty');
const elCashFlow     = el('cashFlow');
const elCardFlow     = el('cardFlow');
const elCfCarry      = el('cfCarry');
const elCfIn         = el('cfIn');
const elCfOut        = el('cfOut');
const elCfLeft       = el('cfLeft');
const elCardUse      = el('cardUse');
const elCardPrev     = el('cardPrev');
const elCatSection   = el('categorySection');
const elCatList      = el('categoryList');
const elTxnList      = el('transactionList');
const elEmptyState   = el('emptyState');
const elModalOverlay = el('modalOverlay');
const elSegments     = el('segmentControl');
const elInputDate    = el('inputDate');
const elInputAmount  = el('inputAmount');
const elInputCategory= el('inputCategory');
const elCategoryGroup= el('categoryGroup');
const elBillGroup    = el('billGroup');
const elInputBill    = el('inputBill');
const elDirGroup     = el('dirGroup');
const elDirControl   = el('dirControl');
const elInputNote    = el('inputNote');
const elSnackbar     = el('snackbar');
const elSnackbarMsg  = el('snackbarMsg');
const elDataOverlay  = el('dataOverlay');
const elImportText   = el('importText');
const elImportFile   = el('importFile');

function renderCategoryOptions(type) {
  const list = type === 'income' ? INCOME_CATEGORIES : CATEGORIES;
  elInputCategory.innerHTML = list
    .map(c => '<option value="' + escHtml(c) + '">' + escHtml(c) + '</option>').join('');
}

// 카드는 청구월(bm), 통장은 거래일 기준으로 그 달에 속한다.
function txnMonth(t, account) { return account === CARD_ACCOUNT ? t.bm : t.date.slice(0,7); }
function getMonthlyTxns(account, mKey) {
  const acct = account || currentAccount;
  const key  = mKey || monthKey(currentYear, currentMonth);
  return getTransactions(acct).filter(t => txnMonth(t, acct) === key);
}

function renderSummary(txns) {
  if (currentAccount === 'card') { renderCardFlow(txns); }
  else { renderCashFlow(txns); }

}

// 가계(월급 기준 정리). 흐름 기준이다 — 실제로 돈이 움직인 것만 '실제'로 센다.
//
// 설정값(월급·마통 보충·추가 수입·고정 지출·기타)은 그 달 통장 내역과 금액으로 맞춰본다.
//  - 같은 금액의 거래가 그 달에 있으면 그 줄은 '실제'(real: true) 로 확정하고 그 거래를 소비한다.
//  - 맞는 거래가 없으면 '예정'(real: false) 으로 남긴다. 아직 안 빠진 돈이거나 다른 계좌에서 나간 돈이다.
//  - 어느 설정값에도 안 잡힌 통장 거래는 '통장에서 (적요)' 줄로 따로 세운다 — 빠뜨리지 않기 위해서다.
// 총계는 실제 + 예정을 다 더한다. 예정이 섞여 있으면 화면에 그렇게 적는다.
function householdTotals(mKey) {
  const cfg = loadSettings();
  const bankRows = getMonthlyTxns(BUDGET_ACCOUNT, mKey);
  const hasBank  = bankRows.length > 0;

  // 가계 범위 안의 통장 거래만 매칭 대상이다.
  // 카드대금은 카드 명세서 상세가 대체하므로 뺀다(이중 계산).
  const bankIn = bankRows.filter(t =>
    (t.type === 'income' && OUT_OF_HOUSEHOLD_INCOME.indexOf(t.category) === -1) ||
    (t.type === 'transfer' && t.dir === 'in' && t.category !== '카드대금'));
  const bankOut = bankRows.filter(t =>
    t.type === 'expense' &&
    EXCLUDED_AS_DOUBLE_COUNT.indexOf(t.category) === -1 &&
    OUT_OF_HOUSEHOLD_EXPENSE.indexOf(t.category) === -1);

  // 같은 금액의 거래를 하나 집어 쓴다(한 번 쓴 거래는 다시 안 쓴다).
  const take = (pool, amount) => {
    const i = pool.findIndex(t => t.amount === amount);
    return i === -1 ? null : pool.splice(i, 1)[0];
  };
  const leftIn = bankIn.slice(), leftOut = bankOut.slice();
  const matched = (pool, name, amount, fallbackNote) => {
    const hit = amount ? take(pool, amount) : null;
    return hit
      ? { name, amount: hit.amount, real: true, note: hit.note }
      : { name, amount: amount || 0, real: false, note: fallbackNote || '' };
  };

  // ---- 들어온 돈 ----
  // 월급: 짝 없는 자기이체 입금이 급여계좌에서 넘어온 돈이다. 금액이 같으면 그걸 쓴다.
  const salarySet = salaryFor(mKey);
  const inRows = [];
  inRows.push(matched(leftIn, '월급', salarySet, '아직 입금 전'));
  // 마통 보충: 짝이 확인된 계좌 간 이동만 실제로 센다.
  const topupActual = topupFor(mKey);
  if (topupActual > 0) {
    // 실제 이동액은 위 매칭 풀에서도 빼둔다(같은 거래를 두 번 세지 않도록).
    take(leftIn, topupActual);
    inRows.push({ name: '마통에서', amount: topupActual, real: true, note: '실제 이동액' });
  } else if (cfg.topup > 0) {
    inRows.push({ name: '마통에서', amount: cfg.topup, real: false, note: '아직 안 옮김' });
  }
  cfg.income.forEach(i => inRows.push(matched(leftIn, i.name, i.amount || 0, '아직 입금 전')));
  ((cfg.extraIn && cfg.extraIn[mKey]) || [])
    .forEach(i => inRows.push(matched(leftIn, i.name, i.amount || 0, '아직 입금 전')));
  // 설정에 없는 실제 입금도 빠뜨리지 않는다.
  leftIn.forEach(t => inRows.push({
    name: '통장에서 · ' + (t.note || t.category), amount: t.amount, real: true, note: '' }));

  const inflow = inRows.reduce((s, r) => s + r.amount, 0);

  // ---- 카드값 (항상 명세서 실제) ----
  const cardRows = getMonthlyTxns(CARD_ACCOUNT, mKey).filter(t => t.type === 'expense');
  const isMine = t => NON_HOUSEHOLD_CATEGORIES.indexOf(t.category) === -1;
  const cardUse  = cardRows.filter(isMine).reduce((s,t) => s + t.amount, 0);
  const cardElse = cardRows.filter(t => !isMine(t)).reduce((s,t) => s + t.amount, 0);
  const byIssuer = {};
  cardRows.filter(isMine).forEach(t => {
    const k = t.issuer || '카드';
    byIssuer[k] = (byIssuer[k] || 0) + t.amount;
  });

  // ---- 고정 지출 · 기타 ----
  const fixed = cfg.fixed.map(i => matched(leftOut, i.name, i.amount || 0, '아직 안 빠짐'));
  const etc   = cfg.etc.map(i => matched(leftOut, i.name, i.amount || 0, '아직 안 빠짐'));
  // 설정에 없는 실제 통장 지출 — 기타로 모은다.
  leftOut.forEach(t => etc.push({
    name: '통장에서 · ' + (t.note || t.category), amount: t.amount, real: true, note: '' }));
  const fixedTotal = fixed.reduce((s,i) => s + i.amount, 0);
  const etcTotal   = etc.reduce((s,i) => s + i.amount, 0);

  // 카테고리별 — 카드 명세서 + 통장 실제 지출
  const byCat = {};
  bankOut.forEach(t => {
    const c = HOUSEHOLD_CATEGORIES.indexOf(t.category) === -1 ? '기타' : t.category;
    byCat[c] = (byCat[c] || 0) + t.amount;
  });
  cardRows.filter(isMine).forEach(t => {
    const c = HOUSEHOLD_CATEGORIES.indexOf(t.category) === -1 ? '기타' : t.category;
    byCat[c] = (byCat[c] || 0) + t.amount;
  });
  const bankSpend = bankOut.reduce((s,t) => s + t.amount, 0);

  const planned = inRows.concat(fixed, etc).filter(r => !r.real && r.amount).length;
  const spent   = fixedTotal + cardUse + etcTotal;
  // 나간 돈 중 거래내역으로 확인된 금액과, 아직 설정값인 금액
  const spentReal = cardUse +
    fixed.concat(etc).filter(r => r.real).reduce((s,r) => s + r.amount, 0);
  return { inRows, inflow, hasBank, planned, spentReal, spentPlanned: spent - spentReal,
           fixed, fixedTotal, etc, etcTotal, separate: cfg.separate,
           cardUse, cardElse, byIssuer, bankSpend, byCat, spent, left: inflow - spent };
}

function renderHousehold() {
  const mKey = monthKey(currentYear, currentMonth);

  // 시작월 이전은 숫자를 내지 않는다. 반쪽 데이터로 낸 숫자가 더 나쁘다.
  if (mKey < HOUSEHOLD_START_MONTH) {
    elOverview.style.display = 'none';
    elCatSection.style.display = 'none';
    elHouseStart.style.display = '';
    elHouseStart.innerHTML = '<b>' + HOUSEHOLD_START_MONTH.replace('-','년 ') + '월부터 정리합니다</b>' +
      currentYear + '년 ' + currentMonth + '월은 가계 집계 범위 밖입니다. ' +
      '이 달의 자금 흐름은 공금마통·차마통 탭에서 볼 수 있습니다.';
    return;
  }
  elOverview.style.display = '';
  elHouseStart.style.display = 'none';

  const h = householdTotals(mKey);

  elOvLeft.textContent = (h.left < 0 ? '-' : '') + fmtWon(h.left);
  elOvLeft.className   = 'ov-left-amt' + (h.left < 0 ? ' negative' : '');

  const won = n => fmtWon(n);
  const line = (name, amt, cls) =>
    '<div class="hs-row"><span class="hs-name">' + (name.indexOf('<button') >= 0 || name.indexOf('<i ') >= 0 ? name : escHtml(name)) + '</span>' +
    '<span class="hs-amt' + (cls ? ' ' + cls : '') + '">' + amt + '</span></div>';
  const sub = (amt, cls) =>
    '<div class="hs-sub"><span>소계</span><span class="' + (cls||'') + '">' + amt + '</span></div>';
  // 실제로 돈이 움직인 줄과, 아직 안 움직인 '예정' 줄을 구분해 보여준다.
  const tag = r => r.real ? '' : '<i class="hs-tag" title="' + escHtml(r.note || '예정') + '">예정</i>';
  const flowLine = (r, sign, cls, extra) =>
    line(escHtml(r.name) + (extra || '') + tag(r), sign + won(r.amount), cls);

  elHsIn.innerHTML =
    h.inRows.map((r, i) => flowLine(r, '+', 'income',
      r.name === '월급' ? ' <button class="hs-edit" data-edit="salary">수정</button>' : '')).join('') +
    sub('+' + won(h.inflow), 'income');

  elHsFixed.innerHTML = h.fixed.length
    ? h.fixed.map(r => flowLine(r, '-', 'expense')).join('') +
      sub('-' + won(h.fixedTotal), 'expense')
    : '<div class="hs-empty">등록된 고정 지출이 없습니다</div>';

  const issuers = Object.keys(h.byIssuer).sort((a,b) => h.byIssuer[b] - h.byIssuer[a]);
  elHsCard.innerHTML = (issuers.length
      ? issuers.map(k => line(k + '카드', '-' + won(h.byIssuer[k]), 'expense')).join('')
      : '<div class="hs-empty">이 달 카드 명세서가 없습니다</div>') +
    (h.cardElse ? line('(제외) 타인 부담 · 차마통 결제', won(h.cardElse), 'muted') : '') +
    sub('-' + won(h.cardUse), 'expense');

  elHsEtc.innerHTML = h.etc.length
    ? h.etc.map(r => flowLine(r, '-', 'expense')).join('') +
      sub('-' + won(h.etcTotal), 'expense')
    : '<div class="hs-empty">등록된 기타 항목이 없습니다</div>';

  // 별도 결제 건 — 참고만, 총계에 넣지 않는다
  elHsSepBox.style.display = h.separate.length ? '' : 'none';
  elHsSep.innerHTML = h.separate.map(i =>
    line(i.name, i.amount ? won(i.amount) : (i.note || '완납'), 'muted')).join('');

  elHsFormula.textContent =
    won(h.inflow) + ' − ' + won(h.fixedTotal) + ' − ' + won(h.cardUse) + ' − ' + won(h.etcTotal);

  // 예정이 섞여 있으면 숨기지 않고 적는다.
  elHouseFlow.style.display = h.planned ? '' : 'none';
  if (h.planned) {
    elHouseFlow.innerHTML = '<b>예정 ' + h.planned + '건이 섞여 있습니다</b>' +
      (h.hasBank
        ? '이 달 통장 내역에서 같은 금액을 찾지 못한 항목입니다 — 아직 안 빠졌거나 다른 계좌에서 나간 돈입니다.'
        : '이 달 통장 내역이 아직 들어오지 않아, 카드값만 실제 금액이고 나머지는 설정값입니다. 내역을 넣으면 자동으로 실제 금액으로 바뀝니다.');
  }

  const pct = h.inflow > 0 ? Math.min(100, Math.round(h.spent / h.inflow * 100)) : 0;
  elOvBar.style.width = pct + '%';
  elOvBar.className   = 'ov-bar-fill' + (pct >= 100 ? ' over' : pct >= 80 ? ' warn' : '');

  const now = new Date();
  if (now.getFullYear() === currentYear && now.getMonth() + 1 === currentMonth) {
    const daysLeft = lastDayOf(currentYear, currentMonth) - now.getDate() + 1;
    elOvDaily.textContent = h.left > 0
      ? '남은 ' + daysLeft + '일 · 하루 ' + won(Math.floor(h.left / daysLeft)) + ' 쓸 수 있음'
      : '예산 초과';
  } else {
    elOvDaily.textContent = h.inflow > 0 ? '들어온 돈의 ' + pct + '% 사용' : '';
  }

  // 나간 돈이 얼마나 실제 확인된 금액인지 그대로 적는다.
  if (h.spentPlanned > 0 && h.spent > 0) {
    elOvWarn.style.display = '';
    elOvWarn.textContent = '나간 돈 ' + won(h.spent) + ' 중 ' + won(h.spentReal) +
      '은 거래내역으로 확인, ' + won(h.spentPlanned) + '은 아직 설정값(예정)입니다';
  } else { elOvWarn.style.display = 'none'; }

  const prev = householdTotals(prevMonthKey());
  if (prev.spent === 0) { elOvDelta.textContent = ''; }
  else {
    const diff = h.spent - prev.spent;
    elOvDelta.textContent = '전월대비 ' + (diff >= 0 ? '+' : '-') + won(diff);
    elOvDelta.className = 'ov-delta' + (diff > 0 ? ' up' : ' down');
  }

  const catTotal = Object.keys(h.byCat).reduce((s,k) => s + h.byCat[k], 0);
  if (catTotal === 0) { elCatSection.style.display = 'none'; return; }
  elCatSection.style.display = '';
  el('categoryTotal').textContent = won(catTotal);
  elCatList.innerHTML = Object.keys(h.byCat)
    .map(c => ({ cat: c, amt: h.byCat[c] }))
    .sort((a,b) => b.amt - a.amt)
    .map(r => {
      const pp = Math.round(r.amt / catTotal * 100);
      return '<div class="cat-row"><div class="cat-head">' +
        '<span class="cat-name">' + escHtml(r.cat) + '</span>' +
        '<span class="cat-amt">' + won(r.amt) + '<span class="cat-pct">' + pp + '%</span></span></div>' +
        '<div class="cat-bar"><div class="cat-bar-fill" style="width:' + pp + '%"></div></div></div>';
    }).join('');
}

// 통장 탭: 이월 → 당월 입금 → 당월 출금(카드대금·이체·대차 전부) → 당월말 남은 잔액
function renderCashFlow(txns) {
  elCashFlow.style.display = ''; elCardFlow.style.display = 'none';

  const prevEnd = currentMonth === 1 ? monthEnd(currentYear-1, 12) : monthEnd(currentYear, currentMonth-1);
  const carry = balanceAsOf(currentAccount, prevEnd);
  const inAmt  = txns.filter(isInflow).reduce((s,t) => s + t.amount, 0);
  const outAmt = txns.filter(isOutflow).reduce((s,t) => s + t.amount, 0);
  const left   = balanceAsOf(currentAccount, monthEnd(currentYear, currentMonth));

  elCfCarry.textContent = (carry < 0 ? '-' : '') + fmtWon(carry);
  elCfCarry.className   = 'cf-amt' + (carry < 0 ? ' negative' : '');
  elCfIn.textContent    = '+' + fmtWon(inAmt);
  elCfOut.textContent   = '-' + fmtWon(outAmt);
  elCfLeft.textContent  = (left < 0 ? '-' : '') + fmtWon(left);
  elCfLeft.className    = 'cf-left-amt' + (left < 0 ? ' negative' : ' positive');
}

// 카드 탭: 잔액 개념이 없으니 '당월 사용액 = 다음 결제 예정액'을 보여준다
function renderCardFlow(txns) {
  elCashFlow.style.display = 'none'; elCardFlow.style.display = '';
  const use  = txns.filter(t => t.type === 'expense').reduce((s,t) => s + t.amount, 0);
  const prev = getMonthlyTxns(CARD_ACCOUNT, prevMonthKey()).filter(t => t.type === 'expense').reduce((s,t) => s + t.amount, 0);
  elCardUse.textContent  = fmtWon(use);
  elCardPrev.textContent = fmtWon(prev);

  // 카드 한 탭에 3장을 모았으니 카드사별 내림은 따로 보여준다.
  const byIssuer = {};
  txns.filter(t => t.type === 'expense').forEach(t => {
    const k = t.issuer || '미지정';
    byIssuer[k] = (byIssuer[k] || 0) + t.amount;
  });
  const keys = Object.keys(byIssuer).sort((a,b) => byIssuer[b] - byIssuer[a]);
  el('cardIssuers').innerHTML = keys.length <= 1 ? '' : keys.map(k =>
    '<div class="cf-row"><span class="cf-label">' + escHtml(k) + '</span>' +
    '<span class="cf-amt">' + fmtWon(byIssuer[k]) + '</span></div>').join('');
}

// 대차: 상대방별로 '내가 준 돈 - 받은 돈'을 모아 미정산 잔액을 낸다.
// (+)는 내가 받을 돈, (-)는 내가 줄 돈.
function debtByPeer() {
  const net = {}, log = {};
  BANK_ACCOUNTS.forEach(a => {
    getTransactions(a).forEach(t => {
      if (t.category !== DEBT_CATEGORY) return;
      const peer = t.peer || '기타';
      const sign = t.type === 'expense' ? 1 : -1;
      net[peer] = (net[peer] || 0) + sign * t.amount;
      (log[peer] = log[peer] || []).push(t);
    });
  });
  return Object.keys(net)
    .map(p => ({ peer: p, net: net[p], count: log[p].length }))
    .sort((a,b) => Math.abs(b.net) - Math.abs(a.net));
}

function renderDebt() {
  const rows = debtByPeer().filter(r => r.net !== 0 || r.count);
  if (rows.length === 0) { elDebtEmpty.style.display = ''; elDebtList.innerHTML = ''; return; }
  elDebtEmpty.style.display = 'none';
  const toGet = rows.filter(r => r.net > 0).reduce((s,r) => s + r.net, 0);
  const toPay = rows.filter(r => r.net < 0).reduce((s,r) => s - r.net, 0);
  elDebtList.innerHTML =
    '<div class="debt-total"><span>받을 돈 <b class="income">' + fmtWon(toGet) + '</b></span>' +
    '<span>줄 돈 <b class="expense">' + fmtWon(toPay) + '</b></span></div>' +
    rows.map(r =>
      '<div class="debt-row"><span class="debt-peer">' + escHtml(r.peer) +
      '<em>' + r.count + '건</em></span>' +
      '<span class="debt-amt ' + (r.net > 0 ? 'income' : r.net < 0 ? 'expense' : 'muted') + '">' +
        (r.net > 0 ? '받을 ' : r.net < 0 ? '줄 ' : '정산됨 ') + fmtWon(r.net) +
      '</span></div>').join('');
}

function renderCategories(txns) {
  const spending = txns.filter(isSpending);
  const total = spending.reduce((s,t) => s + t.amount, 0);
  if (total === 0) { elCatSection.style.display = 'none'; return; }
  elCatSection.style.display = '';

  const byCat = {};
  spending.forEach(t => { byCat[t.category] = (byCat[t.category] || 0) + t.amount; });
  const rows = Object.keys(byCat).map(c => ({ cat: c, amt: byCat[c] })).sort((a,b) => b.amt - a.amt);

  el('categoryTotal').textContent = fmtWon(total);
  elCatList.innerHTML = rows.map(r => {
    const pct = Math.round(r.amt / total * 100);
    return '<div class="cat-row">' +
      '<div class="cat-head"><span class="cat-name">' + escHtml(r.cat) + '</span>' +
      '<span class="cat-amt">' + fmtWon(r.amt) + '<span class="cat-pct">' + pct + '%</span></span></div>' +
      '<div class="cat-bar"><div class="cat-bar-fill" style="width:' + pct + '%"></div></div>' +
    '</div>';
  }).join('');
}

function renderList(txns) {
  const sorted = txns.slice().sort((a,b) => b.date.localeCompare(a.date) || b.createdAt - a.createdAt);
  Array.from(elTxnList.children).forEach(e => { if (e.id !== 'emptyState') e.remove(); });
  if (sorted.length === 0) { elEmptyState.style.display = ''; return; }
  elEmptyState.style.display = 'none';
  sorted.forEach(t => {
    const item = document.createElement('div');
    item.className = 'txn-item'; item.dataset.id = t.id;
    const inflow = t.type === 'income' || (t.type === 'transfer' && t.dir === 'in');
    const sign = (inflow !== (t.amount < 0)) ? '+' : '-';
    item.innerHTML =
      '<span class="txn-date">' + escHtml(fmtDate(t.date)) + '</span>' +
      '<div class="txn-body">' +
        '<span class="txn-note">' + escHtml(t.note || '(비고 없음)') + '</span>' +
        '<span class="txn-cat">' + escHtml(
            t.category
            + (t.type === 'transfer' ? (t.dir === 'in' ? ' · 받음' : ' · 보냄') : '')
            + (t.issuer ? ' · ' + t.issuer : '')
            + (t.peer ? ' · ' + t.peer : '')
            + (currentAccount === CARD_ACCOUNT && t.bm !== t.date.slice(0,7)
               ? ' · 이용 ' + t.date.slice(5).replace('-','.') : '')
          ) + '</span>' +
      '</div>' +
      '<span class="txn-amount ' + t.type + '">' + sign + fmtWon(t.amount) + '</span>' +
      '<button class="txn-del-btn" data-id="' + t.id + '" aria-label="삭제">&#10005;</button>';
    elTxnList.appendChild(item);
  });
}

function render() {
  elMonthLabel.textContent = currentYear + '년 ' + currentMonth + '월';
  if (currentAccount === 'house') { renderHousehold(); return; }
  if (currentAccount === 'debt')  { renderDebt(); return; }
  const txns = getMonthlyTxns();
  renderSummary(txns); renderCategories(txns); renderList(txns);
}

function setAccount(account) {
  currentAccount = account;
  Array.from(elTabs.children).forEach(b => b.classList.toggle('active', b.dataset.account === account));
  document.body.className = 'account-' + account;
  // 가계(월급 기준)와 대차는 계좌가 아니라 관점이다. 계좌용 영역을 상황에 맞게 숨긴다.
  const isDebt = account === 'debt', isHouse = account === 'house';
  elOverview.style.display  = isHouse ? '' : 'none';
  elHouseNote.style.display = isHouse ? '' : 'none';
  elHouseStart.style.display = 'none';
  elDebtPanel.style.display = isDebt ? '' : 'none';
  elCashFlow.style.display  = 'none';
  elCardFlow.style.display  = 'none';
  elCatSection.style.display = isDebt ? 'none' : '';
  elTxnList.style.display   = (isDebt || isHouse) ? 'none' : '';
  el('fabBtn').style.display = (isDebt || isHouse) ? 'none' : '';
  render();
}

elTabs.addEventListener('click', e => {
  const btn = e.target.closest('.tab-btn'); if (btn) setAccount(btn.dataset.account);
});
el('prevMonth').addEventListener('click', () => { currentMonth--; if (currentMonth<1){currentMonth=12;currentYear--;} render(); });
el('nextMonth').addEventListener('click', () => { currentMonth++; if (currentMonth>12){currentMonth=1;currentYear++;} render(); });

function setSegment(type) {
  selectedType = type;
  Array.from(elSegments.children).forEach(b => {
    const on = b.dataset.type === type;
    b.className = 'segment-btn' + (on ? ' active ' + type + '-active' : '');
  });
  elCategoryGroup.style.display = type === 'transfer' ? 'none' : '';
  elDirGroup.style.display = type === 'transfer' ? '' : 'none';
  if (type !== 'transfer') renderCategoryOptions(type);
  elBillGroup.style.display = (currentAccount === CARD_ACCOUNT && type === 'expense') ? '' : 'none';
}

function openModal() {
  elInputDate.value = new Date().toISOString().slice(0,10);
  elInputBill.value = monthKey(currentYear, currentMonth);
  elInputAmount.value = ''; elInputNote.value = '';
  setSegment('expense'); setDir('out');
  elModalOverlay.classList.remove('hidden');
  setTimeout(() => elInputAmount.focus(), 150);
}
function closeModal() { elModalOverlay.classList.add('hidden'); }

el('fabBtn').addEventListener('click', openModal);
el('modalClose').addEventListener('click', closeModal);
elModalOverlay.addEventListener('click', e => { if (e.target === elModalOverlay) closeModal(); });

elSegments.addEventListener('click', e => {
  const btn = e.target.closest('.segment-btn'); if (btn) setSegment(btn.dataset.type);
});

function setDir(dir) {
  selectedDir = dir;
  Array.from(elDirControl.children).forEach(b => {
    b.className = 'segment-btn' + (b.dataset.dir === dir ? ' active expense-active' : '');
  });
}
elDirControl.addEventListener('click', e => {
  const btn = e.target.closest('.segment-btn'); if (btn) setDir(btn.dataset.dir);
});

el('submitBtn').addEventListener('click', () => {
  const dateVal = elInputDate.value, amountStr = elInputAmount.value.trim();
  if (!dateVal) { elInputDate.focus(); return; }
  const amount = parseFloat(amountStr);
  if (!amountStr || isNaN(amount) || amount <= 0) { elInputAmount.focus(); return; }
  addTransaction(currentAccount, {
    id: uid(), type: selectedType, date: dateVal, amount,
    category: selectedType === 'transfer' ? TRANSFER_CATEGORY : elInputCategory.value,
    dir: selectedType === 'transfer' ? selectedDir : null,
    bm: (currentAccount === CARD_ACCOUNT && selectedType === 'expense' && elInputBill.value)
          ? elInputBill.value : dateVal.slice(0,7),
    note: elInputNote.value.trim(), createdAt: Date.now(),
  });
  closeModal(); render();
});

elTxnList.addEventListener('click', e => {
  const btn = e.target.closest('.txn-del-btn'); if (!btn) return;
  const txn = getTransactions(currentAccount).find(t => t.id === btn.dataset.id); if (!txn) return;
  removeTransaction(currentAccount, txn.id); render();
  pendingDelete = { txn, account: currentAccount };
  if (undoTimer) clearTimeout(undoTimer);
  showSnackbar('삭제됨', true);
  undoTimer = setTimeout(() => { pendingDelete = null; elSnackbar.classList.add('hidden'); }, 3000);
});

el('snackbarUndo').addEventListener('click', () => {
  if (!pendingDelete) return;
  clearTimeout(undoTimer);
  const { txn, account } = pendingDelete; pendingDelete = null;
  addTransaction(account, txn); elSnackbar.classList.add('hidden'); render();
});

function showSnackbar(msg, undoable) {
  elSnackbarMsg.textContent = msg;
  el('snackbarUndo').style.display = undoable ? '' : 'none';
  elSnackbar.classList.remove('hidden');
  if (!undoable) setTimeout(() => elSnackbar.classList.add('hidden'), 2500);
}

elHsIn.addEventListener('click', e => {
  if (!e.target.closest('[data-edit="salary"]')) return;
  const mKey = monthKey(currentYear, currentMonth);
  const cur = salaryFor(mKey);
  const input = prompt(mKey + ' 월급(수입 총액)을 입력하세요.\n비우면 기본값(' + fmtWon(loadSettings().salary) + ')으로 돌아갑니다.', cur);
  if (input === null) return;
  const s = loadSettings();
  if (input.trim() === '') { delete s.overrides[mKey]; }
  else {
    const n = parseInt(input.replace(/[^0-9]/g, ''), 10);
    if (!n) return;
    if (confirm('이 금액을 기본 월급으로도 쓸까요?\n확인=기본값까지 변경, 취소=' + mKey + '만 변경')) s.salary = n;
    else s.overrides[mKey] = n;
  }
  saveSettings(s); render();
});

/* ---------- 데이터 관리 (내보내기 / 가져오기 / 초기화) ---------- */

el('dataBtn').addEventListener('click', () => { elImportText.value = ''; elDataOverlay.classList.remove('hidden'); });
el('dataClose').addEventListener('click', () => elDataOverlay.classList.add('hidden'));
elDataOverlay.addEventListener('click', e => { if (e.target === elDataOverlay) elDataOverlay.classList.add('hidden'); });

el('exportBtn').addEventListener('click', () => {
  const out = { version: 1, exportedAt: new Date().toISOString(),
                settings: loadSettings(), accounts: {} };
  Object.keys(ACCOUNTS).forEach(a => { out.accounts[a] = getTransactions(a); });
  const blob = new Blob([JSON.stringify(out, null, 2)], { type: 'application/json' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'fintrack-' + new Date().toISOString().slice(0,10) + '.json';
  a.click(); URL.revokeObjectURL(a.href);
});

// {version,accounts:{gongeum:[...]}} 또는 [{account,date,type,amount,category,note}] 둘 다 받는다.
function parseImport(text) {
  const data = JSON.parse(text);
  // 월급·고정지출·기타처럼 거래가 아닌 설정도 같은 파일로 받는다.
  if (data && data.settings) {
    const cur = loadSettings(), inc = data.settings;
    ['salary','topup'].forEach(k => { if (typeof inc[k] === 'number') cur[k] = inc[k]; });
    ['income','fixed','etc','separate'].forEach(k => { if (Array.isArray(inc[k])) cur[k] = inc[k]; });
    if (inc.overrides && typeof inc.overrides === 'object') {
      Object.keys(inc.overrides).forEach(m => { cur.overrides[m] = inc.overrides[m]; });
    }
    if (inc.extraIn && typeof inc.extraIn === 'object') {
      Object.keys(inc.extraIn).forEach(m => { cur.extraIn[m] = inc.extraIn[m]; });
    }
    saveSettings(cur);
  }
  const buckets = {};
  Object.keys(ACCOUNTS).forEach(a => { buckets[a] = []; });
  if (Array.isArray(data)) {
    data.forEach(r => { const a = ACCOUNTS[r.account] ? r.account : currentAccount; buckets[a].push(r); });
  } else if (data && data.accounts === undefined && data.settings) {
    return buckets;   // 설정만 들어온 파일
  } else if (data && data.accounts) {
    Object.keys(data.accounts).forEach(a => {
      if (!ACCOUNTS[a]) throw new Error('알 수 없는 계좌: ' + a);
      buckets[a] = data.accounts[a] || [];
    });
  } else { throw new Error('형식을 알 수 없습니다'); }
  return buckets;
}

function doImport(text) {
  let buckets;
  try { buckets = parseImport(text); }
  catch (err) { showSnackbar('가져오기 실패: ' + err.message, false); return; }

  let added = 0, skipped = 0, bad = 0;
  Object.keys(buckets).forEach(acct => {
    const existing = getTransactions(acct);
    // 같은 건이 이미 저장된 '건수'만큼만 건너뛴다. 명세서에 2건이면 2건 다 들어가고,
    // 같은 파일을 다시 가져오면 0건 추가가 된다.
    const have = {};
    existing.forEach(t => { const k = txnKey(t); have[k] = (have[k] || 0) + 1; });
    buckets[acct].forEach(raw => {
      if (!raw || !/^\d{4}-\d{2}-\d{2}$/.test(String(raw.date)) || !(Math.abs(Number(raw.amount)) > 0)) { bad++; return; }
      const t = normalize(raw);
      if (!t.createdAt) t.createdAt = Date.now();
      const k = txnKey(t);
      if (have[k] > 0) { have[k]--; skipped++; return; }
      existing.push(t); added++;
    });
    saveData(acct, existing);
  });
  elDataOverlay.classList.add('hidden'); render();
  showSnackbar(added + '건 추가' + (skipped ? ' / 중복 ' + skipped + '건 제외' : '') + (bad ? ' / 오류 ' + bad + '건' : ''), false);
}

el('importBtn').addEventListener('click', () => {
  const text = elImportText.value.trim();
  if (!text) { elImportText.focus(); return; }
  doImport(text);
});
elImportFile.addEventListener('change', e => {
  const file = e.target.files && e.target.files[0]; if (!file) return;
  const reader = new FileReader();
  reader.onload = () => doImport(String(reader.result));
  reader.readAsText(file);
  e.target.value = '';
});

el('resetBtn').addEventListener('click', () => {
  if (!confirm('모든 계좌의 거래 내역을 전부 삭제합니다. 되돌릴 수 없습니다. 계속할까요?')) return;
  if (!confirm('마지막 확인입니다. 내보내기로 백업해두셨나요?')) return;
  Object.keys(ACCOUNTS).forEach(a => saveData(a, []));
  elDataOverlay.classList.add('hidden'); render();
  showSnackbar('전체 초기화 완료', false);
});

document.addEventListener('keydown', e => {
  if (e.key !== 'Escape') return;
  closeModal(); elDataOverlay.classList.add('hidden');
});

// 가계가 기본 탭이므로, 아직 시작월 전이면 시작월을 바로 띄운다.
if (monthKey(currentYear, currentMonth) < HOUSEHOLD_START_MONTH) {
  currentYear  = parseInt(HOUSEHOLD_START_MONTH.slice(0,4), 10);
  currentMonth = parseInt(HOUSEHOLD_START_MONTH.slice(5,7), 10);
}
renderCategoryOptions('expense');
setAccount('house');
