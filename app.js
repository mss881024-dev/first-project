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

      overrides: raw.overrides || {},
    };
  } catch { return { salary: DEFAULT_SALARY, topup: 0, overrides: {} }; }
}
function saveSettings(s) { localStorage.setItem(SETTINGS_KEY, JSON.stringify(s)); }
// 월급은 거래내역에서 뽑지 않는다 — 급여 계좌가 따로 있어서 이 계좌들에는 안 들어온다.
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
    amount: Math.abs(Number(t.amount) || 0),
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
const elOvIncome     = el('ovIncome');
const elOvCard       = el('ovCard');
const elOvBank       = el('ovBank');
const elOvOther      = el('ovOther');
const elOvOtherRow   = el('ovOtherRow');
const elOvOtherIn    = el('ovOtherIn');
const elOvInRow      = el('ovInRow');
const elOvBar        = el('ovBar');
const elOvDaily      = el('ovDaily');
const elOvDelta      = el('ovDelta');
const elOvWarn       = el('ovWarn');
const elOverview     = el('overview');
const elHouseNote    = el('houseNote');
const elOvElseRow    = el('ovElseRow');
const elOvElse       = el('ovElse');
const elOvSalaryEdit = el('ovSalaryEdit');
const elOvTopupRow   = el('ovTopupRow');
const elOvTopup      = el('ovTopup');
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

// 이번 달 전체(계좌 구분 없음): 수입을 총액으로 놓고 카드값·지출을 깎아 남은 금액을 낸다.
// 카드 사용액은 통장에서 다음 달에 빠지더라도 '이번 달에 쓴 돈'으로 보고 지금 차감한다.
// 그래서 통장의 '카드대금' 출금은 여기서 세지 않는다(이중 계상 방지).
function monthTotals(mKey) {
  let otherIncome = 0, bankSpend = 0, moved = 0, cardPaid = 0;
  const income = salaryFor(mKey);   // 월급은 급여 계좌로 들어오므로 설정값으로 대리한다
  const topup  = topupFor(mKey);    // 차마통에서 실제로 옮겨온 돈 (그 달치)
  [BUDGET_ACCOUNT].forEach(a => {
    getMonthlyTxns(a, mKey).forEach(t => {
      // 내 계좌끼리 옮긴 돈은 흐름이 두 번 찍히지만 실제로는 늘지도 줄지도 않는다.
      if (t.type === 'transfer') { moved += t.amount; return; }
      // 월급 외에 밖에서 들어온 돈(매각대금·보험만기·받은 돈 등)은 흐름이므로 더한다.
      if (t.type === 'income') { otherIncome += t.amount; return; }
      // 통장에서 빠진 카드대금은 카드 명세서 상세로 대체한다(이중 계상 방지).
      if (t.category === '카드대금') { cardPaid += t.amount; return; }
      bankSpend += t.amount;
    });
  });
  const cardUse = getMonthlyTxns(CARD_ACCOUNT, mKey)
    .filter(t => t.type === 'expense').reduce((s,t) => s + t.amount, 0);
  const spent = bankSpend + cardUse;
  return { income, topup, otherIncome, bankSpend, cardUse, cardPaid, moved, spent,
           left: income + topup + otherIncome - spent };
}

