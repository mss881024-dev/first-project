'use strict';

// ── 상수 ─────────────────────────────────────────────────────────────────────

const STORAGE_KEYS = {
  gongeum: 'fintrack_gongeum',
  car:     'fintrack_car',
};

// ── 상태 ─────────────────────────────────────────────────────────────────────

let currentAccount = 'gongeum'; // 'gongeum' | 'car'
let currentYear    = new Date().getFullYear();
let currentMonth   = new Date().getMonth() + 1; // 1-12

let pendingDelete  = null; // { id, account }
let undoTimer      = null;

// ── 데이터 ───────────────────────────────────────────────────────────────────

function loadData(account) {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEYS[account])) || [];
  } catch {
    return [];
  }
}

function saveData(account, data) {
  localStorage.setItem(STORAGE_KEYS[account], JSON.stringify(data));
}

function getTransactions(account) {
  return loadData(account);
}

function addTransaction(account, txn) {
  const data = loadData(account);
  data.push(txn);
  saveData(account, data);
}

function removeTransaction(account, id) {
  const data = loadData(account).filter(t => t.id !== id);
  saveData(account, data);
}

function uid() {
  return Date.now().toString(36) + Math.random().toString(36).slice(2);
}

// ── 포맷 ─────────────────────────────────────────────────────────────────────

function fmtWon(n) {
  return '₩' + Math.abs(n).toLocaleString('ko-KR');
}

function fmtDate(iso) {
  // iso: YYYY-MM-DD → M.DD
  const parts = iso.split('-');
  const m = parseInt(parts[1], 10);
  const d = parts[2];
  return m + '.' + d;
}

function escHtml(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

// ── DOM Refs ──────────────────────────────────────────────────────────────────

const elMonthLabel     = document.getElementById('monthLabel');
const elPrevMonth      = document.getElementById('prevMonth');
const elNextMonth      = document.getElementById('nextMonth');
const elTabGongeum     = document.getElementById('tabGongeum');
const elTabCar         = document.getElementById('tabCar');
const elSumBalance     = document.getElementById('sumBalance');
const elSumIncome      = document.getElementById('sumIncome');
const elSumExpense     = document.getElementById('sumExpense');
const elTxnList        = document.getElementById('transactionList');
const elEmptyState     = document.getElementById('emptyState');
const elFabBtn         = document.getElementById('fabBtn');
const elModalOverlay   = document.getElementById('modalOverlay');
const elModalClose     = document.getElementById('modalClose');
const elSegIncome      = document.getElementById('segIncome');
const elSegExpense     = document.getElementById('segExpense');
const elInputDate      = document.getElementById('inputDate');
const elInputAmount    = document.getElementById('inputAmount');
const elInputNote      = document.getElementById('inputNote');
const elSubmitBtn      = document.getElementById('submitBtn');
const elSnackbar       = document.getElementById('snackbar');
const elSnackbarMsg    = document.getElementById('snackbarMsg');
const elSnackbarUndo   = document.getElementById('snackbarUndo');

// ── 렌더 ──────────────────────────────────────────────────────────────────────

function renderMonthLabel() {
  elMonthLabel.textContent = currentYear + '년 ' + currentMonth + '월';
}

function getMonthlyTxns() {
  const all = getTransactions(currentAccount);
  const prefix = currentYear + '-' + String(currentMonth).padStart(2, '0');
  return all.filter(t => t.date.startsWith(prefix));
}

function renderSummary(txns) {
  const income  = txns.filter(t => t.type === 'income').reduce((s, t) => s + t.amount, 0);
  const expense = txns.filter(t => t.type === 'expense').reduce((s, t) => s + t.amount, 0);
  const balance = income - expense;

  elSumBalance.textContent = fmtWon(balance);
  elSumBalance.className   = 'summary-value' + (balance >= 0 ? ' positive' : ' negative');
  elSumIncome.textContent  = fmtWon(income);
  elSumExpense.textContent = fmtWon(expense);
}

function renderList(txns) {
  // 날짜 오름차순
  const sorted = txns.slice().sort((a, b) => a.date.localeCompare(b.date) || a.createdAt - b.createdAt);

  // 기존 항목 제거 (emptyState 노드 제외)
  Array.from(elTxnList.children).forEach(el => {
    if (el.id !== 'emptyState') el.remove();
  });

  if (sorted.length === 0) {
    elEmptyState.style.display = '';
    return;
  }
  elEmptyState.style.display = 'none';

  sorted.forEach(t => {
    const item = document.createElement('div');
    item.className = 'txn-item';
    item.dataset.id = t.id;

    const sign = t.type === 'income' ? '+' : '-';
    item.innerHTML =
      '<span class="txn-date">' + escHtml(fmtDate(t.date)) + '</span>' +
      '<span class="txn-note">' + escHtml(t.note || '(비고 없음)') + '</span>' +
      '<span class="txn-amount ' + t.type + '">' + sign + fmtWon(t.amount) + '</span>' +
      '<button class="txn-del-btn" data-id="' + t.id + '" aria-label="삭제">&#10005;</button>';

    elTxnList.appendChild(item);
  });
}

function render() {
  renderMonthLabel();
  const txns = getMonthlyTxns();
  renderSummary(txns);
  renderList(txns);
}

// ── 탭 전환 ───────────────────────────────────────────────────────────────────

function setAccount(account) {
  currentAccount = account;

  elTabGongeum.classList.toggle('active', account === 'gongeum');
  elTabCar.classList.toggle('active', account === 'car');

  document.body.classList.remove('account-gongeum', 'account-car');
  document.body.classList.add('account-' + account);

  render();
}

// ── 월 이동 ───────────────────────────────────────────────────────────────────

elPrevMonth.addEventListener('click', () => {
  currentMonth--;
  if (currentMonth < 1) { currentMonth = 12; currentYear--; }
  render();
});

elNextMonth.addEventListener('click', () => {
  currentMonth++;
  if (currentMonth > 12) { currentMonth = 1; currentYear++; }
  render();
});

// ── 계좌 탭 ───────────────────────────────────────────────────────────────────

elTabGongeum.addEventListener('click', () => setAccount('gongeum'));
elTabCar.addEventListener('click',     () => setAccount('car'));

// ── 모달 ──────────────────────────────────────────────────────────────────────

let selectedType = 'expense'; // 기본값: 출금

function openModal() {
  elInputDate.value   = new Date().toISOString().slice(0, 10);
  elInputAmount.value = '';
  elInputNote.value   = '';
  setSegment('expense');
  elModalOverlay.classList.remove('hidden');
  setTimeout(() => elInputAmount.focus(), 150);
}

function closeModal() {
  elModalOverlay.classList.add('hidden');
}

function setSegment(type) {
  selectedType = type;
  elSegIncome.classList.remove('active', 'income-active', 'expense-active');
  elSegExpense.classList.remove('active', 'income-active', 'expense-active');

  if (type === 'income') {
    elSegIncome.classList.add('active', 'income-active');
  } else {
    elSegExpense.classList.add('active', 'expense-active');
  }
}

elFabBtn.addEventListener('click', openModal);
elModalClose.addEventListener('click', closeModal);
elModalOverlay.addEventListener('click', e => {
  if (e.target === elModalOverlay) closeModal();
});
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') closeModal();
});

