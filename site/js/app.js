(function () {
  'use strict';
  var KEY = 'draftbanket_cart_v2';
  var products = ITEMS.filter(function (item) { return item.type === 'snack'; });
  var byId = Object.fromEntries(products.map(function (item) { return [item.id, item]; }));
  var cart = loadCart();
  var $ = function (id) { return document.getElementById(id); };
  var money = function (n) { return n.toLocaleString('ru-RU', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + ' BYN'; };
  var esc = function (s) { return String(s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); };

  function validQty(item, qty) { return Number.isInteger(qty) && qty >= item.minQty && (qty - item.minQty) % item.qtyStep === 0; }
  function loadCart() {
    try {
      var saved = JSON.parse(localStorage.getItem(KEY) || '{}');
      if (!saved.savedAt || Date.now() - saved.savedAt > 48 * 3600000) return {};
      var clean = {};
      Object.keys(saved.items || {}).forEach(function (id) {
        if (byId[id] && validQty(byId[id], saved.items[id])) clean[id] = saved.items[id];
      });
      return clean;
    } catch (_) { return {}; }
  }
  function saveCart() { try { localStorage.setItem(KEY, JSON.stringify({ savedAt: Date.now(), items: cart })); } catch (_) {} }
  function subtotal() { return Object.keys(cart).reduce(function (sum, id) { return sum + byId[id].price * cart[id]; }, 0); }
  function lineCount() { return Object.keys(cart).length; }
  function delivery() {
    var method = $('fulfillment').value;
    if (method === 'pickup') return 0;
    if (method === 'minsk') return subtotal() >= 500 ? 0 : 20;
    return null;
  }
  function changeQty(id, direction) {
    var item = byId[id]; if (!item) return;
    var current = cart[id] || 0;
    var next = direction === 'remove' ? 0 : current === 0 ? item.minQty : current + (direction === 'plus' ? item.qtyStep : -item.qtyStep);
    if (next < item.minQty) delete cart[id]; else cart[id] = next;
    saveCart(); render();
  }
  function control(id) {
    var item = byId[id], qty = cart[id] || 0;
    if (!qty) return '<button class="add-btn" data-action="plus" data-id="' + id + '">Добавить</button>';
    return '<div class="qty-stepper"><button data-action="minus" data-id="' + id + '" aria-label="Уменьшить">−</button><span>' + qty + '</span><button data-action="plus" data-id="' + id + '" aria-label="Увеличить">+</button></div>';
  }
  function renderCatalog() {
    var categories = CATEGORIES.filter(function (category) { return category.id !== 'sets'; });
    $('categoryNav').innerHTML = categories.map(function (c) { return '<a class="chip" href="#cat-' + c.id + '">' + esc(c.title) + '</a>'; }).join('');
    $('catalog').innerHTML = categories.map(function (category) {
      return '<section class="category-section" id="cat-' + category.id + '"><h2>' + esc(category.title) + '</h2><div class="grid">' + products.filter(function (item) { return item.category === category.id; }).map(function (item) {
        return '<article class="card"><div class="card-photo"><img src="' + item.img + '" alt="' + esc(item.name) + '" loading="lazy"></div><div class="card-body"><div class="card-name">' + esc(item.name) + '</div><div class="card-weight">' + esc(item.weight) + '</div><div class="card-desc">' + esc(item.description) + '</div><div class="card-composition">' + esc(item.composition) + '</div><div class="quantity-rule">От ' + item.minQty + ' шт., далее + ' + item.qtyStep + ' шт.</div><div class="card-footer"><div><div class="card-price">' + money(item.price) + ' / шт.</div><small>Минимум ' + money(item.price * item.minQty) + '</small></div><div class="card-action" data-control="' + item.id + '"></div></div></div></article>';
      }).join('') + '</div></section>';
    }).join('');
  }
  function renderCart() {
    var ids = Object.keys(cart);
    $('cartCount').hidden = ids.length === 0;
    $('cartCount').textContent = String(ids.length);
    $('cartFooter').hidden = ids.length === 0;
    $('cartBody').innerHTML = ids.length ? ids.map(function (id) {
      var item = byId[id], qty = cart[id];
      return '<div class="cart-line"><img src="' + item.img + '" alt=""><div class="cart-line-info"><div class="cart-line-name">' + esc(item.name) + '</div><div class="cart-line-price">' + money(item.price) + ' × ' + qty + ' = ' + money(item.price * qty) + '</div><div class="cart-line-controls">' + control(id) + '<button class="remove-btn" data-action="remove" data-id="' + id + '">Удалить</button></div></div></div>';
    }).join('') : '<div class="cart-empty">Корзина пока пуста.<br>Добавьте закуски из конструктора.</div>';
    $('cartTotal').textContent = money(subtotal());
    renderSummary();
  }
  function renderSummary() {
    var fee = delivery();
    $('checkoutSummary').innerHTML = '<div>Закуски: <strong>' + money(subtotal()) + '</strong></div><div>Доставка: <strong>' + (fee === null ? 'уточнит администратор' : money(fee)) + '</strong></div><div>Предварительный итог: <strong>' + (fee === null ? money(subtotal()) + ' + доставка' : money(subtotal() + fee)) + '</strong></div>';
  }
  function render() { document.querySelectorAll('[data-control]').forEach(function (el) { el.innerHTML = control(el.dataset.control); }); renderCart(); }
  function show(view) { ['viewCart', 'viewCheckout', 'viewSuccess'].forEach(function (id) { $(id).hidden = id !== view; }); }
  function open() { $('cartOverlay').classList.add('open'); document.body.style.overflow = 'hidden'; }
  function close() { $('cartOverlay').classList.remove('open'); document.body.style.overflow = ''; }
  function updateMethod() { $('fieldAddress').hidden = $('fulfillment').value === 'pickup'; renderSummary(); }
  function fieldValid(id, ok) { $(id).classList.toggle('invalid', !ok); return ok; }
  function validate() {
    var name = fieldValid('fieldName', $('customerName').value.trim().length >= 2);
    var digits = $('phone').value.replace(/\D/g, '');
    var phone = fieldValid('fieldPhone', digits.length >= 10 && digits.length <= 15);
    var day = $('eventDate').value;
    var date = fieldValid('fieldDate', !!day && day >= new Date().toISOString().slice(0, 10));
    var time = fieldValid('fieldTime', !!$('eventTime').value);
    var address = fieldValid('fieldAddress', $('fulfillment').value === 'pickup' || $('address').value.trim().length >= 3);
    return name && phone && date && time && address;
  }
  document.addEventListener('click', function (event) {
    var button = event.target.closest('[data-action]');
    if (button) changeQty(button.dataset.id, button.dataset.action);
  });
  $('cartOpenBtn').addEventListener('click', function () { show('viewCart'); open(); });
  document.querySelectorAll('[data-close-overlay]').forEach(function (el) { el.addEventListener('click', close); });
  $('toCheckoutBtn').addEventListener('click', function () { if (lineCount()) { show('viewCheckout'); updateMethod(); } });
  $('backToCartBtn').addEventListener('click', function () { show('viewCart'); });
  $('closeSuccessBtn').addEventListener('click', function () { close(); show('viewCart'); });
  $('fulfillment').addEventListener('change', updateMethod);
  $('eventDate').min = new Date().toISOString().slice(0, 10);
  $('submitOrderBtn').addEventListener('click', async function () {
    if (!lineCount() || !validate()) return;
    var button = this;
    var payload = {
      name: $('customerName').value.trim(), phone: $('phone').value.trim(), telegramNick: $('tgNick').value.trim(),
      eventDate: $('eventDate').value, eventTime: $('eventTime').value,
      fulfillment: $('fulfillment').value, address: $('address').value.trim(), comment: $('comment').value.trim(),
      items: Object.keys(cart).map(function (id) { return { id: id, quantity: cart[id] }; }),
      source: new URLSearchParams(location.search).get('utm_source') || 'site'
    };
    button.disabled = true; button.textContent = 'Отправляем…';
    try {
      var response = await fetch('/api/order', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
      if (!response.ok) throw new Error('request failed');
      cart = {}; saveCart(); render(); $('checkoutForm').reset(); updateMethod(); show('viewSuccess');
    } catch (_) { alert('Не удалось отправить заявку. Данные сохранены — попробуйте ещё раз позднее.'); }
    finally { button.disabled = false; button.textContent = 'Отправить заявку'; }
  });
  renderCatalog(); render(); updateMethod();
})();
