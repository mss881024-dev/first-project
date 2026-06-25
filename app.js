'use strict';
const STORAGE_KEY = 'fintrack_transactions';
const CATEGORIES = {
  income:  ['Salary', 'Freelance', 'Investment', 'Gift', 'Refund', 'Other'],
  expense: ['Food & Drink', 'Housing', 'Transport', 'Shopping', 'Healthcare', 'Entertainment', 'Utilities', 'Other'],
};
const CATEGORY_ICONS = {
  'Salary': '💼', 'Freelance': '🖥️', 'Investment': '📈', 'Gift': '🎁',
  'Refund': '↩️', 'Food & Drink': '🍔', 'Housing': '🏠', 'Transport': '🚗',
  'Shopping': '🛍️', 'Healthcare': '💊', 'Entertainment': '🎬',
  'Utilities': '💡', 'Other': '📌',
};
function loadData() { try { return JSON.parse(localStorage.getItem(STORAGE_KEY)) || []; } catch { return []; } }
function saveData(data) { localStorage.setItem(STORAGE_KEY, JSON.stringify(data)); }
let transactions = loadData();
const elBalance      = document.getElementById('balance');
const elBalanceNote  = document.getElementById('balance-note');
const elIncome       = document.getElementById('total-income');
const elIncomeCount  = document.getElementById('income-count');
const elExpense      = document.getElementById('total-expense');
const elExpenseCount = document.getElementById('expense-count');
const elTxnList      = document.getElementById('txn-list');
const elEmptyState   = document.getElementById('empty-state');
const elFilterType   = document.getElementById('filter-type');
const elFilterCat    = document.getElementById('filter-category');
const elChart        = document.getElementById('chart');
const elChartEmpty   = document.getElementById('chart-empty');
const elToast        = document.getElementById('toast');
const elOverlay      = document.getElementById('modal-overlay');
const elForm         = document.getElementById('txn-form');
const elFDesc        = document.getElementById('f-desc');
const elFAmount      = document.getElementById('f-amount');
const elFType        = document.getElementById('f-type');
const elFCat         = document.getElementById('f-category');
const elFDate        = document.getElementById('f-date');
const elFormErr      = document.getElementById('form-error');
function fmt(n) { return '$' + Math.abs(n).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }); }
function fmtDate(iso) { const d = new Date(iso + 'T00:00:00'); return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }); }
function uid() { return Date.now().toString(36) + Math.random().toString(36).slice(2); }
function escHtml(s) { return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'); }
function showToast(msg, dur = 2400) {
  elToast.textContent = msg;
  elToast.classList.remove('hidden', 'fade-out');
  clearTimeout(showToast._t);
  showToast._t = setTimeout(() => { elToast.classList.add('fade-out'); setTimeout(() => elToast.classList.add('hidden'), 400); }, dur);
}
function populateCategorySelect(type, selectEl, selectedVal = '') {
  selectEl.innerHTML = '';
  CATEGORIES[type].forEach(c => { const o = document.createElement('option'); o.value = c; o.textContent = c; if (c === selectedVal) o.selected = true; selectEl.appendChild(o); });
}
function populateFilterCategories() {
  const current = elFilterCat.value;
  elFilterCat.innerHTML = '<option value="all">All Categories</option>';
  const seen = new Set();
  transactions.forEach(t => seen.add(t.category));
  seen.forEach(c => { const o = document.createElement('option'); o.value = c; o.textContent = c; if (c === current) o.selected = true; elFilterCat.appendChild(o); });
}
function updateSummary() {
  const incomes  = transactions.filter(t => t.type === 'income');
  const expenses = transactions.filter(t => t.type === 'expense');
  const totalIn  = incomes.reduce((s, t) => s + t.amount, 0);
  const totalEx  = expenses.reduce((s, t) => s + t.amount, 0);
  const balance  = totalIn - totalEx;
  elBalance.textContent = fmt(balance);
  elBalanceNote.textContent = balance >= 0 ? (transactions.length ? "You're in the green 🎉" : 'No transactions yet') : 'Spending exceeds income';
  elIncome.textContent = fmt(totalIn);
  elIncomeCount.textContent = `${incomes.length} transaction${incomes.length !== 1 ? 's' : ''}`;
  elExpense.textContent = fmt(totalEx);
  elExpenseCount.textContent = `${expenses.length} transaction${expenses.length !== 1 ? 's' : ''}`;
}
function renderList() {
  const typeFilter = elFilterType.value, catFilter = elFilterCat.value;
  let filtered = transactions.filter(t => {
    if (typeFilter !== 'all' && t.type !== typeFilter) return false;
    if (catFilter  !== 'all' && t.category !== catFilter) return false;
    return true;
  }).slice().sort((a, b) => b.date.localeCompare(a.date) || b.createdAt - a.createdAt);
  Array.from(elTxnList.querySelectorAll('.txn-item')).forEach(n => n.remove());
  if (filtered.length === 0) { elEmptyState.style.display = ''; return; }
  elEmptyState.style.display = 'none';
  filtered.forEach(t => {
    const icon = CATEGORY_ICONS[t.category] || '📌';
    const sign = t.type === 'income' ? '+' : '−';
    const item = document.createElement('div');
    item.className = 'txn-item'; item.dataset.id = t.id;
    item.innerHTML = `<div class="txn-icon ${t.type}">${icon}</div><div class="txn-body"><div class="txn-desc">${escHtml(t.description)}</div><div class="txn-meta">${escHtml(t.category)} · ${fmtDate(t.date)}</div></div><div class="txn-amount ${t.type}">${sign}${fmt(t.amount)}</div><button class="txn-delete" data-id="${t.id}" title="Delete">✕</button>`;
    elTxnList.appendChild(item);
  });
}
function renderChart() {
  if (transactions.length === 0) { elChart.style.display = 'none'; elChartEmpty.style.display = ''; return; }
  elChart.style.display = ''; elChartEmpty.style.display = 'none';
  const today = new Date(), days = [];
  for (let i = 29; i >= 0; i--) { const d = new Date(today); d.setDate(d.getDate() - i); days.push(d.toISOString().slice(0, 10)); }
  const sorted = transactions.slice().sort((a, b) => a.date.localeCompare(b.date));
  const windowStart = days[0]; let baseBalance = 0;
  sorted.forEach(t => { if (t.date < windowStart) baseBalance += t.type === 'income' ? t.amount : -t.amount; });
  const dayMap = {}; days.forEach(d => { dayMap[d] = 0; });
  sorted.forEach(t => { if (t.date >= windowStart && dayMap[t.date] !== undefined) dayMap[t.date] += t.type === 'income' ? t.amount : -t.amount; });
  const values = []; let running = baseBalance;
  days.forEach(d => { running += dayMap[d]; values.push(running); });
  const dpr = window.devicePixelRatio || 1, w = elChart.parentElement.clientWidth - 48, h = 160;
  elChart.width = w * dpr; elChart.height = h * dpr; elChart.style.width = w + 'px'; elChart.style.height = h + 'px';
  const ctx = elChart.getContext('2d'); ctx.scale(dpr, dpr);
  const pad = { top: 16, right: 16, bottom: 36, left: 60 };
  const cw = w - pad.left - pad.right, ch = h - pad.top - pad.bottom;
  const min = Math.min(...values), max = Math.max(...values), range = max - min || 1;
  const xOf = i => pad.left + (i / (values.length - 1)) * cw;
  const yOf = v => pad.top + ch - ((v - min) / range) * ch;
  ctx.strokeStyle = '#2e3350'; ctx.lineWidth = 1;
  for (let i = 0; i <= 4; i++) {
    const y = pad.top + (i / 4) * ch;
    ctx.beginPath(); ctx.moveTo(pad.left, y); ctx.lineTo(pad.left + cw, y); ctx.stroke();
    ctx.fillStyle = '#8892b0'; ctx.font = '10px system-ui'; ctx.textAlign = 'right';
    ctx.fillText('$' + (max - (i / 4) * range).toFixed(0), pad.left - 6, y + 4);
  }
  const grad = ctx.createLinearGradient(0, pad.top, 0, pad.top + ch);
  grad.addColorStop(0, 'rgba(99,102,241,.45)'); grad.addColorStop(1, 'rgba(99,102,241,0)');
  ctx.beginPath();
  values.forEach((v, i) => { i === 0 ? ctx.moveTo(xOf(i), yOf(v)) : ctx.lineTo(xOf(i), yOf(v)); });
  ctx.lineTo(xOf(values.length - 1), pad.top + ch); ctx.lineTo(xOf(0), pad.top + ch); ctx.closePath();
  ctx.fillStyle = grad; ctx.fill();
  ctx.beginPath();
  values.forEach((v, i) => { i === 0 ? ctx.moveTo(xOf(i), yOf(v)) : ctx.lineTo(xOf(i), yOf(v)); });
  ctx.strokeStyle = '#6366f1'; ctx.lineWidth = 2.5; ctx.lineJoin = 'round'; ctx.stroke();
  const step = Math.ceil(days.length / 6);
  ctx.fillStyle = '#8892b0'; ctx.font = '10px system-ui'; ctx.textAlign = 'center';
  days.forEach((d, i) => {
    if (i % step === 0 || i === days.length - 1) { const dt = new Date(d + 'T00:00:00'); ctx.fillText((dt.getMonth()+1)+'/'+dt.getDate(), xOf(i), h - 8); }
  });
  const last = values.length - 1;
  ctx.beginPath(); ctx.arc(xOf(last), yOf(values[last]), 5, 0, Math.PI * 2);
  ctx.fillStyle = '#6366f1'; ctx.fill(); ctx.strokeStyle = '#1a1d27'; ctx.lineWidth = 2; ctx.stroke();
}
function render() { updateSummary(); populateFilterCategories(); renderList(); renderChart(); }
function openModal() {
  elFDate.value = new Date().toISOString().slice(0, 10);
  populateCategorySelect(elFType.value, elFCat);
  elFormErr.classList.add('hidden'); elForm.reset();
  elFDate.value = new Date().toISOString().slice(0, 10);
  elOverlay.classList.remove('hidden'); elFDesc.focus();
}
function closeModal() { elOverlay.classList.add('hidden'); elForm.reset(); elFormErr.classList.add('hidden'); }
document.getElementById('btn-add-txn').addEventListener('click', openModal);
document.getElementById('btn-close-modal').addEventListener('click', closeModal);
document.getElementById('btn-cancel').addEventListener('click', closeModal);
elOverlay.addEventListener('click', e => { if (e.target === elOverlay) closeModal(); });
document.addEventListener('keydown', e => { if (e.key === 'Escape') closeModal(); });
elFType.addEventListener('change', () => { populateCategorySelect(elFType.value, elFCat); });
elForm.addEventListener('submit', e => {
  e.preventDefault();
  const desc = elFDesc.value.trim(), amount = parseFloat(elFAmount.value), type = elFType.value, cat = elFCat.value, date = elFDate.value;
  if (!desc || isNaN(amount) || amount <= 0 || !date) { elFormErr.classList.remove('hidden'); return; }
  elFormErr.classList.add('hidden');
  transactions.push({ id: uid(), description: desc, amount, type, category: cat, date, createdAt: Date.now() });
  saveData(transactions); render(); closeModal();
  showToast(`Transaction added: ${type === 'income' ? '+' : '−'}${fmt(amount)}`);
});
elTxnList.addEventListener('click', e => {
  const btn = e.target.closest('.txn-delete'); if (!btn) return;
  const txn = transactions.find(t => t.id === btn.dataset.id); if (!txn) return;
  if (!confirm(`Delete "${txn.description}"?`)) return;
  transactions = transactions.filter(t => t.id !== txn.id);
  saveData(transactions); render(); showToast('Transaction deleted.');
});
elFilterType.addEventListener('change', renderList);
elFilterCat.addEventListener('change', renderList);
window.addEventListener('resize', () => { if (transactions.length) renderChart(); });
render();