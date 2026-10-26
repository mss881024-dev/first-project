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
// 통장의 '카드대금' 출금은 카드 탭의 상세 N건과 이중 계상되므로 지출 집계에서 뺀다.
const EXCLUDED_FROM_SPENDING = ['카드대금'];

let currentAccount = 'gongeum';
let currentYear    = new Date().getFullYear();
let currentMonth   = new Date().getMonth() + 1;
let selectedType   = 'expense';
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
function isSpending(t) { return t.type === 'expense' && EXCLUDED_FROM_SPENDING.indexOf(t.category) === -1; }
function txnKey(t) { return [t.date, t.type, t.amount, t.category, t.note].join('|'); }

const el = id => document.getElementById(id);
const elMonthLabel   = el('monthLabel');
const elTabs         = el('accountTabs');
const elSumSpending  = el('sumSpending');
const elSumIncome    = el('sumIncome');
const elSumBalance   = el('sumBalance');
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
  const income   = txns.filter(t => t.type === 'income').reduce((s,t) => s + t.amount, 0);

  const all      = getTransactions(currentAccount);
  const totalIn  = all.filter(t => t.type === 'income').reduce((s,t) => s + t.amount, 0);
  const totalOut = all.filter(t => t.type === 'expense').reduce((s,t) => s + t.amount, 0);
  const balance  = totalIn - totalOut;

  elSumSpending.textContent = fmtWon(spending);
  elSumIncome.textContent   = fmtWon(income);
  elSumBalance.textContent  = fmtWon(balance);
  elSumBalance.className    = 'summary-value' + (balance >= 0 ? ' positive' : ' negative');

  const prev = getMonthlyTxns(currentAccount, prevMonthKey()).filter(isSpending).reduce((s,t) => s + t.amount, 0);
  if (prev === 0 && spending === 0) { elSpendDelta.textContent = ''; return; }
  if (prev === 0) { elSpendDelta.textContent = '전월 기록 없음'; elSpendDelta.className = 'spend-delta'; return; }
  const diff = spending - prev;
  const pct  = Math.round(Math.abs(diff) / prev * 100);
  elSpendDelta.textContent = '전월대비 ' + (diff >= 0 ? '+' : '-') + fmtWon(diff) + ' (' + pct + '%)';
  elSpendDelta.className = 'spend-delta' + (diff > 0 ? ' up' : diff < 0 ? ' down' : '');
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
    const sign = t.type === 'income' ? '+' : t.type === 'transfer' ? '' : '-';
    item.innerHTML =
      '<span class="txn-date">' + escHtml(fmtDate(t.date)) + '</span>' +
      '<div class="txn-body">' +
        '<span class="txn-note">' + escHtml(t.note || '(비고 없음)') + '</span>' +
        '<span class="txn-cat">' + escHtml(t.category) + '</span>' +
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
}

function openModal() {
  elInputDate.value = new Date().toISOString().slice(0,10);
  elInputAmount.value = ''; elInputNote.value = '';
  elInputCategory.value = CATEGORIES[0];
  setSegment('expense');
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

el('submitBtn').addEventListener('click', () => {
  const dateVal = elInputDate.value, amountStr = elInputAmount.value.trim();
  if (!dateVal) { elInputDate.focus(); return; }
  const amount = parseFloat(amountStr);
  if (!amountStr || isNaN(amount) || amount <= 0) { elInputAmount.focus(); return; }
  addTransaction(currentAccount, {
    id: uid(), type: selectedType, date: dateVal, amount,
    category: selectedType === 'transfer' ? TRANSFER_CATEGORY : elInputCategory.value,
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
    const seen = {};
    existing.forEach(t => { seen[txnKey(t)] = true; });
    buckets[acct].forEach(raw => {
      if (!raw || !/^\d{4}-\d{2}-\d{2}$/.test(String(raw.date)) || !(Math.abs(Number(raw.amount)) > 0)) { bad++; return; }
      const t = normalize(raw);
      if (!t.createdAt) t.createdAt = Date.now();
      const k = txnKey(t);
      if (seen[k]) { skipped++; return; }   // 같은 날짜·금액·내용은 중복으로 보고 건너뛴다
      seen[k] = true; existing.push(t); added++;
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
