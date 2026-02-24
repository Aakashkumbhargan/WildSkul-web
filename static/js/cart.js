// Simple INR formatter
const fmtINR = n => "₹" + Number(n || 0).toLocaleString("en-IN");

const cartBtn = document.getElementById('cartBtn');
const cartCount = document.getElementById('cartCount');
const cartOverlay = document.getElementById('cartOverlay');
const cartDrawer = document.getElementById('cartDrawer');
const cartItemsEl = document.getElementById('cartItems');
const cartSubtotalEl = document.getElementById('cartSubtotal');
const closeCartBtn = document.getElementById('closeCart');
const clearCartBtn = document.getElementById('clearCart');
const continueBtn = document.getElementById('continueBtn');
const checkoutBtn = document.getElementById('checkoutBtn');

function openCart(){
  document.body.classList.add('cart-open');
  cartOverlay.classList.add('show');
  cartDrawer.classList.add('open');
  cartDrawer.setAttribute('aria-hidden','false');
  cartOverlay.setAttribute('aria-hidden','false');
}
function closeCart(){
  document.body.classList.remove('cart-open');
  cartOverlay.classList.remove('show');
  cartDrawer.classList.remove('open');
  cartDrawer.setAttribute('aria-hidden','true');
  cartOverlay.setAttribute('aria-hidden','true');
}

cartBtn?.addEventListener('click', openCart);
closeCartBtn?.addEventListener('click', closeCart);
continueBtn?.addEventListener('click', closeCart);
cartOverlay?.addEventListener('click', closeCart);
document.addEventListener('keydown', e => { if(e.key === 'Escape') closeCart(); });

// API helpers
async function apiGetCart(){ const r = await fetch('/api/cart'); return r.json(); }
async function apiAdd(id, qty=1){
  const r = await fetch('/api/cart/add', { method:'POST', headers: { 'Content-Type':'application/json' }, body: JSON.stringify({ id, qty })});
  return r.json();
}
async function apiUpdate(id, qty){
  const r = await fetch('/api/cart/update', { method:'POST', headers: { 'Content-Type':'application/json' }, body: JSON.stringify({ id, qty })});
  return r.json();
}
async function apiRemove(id){ const r = await fetch(`/api/cart/remove/${id}`, { method:'DELETE' }); return r.json(); }
async function apiClear(){ const r = await fetch('/api/cart/clear', { method:'DELETE' }); return r.json(); }

function updateBadge(count){ if(!cartCount) return; cartCount.textContent = String(count || 0); }

function bindRowEvents(row){
  const id = row.dataset.id;
  row.querySelector('.inc')?.addEventListener('click', async ()=>{
    const qInput = row.querySelector('.q');
    const q = Math.max(1, Number(qInput.value || 1)) + 1;
    const data = await apiUpdate(id, q);
    renderCart(data);
  });
  row.querySelector('.dec')?.addEventListener('click', async ()=>{
    const qInput = row.querySelector('.q');
    const q = Math.max(1, Number(qInput.value || 1)) - 1;
    const data = await apiUpdate(id, q);
    renderCart(data);
  });
  row.querySelector('.q')?.addEventListener('change', async (e)=>{
    const q = Math.max(1, Number(e.target.value || 1));
    const data = await apiUpdate(id, q);
    renderCart(data);
  });
  row.querySelector('.remove')?.addEventListener('click', async ()=>{
    const data = await apiRemove(id);
    renderCart(data);
  });
}

function renderCart(data){
  if(!data){ return; }
  updateBadge(data.count);
  cartSubtotalEl.textContent = fmtINR(data.subtotal);

  if(!data.items || data.items.length === 0){
    cartItemsEl.innerHTML = '<div class="cart-empty">Your cart is empty.</div>';
    return;
  }

  cartItemsEl.innerHTML = data.items.map(it => `
    <div class="cart-item" data-id="${it.id}">
      <img class="cart-thumb" src="${it.image}" alt="${it.title}">
      <div>
        <p class="cart-title">${it.title}</p>
        <p class="cart-meta">${fmtINR(it.price)} · ${it.category || ''}</p>
        <div class="qty">
          <button class="dec" type="button">−</button>
          <input class="q" type="number" min="1" value="${it.qty}">
          <button class="inc" type="button">+</button>
        </div>
      </div>
      <div style="display:flex; flex-direction:column; align-items:end; gap:.4rem;">
        <strong>${fmtINR(it.price * it.qty)}</strong>
        <button class="btn danger remove" style="padding:.35rem .6rem; font-size:.85rem;" type="button">Remove</button>
      </div>
    </div>
  `).join('');

  cartItemsEl.querySelectorAll('.cart-item').forEach(bindRowEvents);
}

async function hydrateCart(){
  const data = await apiGetCart();
  renderCart(data);
}

function attachAddToCart(){
  document.querySelectorAll('.add-to-cart').forEach(btn=>{
    btn.addEventListener('click', async ()=>{
      const id = btn.dataset.id || btn.closest('.product-card')?.dataset.id;
      if(!id) return;
      const data = await apiAdd(id, 1);
      renderCart(data);
      openCart();
    });
  });
}

clearCartBtn?.addEventListener('click', async ()=>{
  const data = await apiClear();
  renderCart(data);
});

// Checkout button is an <a> now in base.html; leave nav to anchor.

(function init(){
  const y = document.getElementById('year'); if(y) y.textContent = new Date().getFullYear();
  attachAddToCart();
  hydrateCart();
})();