function renderOverview() {
  const mKey = monthKey(currentYear, currentMonth);
  const t = monthTotals(mKey);

  elOvLeft.textContent = (t.left < 0 ? '-' : '') + fmtWon(t.left);
  elOvLeft.className   = 'ov-left-amt' + (t.left < 0 ? ' negative' : '');
  elOvIncome.textContent = '+' + fmtWon(t.income);
  elOvSalaryEdit.dataset.month = mKey;
  elOvTopupRow.style.display = t.topup === 0 ? 'none' : '';
  elOvTopup.textContent = (t.topup < 0 ? '-' : '+') + fmtWon(t.topup);
  elOvTopup.className = 'ov-amt ' + (t.topup < 0 ? 'expense' : 'income');
  elOvCard.textContent   = '-' + fmtWon(t.cardUse);
  elOvBank.textContent   = '-' + fmtWon(t.bankSpend);
  elOvInRow.style.display = t.otherIncome === 0 ? 'none' : '';
  elOvOtherIn.textContent = '+' + fmtWon(t.otherIncome);
  elOvOtherRow.style.display = t.moved === 0 ? 'none' : '';
  elOvOther.textContent  = fmtWon(t.moved);

  const pool = t.income + t.topup + t.otherIncome;
  const pct  = pool > 0 ? Math.min(100, Math.round(t.spent / pool * 100)) : 0;
  elOvBar.style.width = pct + '%';
  elOvBar.className   = 'ov-bar-fill' + (pct >= 100 ? ' over' : pct >= 80 ? ' warn' : '');

  // 이번 달을 보고 있을 때만 '남은 일수 / 하루 가용액'을 띄운다.
  const now = new Date();
  if (now.getFullYear() === currentYear && now.getMonth() + 1 === currentMonth) {
    const daysLeft = lastDayOf(currentYear, currentMonth) - now.getDate() + 1;
    elOvDaily.textContent = t.left > 0
      ? '남은 ' + daysLeft + '일 · 하루 ' + fmtWon(Math.floor(t.left / daysLeft)) + ' 쓸 수 있음'
      : '예산 초과';
  } else {
    elOvDaily.textContent = pool > 0 ? '들어온 돈의 ' + pct + '% 사용' : '';
  }

  // 통장에서 빠진 카드대금과 명세서 청구합계가 맞는지 대사한다.
  // 안 맞으면 명세서가 덜 들어왔거나 청구월이 잘못 잡힌 것이다.
  if (t.cardPaid === 0 && t.cardUse === 0) { elOvWarn.style.display = 'none'; }
  else if (t.cardPaid === 0) { elOvWarn.style.display = ''; elOvWarn.textContent = '통장에 카드대금 출금이 없음 — 통장 내역 확인'; }
  else if (t.cardUse === 0) { elOvWarn.style.display = ''; elOvWarn.textContent = '카드 명세서 미적재 — 통장 카드대금 ' + fmtWon(t.cardPaid) + '만 있음'; }
  else if (t.cardPaid !== t.cardUse) {
    elOvWarn.style.display = '';
    elOvWarn.textContent = '불일치: 통장 카드대금 ' + fmtWon(t.cardPaid) + ' vs 명세서 ' + fmtWon(t.cardUse)
      + ' (차이 ' + fmtWon(t.cardPaid - t.cardUse) + ')';
  } else { elOvWarn.style.display = 'none'; }

  const prev = monthTotals(prevMonthKey());
  if (prev.spent === 0) { elOvDelta.textContent = ''; return; }
  const diff = t.spent - prev.spent;
  elOvDelta.textContent = '전월대비 ' + (diff >= 0 ? '+' : '-') + fmtWon(diff);
  elOvDelta.className = 'ov-delta' + (diff > 0 ? ' up' : ' down');
}

// 가계: 월급에서 가계 소비(카드값 + 생활비성 통장 지출)를 빼 남은 돈을 낸다.
// 마통 운용(사업자대출·차 구매·지인 대차·대출이자)과 계좌 간 이동은 범위 밖이다.
function householdTotals(mKey) {
  const salary = salaryFor(mKey);
  const cardRows = getMonthlyTxns(CARD_ACCOUNT, mKey).filter(t => t.type === 'expense');
  const isMine = t => NON_HOUSEHOLD_CATEGORIES.indexOf(t.category) === -1;
  const cardUse  = cardRows.filter(isMine).reduce((s,t) => s + t.amount, 0);
  const cardElse = cardRows.filter(t => !isMine(t)).reduce((s,t) => s + t.amount, 0);

  const byCat = {};
  let bankSpend = 0;
  getMonthlyTxns(BUDGET_ACCOUNT, mKey).forEach(t => {
    if (t.type !== 'expense') return;
    if (HOUSEHOLD_CATEGORIES.indexOf(t.category) === -1) return;
    bankSpend += t.amount;
    byCat[t.category] = (byCat[t.category] || 0) + t.amount;
  });
  cardRows.filter(isMine).forEach(t => {
    const c = HOUSEHOLD_CATEGORIES.indexOf(t.category) === -1 ? '기타' : t.category;
    byCat[c] = (byCat[c] || 0) + t.amount;
  });

  const spent = cardUse + bankSpend;
  return { salary, cardUse, cardElse, bankSpend, spent, byCat, left: salary - spent };
}

