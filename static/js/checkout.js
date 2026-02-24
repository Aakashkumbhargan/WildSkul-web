// function addToCart(product) {
//   const cart = JSON.parse(localStorage.getItem('ws_cart') || '[]');
//   const existing = cart.find(p => p.id === product.id);
//   if (existing) existing.qty += product.qty || 1;
//   else cart.push({...product, qty: product.qty || 1});
//   localStorage.setItem('ws_cart', JSON.stringify(cart));
// }
// ``

//     document.addEventListener("DOMContentLoaded", function () {
//       // If you store cart in localStorage, render it here
//       // Example expected structure:
//       // localStorage.setItem('ws_cart', JSON.stringify([{id: 'DUF-1', name: 'Duffel Bag', price: 1999, qty: 1, img: '/static/assets/Duffel_1.jpg'}]));
//       const cart = JSON.parse(localStorage.getItem('ws_cart') || '[]');
//       const cartEl = document.getElementById('cart-items');

//       if (cart.length) {
//         cartEl.innerHTML = '';
//         let subtotal = 0;
//         cart.forEach(item => {
//           subtotal += item.price * item.qty;
//           const row = document.createElement('div');
//           row.className = 'cart-row';
//           row.innerHTML = `
//             <img src="${item.img}" alt="${item.name}">
//             <div class="cart-info">
//               <h3>${item.name}</h3>
//               <p>Qty: ${item.qty}</p>
//               <p class="price">₹${(item.price * item.qty).toLocaleString('en-IN')}</p>
//             </div>
//           `;
//           cartEl.appendChild(row);
//         });
//         document.getElementById('subtotal').textContent = `₹${subtotal.toLocaleString('en-IN')}`;
//         const shipping = subtotal > 2499 ? 0 : 99;
//         document.getElementById('shipping').textContent = `₹${shipping.toLocaleString('en-IN')}`;
//         document.getElementById('grand-total').textContent = `₹${(subtotal + shipping).toLocaleString('en-IN')}`;
//       }

//       // Payment method toggling
//       const pmRadios = document.querySelectorAll('input[name="paymentMethod"]');
//       const upiPanel = document.getElementById('upi-panel');
//       const cardPanel = document.getElementById('card-panel');
//       pmRadios.forEach(r => {
//         r.addEventListener('change', () => {
//           const val = r.value;
//           upiPanel.classList.toggle('hidden', val !== 'upi');
//           cardPanel.classList.toggle('hidden', val !== 'card');
//         });
//       });

//       // Place order (demo handler)
//       const placeBtn = document.getElementById('place-order');
//       const statusEl = document.getElementById('order-status');
//       placeBtn.addEventListener('click', () => {
//         // Basic validation for shipping fields
//         const requiredIds = ['fullName','phone','addressLine1','city','state','pincode'];
//         const missing = requiredIds.filter(id => !document.getElementById(id).value.trim());
//         if (missing.length) {
//           statusEl.textContent = 'Please fill all required shipping fields.';
//           statusEl.className = 'order-status error';
//           return;
//         }

//         const pm = document.querySelector('input[name="paymentMethod"]:checked').value;
//         if (pm === 'upi' && !document.getElementById('upiId').value.trim()) {
//           statusEl.textContent = 'Please enter a valid UPI ID.';
//           statusEl.className = 'order-status error';
//           return;
//         }
//         if (pm === 'card' && (!document.getElementById('cardNumber').value.trim() || !document.getElementById('cvv').value.trim())) {
//           statusEl.textContent = 'Please enter card number and CVV.';
//           statusEl.className = 'order-status error';
//           return;
//         }

//         statusEl.textContent = 'Order placed! (Demo) — This will be replaced with real payment + backend order creation.';
//         statusEl.className = 'order-status success';

//         // Example: clear cart after order in demo
//         // localStorage.removeItem('ws_cart');
//       });
//     });