elSegIncome.addEventListener('click',  () => setSegment('income'));
elSegExpense.addEventListener('click', () => setSegment('expense'));

elSubmitBtn.addEventListener('click', () => {
  const dateVal   = elInputDate.value;
  const amountStr = elInputAmount.value.trim();
  const note      = elInputNote.value.trim();

  if (!dateVal) {
    elInputDate.focus();
    return;
  }
  const amount = parseFloat(amountStr);
  if (!amountStr || isNaN(amount) || amount <= 0) {
    elInputAmount.focus();
    return;
  }

  const txn = {
    id:        uid(),
    type:      selectedType,
    date:      dateVal,
    amount:    amount,
    note:      note,
    createdAt: Date.now(),
  };

  addTransaction(currentAccount, txn);
  closeModal();
  render();
});

// ── 삭제 + 스낵바 (실행취소) ─────────────────────────────────────────────────

elTxnList.addEventListener('click', e => {
  const btn = e.target.closest('.txn-del-btn');
  if (!btn) return;

  const id = btn.dataset.id;
  const txns = getTransactions(currentAccount);
  const txn  = txns.find(t => t.id === id);
  if (!txn) return;

  // 즉시 제거 (로컬스토리지에서도)
  removeTransaction(currentAccount, id);
  render();

  // 취소용 보관
  pendingDelete = { txn, account: currentAccount };

  // 기존 타이머 해제
  if (undoTimer) clearTimeout(undoTimer);

  // 스낵바 표시
  elSnackbarMsg.textContent = '삭제됨';
  elSnackbar.classList.remove('hidden');

  // 3초 후 확정
  undoTimer = setTimeout(() => {
    pendingDelete = null;
    elSnackbar.classList.add('hidden');
  }, 3000);
});

elSnackbarUndo.addEventListener('click', () => {
  if (!pendingDelete) return;

  clearTimeout(undoTimer);
  const { txn, account } = pendingDelete;
  pendingDelete = null;

  // 복원
  addTransaction(account, txn);
  elSnackbar.classList.add('hidden');
  render();
});

// ── 초기화 ───────────────────────────────────────────────────────────────────

setAccount('gongeum');