function renderHousehold() {
  const mKey = monthKey(currentYear, currentMonth);
  const h = householdTotals(mKey);

  elOvLeft.textContent = (h.left < 0 ? '-' : '') + fmtWon(h.left);
  elOvLeft.className   = 'ov-left-amt' + (h.left < 0 ? ' negative' : '');
  elOvIncome.textContent = '+' + fmtWon(h.salary);
  elOvCard.textContent   = '-' + fmtWon(h.cardUse);
  elOvBank.textContent   = '-' + fmtWon(h.bankSpend);
  elOvElseRow.style.display = h.cardElse === 0 ? 'none' : '';
  elOvElse.textContent   = fmtWon(h.cardElse);
  elOvSalaryEdit.dataset.month = mKey;

  const pct = h.salary > 0 ? Math.min(100, Math.round(h.spent / h.salary * 100)) : 0;
  elOvBar.style.width = pct + '%';
  elOvBar.className   = 'ov-bar-fill' + (pct >= 100 ? ' over' : pct >= 80 ? ' warn' : '');

  const now = new Date();
  if (now.getFullYear() === currentYear && now.getMonth() + 1 === currentMonth) {
    const daysLeft = lastDayOf(currentYear, currentMonth) - now.getDate() + 1;
    elOvDaily.textContent = h.left > 0
      ? '남은 ' + daysLeft + '일 · 하루 ' + fmtWon(Math.floor(h.left / daysLeft)) + ' 쓸 수 있음'
      : '월급 초과';
  } else {
    elOvDaily.textContent = h.salary > 0 ? '월급의 ' + pct + '% 사용' : '';
  }

  // 카드 명세서가 안 들어온 달은 카드값이 0으로 나와 남은 돈이 부풀려진다. 그걸 알린다.
  const cardPaid = getMonthlyTxns(BUDGET_ACCOUNT, mKey)
    .filter(t => t.type === 'expense' && t.category === '카드대금')
    .reduce((s,t) => s + t.amount, 0);
  const stmtTotal = h.cardUse + h.cardElse;   // 명세서 전체(대사는 이 금액으로)
  if (stmtTotal === 0 && cardPaid > 0) {
    elOvWarn.style.display = '';
    elOvWarn.textContent = '카드 명세서 미적재 — 통장에서 빠진 카드대금 ' + fmtWon(cardPaid) + '이 반영 안 됨';
  } else if (cardPaid > 0 && stmtTotal !== cardPaid) {
    elOvWarn.style.display = '';
    elOvWarn.textContent = '불일치: 통장 카드대금 ' + fmtWon(cardPaid) + ' vs 명세서 ' + fmtWon(stmtTotal);
  } else { elOvWarn.style.display = 'none'; }

  const prev = householdTotals(prevMonthKey());
  if (prev.spent === 0) { elOvDelta.textContent = ''; }
  else {
    const diff = h.spent - prev.spent;
    elOvDelta.textContent = '전월대비 ' + (diff >= 0 ? '+' : '-') + fmtWon(diff);
    elOvDelta.className = 'ov-delta' + (diff > 0 ? ' up' : ' down');
  }

  // 카테고리별
  const total = h.spent;
  if (total === 0) { elCatSection.style.display = 'none'; return; }
  elCatSection.style.display = '';
  el('categoryTotal').textContent = fmtWon(total);
  elCatList.innerHTML = Object.keys(h.byCat)
    .map(c => ({ cat: c, amt: h.byCat[c] }))
    .sort((a,b) => b.amt - a.amt)
    .map(r => {
      const p = Math.round(r.amt / total * 100);
      return '<div class="cat-row"><div class="cat-head">' +
        '<span class="cat-name">' + escHtml(r.cat) + '</span>' +
        '<span class="cat-amt">' + fmtWon(r.amt) + '<span class="cat-pct">' + p + '%</span></span></div>' +
        '<div class="cat-bar"><div class="cat-bar-fill" style="width:' + p + '%"></div></div></div>';
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
    const sign = t.type === 'income' || (t.type === 'transfer' && t.dir === 'in') ? '+' : '-';
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

elOvSalaryEdit.addEventListener('click', () => {
  const mKey = elOvSalaryEdit.dataset.month;
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
  const out = { version: 1, exportedAt: new Date().toISOString(), accounts: {} };
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
  const buckets = {};
  Object.keys(ACCOUNTS).forEach(a => { buckets[a] = []; });
  if (Array.isArray(data)) {
    data.forEach(r => { const a = ACCOUNTS[r.account] ? r.account : currentAccount; buckets[a].push(r); });
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

renderCategoryOptions('expense');
setAccount('house');
