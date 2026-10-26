'use strict';

const ACCOUNTS = {
  gongeum: { key: 'fintrack_gongeum', label: '공금통장' },
  car:     { key: 'fintrack_car',     label: '자동차마통' },
  card:    { key: 'fintrack_card',    label: '카드' },
};

// 카테고리는 이 배열만 고치면 전체에 반영된다.
const CATEGORIES = [
  '식비', '생활비', '교통·차량', '주거·통신', '보험·세금', '의료',
  '경조사', '여행', '쇼핑', '취미·여가', '교육',
  '대출·이자', '투자', '대차(빌림·빌려줌)', '카드대금', '기타',
];
const TRANSFER_CATEGORY = '계좌이동';
// 지출(소비) 집계에서 빼는 카테고리. 잔액에는 그대로 반영된다.
//  - 카드대금: 카드 탭의 상세 N건과 이중 계상되므로 제외
//  - 대차·투자: 돈은 나가지만 소비가 아니므로 제외 ('이번달 얼마 썼나'를 정확히 보려고)
const EXCLUDED_FROM_SPENDING = ['카드대금', '대차(빌림·빌려줌)', '투자'];

let currentAccount = 'gongeum';
let currentYear    = new Date().getFullYear();
let currentMonth   = new Date().getMonth() + 1;
let selectedType   = 'expense';
let selectedDir    = 'out';
let pendingDelete  = null;
let undoTimer      = null;

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
    category: t.category || (type === 'transfer' ? TRANSFER_CATEGORY : '기타'),
    dir: type === 'transfer' ? (t.dir === 'in' ? 'in' : 'out') : null,
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
// 해당 날짜까지의 잔액. '당월말에 얼마 남았나'를 보려면 당월 말일로 끊어야 한다.
function balanceAsOf(account, dateStr) {
  return getTransactions(account)
    .filter(t => t.date <= dateStr)
    .reduce((s,t) => s + (isInflow(t) ? t.amount : -t.amount), 0);
}
function isSpending(t) { return t.type === 'expense' && EXCLUDED_FROM_SPENDING.indexOf(t.category) === -1; }
function txnKey(t) { return [t.date, t.type, t.dir, t.amount, t.category, t.note].join('|'); }

const el = id => document.getElementById(id);
const elMonthLabel   = el('monthLabel');
const elTabs         = el('accountTabs');
const elSumSpending  = el('sumSpending');
const elCashFlow     = el('cashFlow');
const elCardFlow     = el('cardFlow');
const elCfCarry      = el('cfCarry');
const elCfIn         = el('cfIn');
const elCfOut        = el('cfOut');
const elCfLeft       = el('cfLeft');
const elCardUse      = el('cardUse');
const elCardPrev     = el('cardPrev');
const elSpendDelta   = el('spendDelta');
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
const elDirGroup     = el('dirGroup');
const elDirControl   = el('dirControl');
const elInputNote    = el('inputNote');
const elSnackbar     = el('snackbar');
const elSnackbarMsg  = el('snackbarMsg');
const elDataOverlay  = el('dataOverlay');
const elImportText   = el('importText');
const elImportFile   = el('importFile');

function renderCategoryOptions() {
  elInputCategory.innerHTML = CATEGORIES
    .map(c => '<option value="' + escHtml(c) + '">' + escHtml(c) + '</option>').join('');
}

function getMonthlyTxns(account, mKey) {
  return getTransactions(account || currentAccount).filter(t => t.date.startsWith(mKey || monthKey(currentYear, currentMonth)));
}

function renderSummary(txns) {
  const spending = txns.filter(isSpending).reduce((s,t) => s + t.amount, 0);
  elSumSpending.textContent = fmtWon(spending);

  if (currentAccount === 'card') { renderCardFlow(txns); }
  else { renderCashFlow(txns); }

  const prev = getMonthlyTxns(currentAccount, prevMonthKey()).filter(isSpending).reduce((s,t) => s + t.amount, 0);
  if (prev === 0 && spending === 0) { elSpendDelta.textContent = ''; return; }
  if (prev === 0) { elSpendDelta.textContent = '전월 기록 없음'; elSpendDelta.className = 'spend-delta'; return; }
  const diff = spending - prev;
  const pct  = Math.round(Math.abs(diff) / prev * 100);
  elSpendDelta.textContent = '전월대비 ' + (diff >= 0 ? '+' : '-') + fmtWon(diff) + ' (' + pct + '%)';
  elSpendDelta.className = 'spend-delta' + (diff > 0 ? ' up' : diff < 0 ? ' down' : '');
}

// 통장 탭: 이월 → 당월 입금 → 당월 출금(카드대금·이체·대차 전부) → 당월말 남은 잔액
function renderCashFlow(txns) {
  elCashFlow.style.display = ''; elCardFlow.style.display = 'none';

  const prevEnd = currentMonth === 1 ? monthEnd(currentYear-1, 12) : monthEnd(currentYear, currentMonth-1);
  const carry = balanceAsOf(currentAccount, prevEnd);
  const inAmt  = txns.filter(isInflow).reduce((s,t) => s + t.amount, 0);
  const outAmt = txns.filter(isOutflow).reduce((s,t) => s + t.amount, 0);
  const left   = carry + inAmt - outAmt;

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
  const prev = getMonthlyTxns('card', prevMonthKey()).filter(t => t.type === 'expense').reduce((s,t) => s + t.amount, 0);
  elCardUse.textContent  = fmtWon(use);
  elCardPrev.textContent = fmtWon(prev);
}

function renderCategories(txns) {
  const spending = txns.filter(isSpending);
  const total = spending.reduce((s,t) => s + t.amount, 0);
  if (total === 0) { elCatSection.style.display = 'none'; return; }
  elCatSection.style.display = '';

  const byCat = {};
  spending.forEach(t => { byCat[t.category] = (byCat[t.category] || 0) + t.amount; });
  const rows = Object.keys(byCat).map(c => ({ cat: c, amt: byCat[c] })).sort((a,b) => b.amt - a.amt);

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
        '<span class="txn-cat">' + escHtml(t.category + (t.type === 'transfer' ? (t.dir === 'in' ? ' · 받음' : ' · 보냄') : '')) + '</span>' +
      '</div>' +
      '<span class="txn-amount ' + t.type + '">' + sign + fmtWon(t.amount) + '</span>' +
      '<button class="txn-del-btn" data-id="' + t.id + '" aria-label="삭제">&#10005;</button>';
    elTxnList.appendChild(item);
  });
}

function render() {
  elMonthLabel.textContent = currentYear + '년 ' + currentMonth + '월';
  const txns = getMonthlyTxns();
  renderSummary(txns); renderCategories(txns); renderList(txns);
}

function setAccount(account) {
  currentAccount = account;
  Array.from(elTabs.children).forEach(b => b.classList.toggle('active', b.dataset.account === account));
  document.body.className = 'account-' + account;
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
}

function openModal() {
  elInputDate.value = new Date().toISOString().slice(0,10);
  elInputAmount.value = ''; elInputNote.value = '';
  elInputCategory.value = CATEGORIES[0];
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

renderCategoryOptions();
setAccount('gongeum');
