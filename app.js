'use strict';

const STORAGE_KEYS = {
  gongeum: 'fintrack_gongeum',
  car:     'fintrack_car',
};

let currentAccount = 'gongeum';
let currentYear    = new Date().getFullYear();
let currentMonth   = new Date().getMonth() + 1;
let pendingDelete  = null;
let undoTimer      = null;

function loadData(account) {
  try { return JSON.parse(localStorage.getItem(STORAGE_KEYS[account])) || []; }
  catch { return []; }
}
function saveData(account, data) { localStorage.setItem(STORAGE_KEYS[account], JSON.stringify(data)); }
function getTransactions(account) { return loadData(account); }
function addTransaction(account, txn) { const data = loadData(account); data.push(txn); saveData(account, data); }
function removeTransaction(account, id) { saveData(account, loadData(account).filter(t => t.id !== id)); }
function uid() { return Date.now().toString(36) + Math.random().toString(36).slice(2); }
function fmtWon(n) { return '₩' + Math.abs(n).toLocaleString('ko-KR'); }
function fmtDate(iso) { const p = iso.split('-'); return parseInt(p[1],10) + '.' + p[2]; }
function escHtml(s) { return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'); }

const elMonthLabel   = document.getElementById('monthLabel');
const elPrevMonth    = document.getElementById('prevMonth');
const elNextMonth    = document.getElementById('nextMonth');
const elTabGongeum   = document.getElementById('tabGongeum');
const elTabCar       = document.getElementById('tabCar');
const elSumBalance   = document.getElementById('sumBalance');
const elSumIncome    = document.getElementById('sumIncome');
const elSumExpense   = document.getElementById('sumExpense');
const elTxnList      = document.getElementById('transactionList');
const elEmptyState   = document.getElementById('emptyState');
const elFabBtn       = document.getElementById('fabBtn');
const elModalOverlay = document.getElementById('modalOverlay');
const elModalClose   = document.getElementById('modalClose');
const elSegIncome    = document.getElementById('segIncome');
const elSegExpense   = document.getElementById('segExpense');
const elInputDate    = document.getElementById('inputDate');
const elInputAmount  = document.getElementById('inputAmount');
const elInputNote    = document.getElementById('inputNote');
const elSubmitBtn    = document.getElementById('submitBtn');
const elSnackbar     = document.getElementById('snackbar');
const elSnackbarMsg  = document.getElementById('snackbarMsg');
const elSnackbarUndo = document.getElementById('snackbarUndo');

function renderMonthLabel() { elMonthLabel.textContent = currentYear + '년 ' + currentMonth + '월'; }

function getMonthlyTxns() {
  const prefix = currentYear + '-' + String(currentMonth).padStart(2,'0');
  return getTransactions(currentAccount).filter(t => t.date.startsWith(prefix));
}

function renderSummary(txns) {
  // 이번 달 입금/출금
  const income  = txns.filter(t => t.type === 'income').reduce((s, t) => s + t.amount, 0);
  const expense = txns.filter(t => t.type === 'expense').reduce((s, t) => s + t.amount, 0);
  // 전체 누적 잠액 (모든 달 합산)
  const all      = getTransactions(currentAccount);
  const totalIn  = all.filter(t => t.type === 'income').reduce((s, t) => s + t.amount, 0);
  const totalOut = all.filter(t => t.type === 'expense').reduce((s, t) => s + t.amount, 0);
  const balance  = totalIn - totalOut;

  elSumBalance.textContent = fmtWon(balance);
  elSumBalance.className   = 'summary-value' + (balance >= 0 ? ' positive' : ' negative');
  elSumIncome.textContent  = fmtWon(income);
  elSumExpense.textContent = fmtWon(expense);
}

function renderList(txns) {
  const sorted = txns.slice().sort((a,b) => a.date.localeCompare(b.date) || a.createdAt - b.createdAt);
  Array.from(elTxnList.children).forEach(el => { if (el.id !== 'emptyState') el.remove(); });
  if (sorted.length === 0) { elEmptyState.style.display = ''; return; }
  elEmptyState.style.display = 'none';
  sorted.forEach(t => {
    const item = document.createElement('div');
    item.className = 'txn-item'; item.dataset.id = t.id;
    const sign = t.type === 'income' ? '+' : '-';
    item.innerHTML =
      '<span class="txn-date">' + escHtml(fmtDate(t.date)) + '</span>' +
      '<span class="txn-note">' + escHtml(t.note || '(비고 없음)') + '</span>' +
      '<span class="txn-amount ' + t.type + '">' + sign + fmtWon(t.amount) + '</span>' +
      '<button class="txn-del-btn" data-id="' + t.id + '" aria-label="삭제">&#10005;</button>';
    elTxnList.appendChild(item);
  });
}

function render() { renderMonthLabel(); const txns = getMonthlyTxns(); renderSummary(txns); renderList(txns); }

function setAccount(account) {
  currentAccount = account;
  elTabGongeum.classList.toggle('active', account === 'gongeum');
  elTabCar.classList.toggle('active', account === 'car');
  document.body.classList.remove('account-gongeum','account-car');
  document.body.classList.add('account-' + account);
  render();
}

elPrevMonth.addEventListener('click', () => { currentMonth--; if (currentMonth<1){currentMonth=12;currentYear--;} render(); });
elNextMonth.addEventListener('click', () => { currentMonth++; if (currentMonth>12){currentMonth=1;currentYear++;} render(); });
elTabGongeum.addEventListener('click', () => setAccount('gongeum'));
elTabCar.addEventListener('click',     () => setAccount('car'));

let selectedType = 'expense';

function openModal() {
  elInputDate.value = new Date().toISOString().slice(0,10);
  elInputAmount.value = ''; elInputNote.value = '';
  setSegment('expense');
  elModalOverlay.classList.remove('hidden');
  setTimeout(() => elInputAmount.focus(), 150);
}
function closeModal() { elModalOverlay.classList.add('hidden'); }
function setSegment(type) {
  selectedType = type;
  elSegIncome.classList.remove('active','income-active','expense-active');
  elSegExpense.classList.remove('active','income-active','expense-active');
  if (type==='income') elSegIncome.classList.add('active','income-active');
  else elSegExpense.classList.add('active','expense-active');
}

elFabBtn.addEventListener('click', openModal);
elModalClose.addEventListener('click', closeModal);
elModalOverlay.addEventListener('click', e => { if (e.target===elModalOverlay) closeModal(); });
document.addEventListener('keydown', e => { if (e.key==='Escape') closeModal(); });
elSegIncome.addEventListener('click',  () => setSegment('income'));
elSegExpense.addEventListener('click', () => setSegment('expense'));

elSubmitBtn.addEventListener('click', () => {
  const dateVal = elInputDate.value, amountStr = elInputAmount.value.trim(), note = elInputNote.value.trim();
  if (!dateVal) { elInputDate.focus(); return; }
  const amount = parseFloat(amountStr);
  if (!amountStr || isNaN(amount) || amount <= 0) { elInputAmount.focus(); return; }
  addTransaction(currentAccount, { id: uid(), type: selectedType, date: dateVal, amount, note, createdAt: Date.now() });
  closeModal(); render();
});

elTxnList.addEventListener('click', e => {
  const btn = e.target.closest('.txn-del-btn'); if (!btn) return;
  const txns = getTransactions(currentAccount);
  const txn  = txns.find(t => t.id === btn.dataset.id); if (!txn) return;
  removeTransaction(currentAccount, txn.id); render();
  pendingDelete = { txn, account: currentAccount };
  if (undoTimer) clearTimeout(undoTimer);
  elSnackbarMsg.textContent = '삭제됨';
  elSnackbar.classList.remove('hidden');
  undoTimer = setTimeout(() => { pendingDelete = null; elSnackbar.classList.add('hidden'); }, 3000);
});

elSnackbarUndo.addEventListener('click', () => {
  if (!pendingDelete) return;
  clearTimeout(undoTimer);
  const { txn, account } = pendingDelete; pendingDelete = null;
  addTransaction(account, txn); elSnackbar.classList.add('hidden'); render();
});

function seedData() {
  const gongeumData = [
    { id: uid(), type: 'income',  date: '2026-06-01', amount: 1100000,  note: '공금',          createdAt: 1 },
    { id: uid(), type: 'expense', date: '2026-06-04', amount: 1114905,  note: '제주환불',       createdAt: 2 },
    { id: uid(), type: 'expense', date: '2026-06-12', amount: 170000,   note: '차입금원금상환', createdAt: 3 },
    { id: uid(), type: 'expense', date: '2026-06-15', amount: 100000,   note: '돌잔치',         createdAt: 4 },
    { id: uid(), type: 'expense', date: '2026-06-18', amount: 150000,   note: '상현이 빌려줘',  createdAt: 5 },
    { id: uid(), type: 'expense', date: '2026-06-18', amount: 7000,     note: '더로우 수수료',  createdAt: 6 },
    { id: uid(), type: 'expense', date: '2026-06-26', amount: 205000,   note: '자동차세',       createdAt: 7 },
    { id: uid(), type: 'expense', date: '2026-06-26', amount: 1114905,  note: '베트남경비',     createdAt: 8 },
    { id: uid(), type: 'income',  date: '2026-06-26', amount: 200000,   note: '차입금원금상환', createdAt: 9 },
  ];
  const carData = [
    { id: uid(), type: 'expense', date: '2026-04-25', amount: 27010069, note: '잠액',              createdAt: 1 },
    { id: uid(), type: 'expense', date: '2026-05-06', amount: 912000,   note: '자동차 원금',        createdAt: 2 },
    { id: uid(), type: 'expense', date: '2026-05-09', amount: 700000,   note: '상현이 빌림',        createdAt: 3 },
    { id: uid(), type: 'expense', date: '2026-05-15', amount: 135238,   note: '대출이자',           createdAt: 4 },
    { id: uid(), type: 'income',  date: '2026-05-18', amount: 10000000, note: '사업자대출',         createdAt: 5 },
    { id: uid(), type: 'income',  date: '2026-05-20', amount: 10000000, note: '사업자대출',         createdAt: 6 },
    { id: uid(), type: 'income',  date: '2026-05-21', amount: 10000000, note: '사업자대출',         createdAt: 7 },
    { id: uid(), type: 'income',  date: '2026-05-23', amount: 10000000, note: '사업자대출',         createdAt: 8 },
    { id: uid(), type: 'income',  date: '2026-05-25', amount: 700000,   note: '상현이 갚음',        createdAt: 9 },
    { id: uid(), type: 'expense', date: '2026-05-25', amount: 1000000,  note: '생활비',             createdAt: 10 },
    { id: uid(), type: 'income',  date: '2026-05-26', amount: 10000000, note: '사업자대출',         createdAt: 11 },
    { id: uid(), type: 'expense', date: '2026-05-28', amount: 5000000,  note: '이자 방어용 이동',   createdAt: 12 },
    { id: uid(), type: 'expense', date: '2026-06-04', amount: 700000,   note: '2년 뒤 갚을 예정',  createdAt: 13 },
    { id: uid(), type: 'expense', date: '2026-06-04', amount: 500000,   note: '8월에 갚을 예정',   createdAt: 14 },
    { id: uid(), type: 'expense', date: '2026-06-07', amount: 911828,   note: '자동차 원금',        createdAt: 15 },
    { id: uid(), type: 'income',  date: '2026-06-08', amount: 912000,   note: '자동차 원금',        createdAt: 16 },
    { id: uid(), type: 'expense', date: '2026-06-15', amount: 21482,    note: '대출이자',           createdAt: 17 },
    { id: uid(), type: 'expense', date: '2026-06-23', amount: 1065000,  note: '주식 구매',          createdAt: 18 },
    { id: uid(), type: 'income',  date: '2026-06-26', amount: 616200,   note: '차 마통 여행경비',   createdAt: 19 },
    { id: uid(), type: 'income',  date: '2026-06-26', amount: 50998,    note: '차 마통 여행경비 르모어', createdAt: 20 },
    { id: uid(), type: 'income',  date: '2026-06-26', amount: 1537652,  note: '차 마통 여행경비 퓨전', createdAt: 21 },
    { id: uid(), type: 'income',  date: '2026-06-26', amount: 50625,    note: '차 마통 여행경비 르모어', createdAt: 22 },
  ];
  const g = loadData('gongeum'), c = loadData('car');
  if (g.length === 0) saveData('gongeum', gongeumData);
  if (c.length === 0) saveData('car', carData);
}

seedData();
setAccount('gongeum');