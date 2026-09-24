(function () {
  'use strict';
  var KEY = 'draftbanket_cart_v2';
  var hiddenCategories = new Set(['profiteroles', 'sandwiches', 'burgers', 'quiches', 'cheesecakes']);
  var products = ITEMS.filter(function (item) {
    return item.type === 'ready-box' || (item.type === 'snack' && !hiddenCategories.has(item.category));
  });
  var byId = Object.fromEntries(products.map(function (item) { return [item.id, item]; }));
  var cart = loadCart();
  var $ = function (id) { return document.getElementById(id); };
  var money = function (n) { return n.toLocaleString('ru-RU', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + ' BYN'; };
  var shortMoney = function (n) { return n.toLocaleString('ru-RU', { minimumFractionDigits: Number.isInteger(n) ? 0 : 2, maximumFractionDigits: 2 }) + ' BYN'; };
  var esc = function (s) { return String(s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); };

  function validQty(item, qty) { return item.available !== false && Number.isInteger(qty) && qty >= item.minQty && (qty - item.minQty) % item.qtyStep === 0; }
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
  function lineTotal(item, qty) { return item.bundlePrice ? item.bundlePrice * qty / item.minQty : item.price * qty; }
  function subtotal() { return Object.keys(cart).reduce(function (sum, id) { return sum + lineTotal(byId[id], cart[id]); }, 0); }
  function lineCount() { return Object.keys(cart).length; }
  var GIFT_THRESHOLD = 200;
  var BIRTHDAY_DISCOUNT_RATE = 0.10;
  var GIFT_ITEM_ID = 'box-profiteroles-mini';
  function giftItem() { return byId[GIFT_ITEM_ID]; }
  // Promos don't stack: the gift box only shows when the birthday discount is not selected.
  function giftEligible() { return subtotal() >= GIFT_THRESHOLD && !!giftItem() && !birthdayChecked(); }
  function birthdayChecked() { var box = $('birthdayDiscount'); return !!(box && box.checked); }
  function discountAmount() { return birthdayChecked() ? Math.round(subtotal() * BIRTHDAY_DISCOUNT_RATE * 100) / 100 : 0; }
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
    if (item.available === false) return '<button class="add-btn" type="button" disabled>Цена уточняется</button>';
    if (!qty) return '<button class="add-btn" data-action="plus" data-id="' + id + '">Добавить</button>';
    return '<div class="qty-stepper"><button data-action="minus" data-id="' + id + '" aria-label="Уменьшить">−</button><span>' + qty + '</span><button data-action="plus" data-id="' + id + '" aria-label="Увеличить">+</button></div>';
  }
  function itemUnit(item, qty) {
    if (item.priceUnit === 'кг') return 'кг';
    if (item.priceUnit === 'чизкейк') {
      var cakeMod10 = qty % 10, cakeMod100 = qty % 100;
      if (cakeMod10 === 1 && cakeMod100 !== 11) return 'чизкейк';
      if (cakeMod10 >= 2 && cakeMod10 <= 4 && (cakeMod100 < 12 || cakeMod100 > 14)) return 'чизкейка';
      return 'чизкейков';
    }
    if (item.priceUnit === 'пирог') {
      var pieMod10 = qty % 10, pieMod100 = qty % 100;
      if (pieMod10 === 1 && pieMod100 !== 11) return 'пирог';
      if (pieMod10 >= 2 && pieMod10 <= 4 && (pieMod100 < 12 || pieMod100 > 14)) return 'пирога';
      return 'пирогов';
    }
    if (item.priceUnit !== 'рулет') return 'шт.';
    var mod10 = qty % 10, mod100 = qty % 100;
    if (mod10 === 1 && mod100 !== 11) return 'рулет';
    if (mod10 >= 2 && mod10 <= 4 && (mod100 < 12 || mod100 > 14)) return 'рулета';
    return 'рулетов';
  }
  function priceSummary(item) {
    if (item.available === false) return '<div class="card-price">Цена уточняется</div>';
    var qty = cart[item.id] || item.minQty;
    var singleUnit = item.priceUnit || 'шт.';
    return '<div class="card-price">' + shortMoney(lineTotal(item, qty)) + ' / ' + qty + ' ' + itemUnit(item, qty) + '</div><small>' + shortMoney(item.price) + ' за 1 ' + singleUnit + '</small>';
  }
  function renderCatalog() {
    var categories = CATEGORIES.filter(function (category) { return category.id !== 'sets' && !hiddenCategories.has(category.id); });
    $('categoryNav').innerHTML = '<a class="chip" href="#ready-boxes">Готовые боксы</a>' + categories.map(function (c) { return '<a class="chip" href="#cat-' + c.id + '">' + esc(c.title) + '</a>'; }).join('');
    $('catalog').innerHTML = categories.map(function (category) {
      return '<section class="category-section" id="cat-' + category.id + '"><h2>' + esc(category.title) + '</h2><div class="grid">' + products.filter(function (item) { return item.type === 'snack' && item.category === category.id; }).map(function (item) {
        if (['bruschette', 'rolls', 'croissants', 'crostini', 'biscuit-rolls', 'salads', 'tartlets', 'desserts', 'pies', 'napoleons'].indexOf(item.category) !== -1) {
          var note = item.note ? '<div class="card-weight">' + esc(item.note) + '</div>' : '';
          var orderText = item.orderLabel || (item.qtyStep === item.minQty
            ? 'Заказ кратно ' + item.minQty + ' шт.'
            : 'Минимум ' + item.minQty + ' шт., далее по ' + item.qtyStep + ' шт.');
          var orderNote = item.hideOrderLabel ? '' : '<div class="quantity-rule">' + esc(orderText) + '</div>';
          var weight = item.weight ? '<div class="card-weight">Вес: ' + esc(item.weight) + '</div>' : '';
          return '<article class="card card-simple"><div class="card-photo"><img src="' + item.img + '" alt="' + esc(item.name) + '" loading="lazy"></div><div class="card-body"><div class="card-name">' + esc(item.name) + '</div>' + weight + note + orderNote + '<div class="card-footer"><div class="card-price-block" data-price-summary="' + item.id + '">' + priceSummary(item) + '</div><div class="card-action" data-control="' + item.id + '"></div></div></div></article>';
        }
        return '<article class="card"><div class="card-photo"><img src="' + item.img + '" alt="' + esc(item.name) + '" loading="lazy"></div><div class="card-body"><div class="card-name">' + esc(item.name) + '</div><div class="card-weight">' + esc(item.weight) + '</div><div class="card-desc">' + esc(item.description) + '</div><div class="card-composition">' + esc(item.composition) + '</div><div class="quantity-rule">От ' + item.minQty + ' шт., далее + ' + item.qtyStep + ' шт.</div><div class="card-footer"><div><div class="card-price">' + money(item.price) + ' / шт.</div><small>Минимум ' + money(item.price * item.minQty) + '</small></div><div class="card-action" data-control="' + item.id + '"></div></div></div></article>';
      }).join('') + '</div></section>';
    }).join('');
  }
  function renderCart() {
    var ids = Object.keys(cart);
    $('cartCount').hidden = ids.length === 0;
    $('cartCount').textContent = String(ids.length);
    $('cartFooter').hidden = ids.length === 0;
    var giftBanner = giftEligible() ? '<div class="cart-line cart-line-gift"><img src="' + giftItem().img + '" alt=""><div class="cart-line-info"><div class="cart-gift-row"><div class="cart-line-name">' + esc(giftItem().name) + '</div><span class="cart-gift-tag">В подарок</span></div><div class="cart-line-price"><span class="cart-gift-strike">' + money(giftItem().price) + '</span>Бесплатно</div></div></div>' : '';
    $('cartBody').innerHTML = (ids.length ? ids.map(function (id) {
      var item = byId[id], qty = cart[id];
      return '<div class="cart-line"><img src="' + item.img + '" alt=""><div class="cart-line-info"><div class="cart-line-name">' + esc(item.name) + '</div><div class="cart-line-price">' + money(item.price) + ' × ' + qty + ' = ' + money(lineTotal(item, qty)) + '</div><div class="cart-line-controls">' + control(id) + '<button class="remove-btn" data-action="remove" data-id="' + id + '">Удалить</button></div></div></div>';
    }).join('') : '<div class="cart-empty">Корзина пока пуста.<br>Добавьте готовый бокс или закуски из конструктора.</div>') + giftBanner;
    $('cartTotal').textContent = money(subtotal());
    renderSummary();
  }
  function renderSummary() {
    var fee = delivery();
    var sub = subtotal();
    var discount = discountAmount();
    var afterDiscount = sub - discount;
    var promoNote = $('promoNote');
    if (promoNote) promoNote.hidden = sub < GIFT_THRESHOLD;
    var html = '<div>Закуски: <strong>' + money(sub) + '</strong></div>';
    if (discount > 0) html += '<div class="summary-discount">Скидка ко дню рождения (−10%): <strong>−' + money(discount) + '</strong></div>';
    html += '<div>Доставка: <strong>' + (fee === null ? 'уточнит администратор' : money(fee)) + '</strong></div>';
    if (giftEligible()) html += '<div class="summary-gift"><img src="' + giftItem().img + '" alt=""><div class="summary-gift-text"><div class="cart-gift-row"><strong>' + esc(giftItem().name) + '</strong><span class="cart-gift-tag">В подарок</span></div><span><span class="cart-gift-strike">' + money(giftItem().price) + '</span>Бесплатно</span></div></div>';
    html += '<div>Предварительный итог: <strong>' + (fee === null ? money(afterDiscount) + ' + доставка' : money(afterDiscount + fee)) + '</strong></div>';
    $('checkoutSummary').innerHTML = html;
  }
  function render() {
    document.querySelectorAll('[data-control]').forEach(function (el) { el.innerHTML = control(el.dataset.control); });
    document.querySelectorAll('[data-price-summary]').forEach(function (el) {
      var item = byId[el.dataset.priceSummary];
      if (item) el.innerHTML = priceSummary(item);
    });
    renderCart();
  }
  function show(view) { ['viewCart', 'viewCheckout', 'viewSuccess'].forEach(function (id) { $(id).hidden = id !== view; }); }
  function open() { $('cartOverlay').classList.add('open'); document.body.style.overflow = 'hidden'; }
  function close() { $('cartOverlay').classList.remove('open'); document.body.style.overflow = ''; }
  function closeMenu() {
    $('mobileMenu').hidden = true;
    $('menuToggle').setAttribute('aria-expanded', 'false');
    $('menuToggle').setAttribute('aria-label', 'Открыть меню');
  }
  function toggleMenu() {
    var willOpen = $('mobileMenu').hidden;
    $('mobileMenu').hidden = !willOpen;
    $('menuToggle').setAttribute('aria-expanded', String(willOpen));
    $('menuToggle').setAttribute('aria-label', willOpen ? 'Закрыть меню' : 'Открыть меню');
  }
  function updateMethod() { $('fieldAddress').hidden = $('fulfillment').value === 'pickup'; renderSummary(); }
  function fieldValid(id, ok) { $(id).classList.toggle('invalid', !ok); return ok; }
  function validate() {
    var name = fieldValid('fieldName', $('customerName').value.trim().length >= 2);
    var digits = $('phone').value.replace(/\D/g, '');
    var phone = fieldValid('fieldPhone', digits.length >= 10 && digits.length <= 15);
    var day = $('eventDate').value;
    var date = fieldValid('fieldDate', !!day && day >= new Date().toISOString().slice(0, 10));
    var address = fieldValid('fieldAddress', $('fulfillment').value === 'pickup' || $('address').value.trim().length >= 3);
    return name && phone && date && address;
  }
  document.addEventListener('click', function (event) {
    if (event.target.closest('[data-telegram-placeholder]')) {
      event.preventDefault();
      return;
    }
    var galleryButton = event.target.closest('[data-gallery-prev], [data-gallery-next]');
    if (galleryButton) {
      var gallery = galleryButton.closest('[data-gallery]');
      var track = gallery.querySelector('.ready-box-gallery-track');
      track.scrollBy({ left: track.clientWidth * (galleryButton.hasAttribute('data-gallery-next') ? 1 : -1), behavior: 'smooth' });
      return;
    }
    var button = event.target.closest('[data-action]');
    if (button) changeQty(button.dataset.id, button.dataset.action);
  });
  document.querySelectorAll('[data-gallery]').forEach(function (gallery) {
    var track = gallery.querySelector('.ready-box-gallery-track');
    var dots = gallery.querySelectorAll('.gallery-dots span');
    track.addEventListener('scroll', function () {
      var active = Math.round(track.scrollLeft / Math.max(track.clientWidth, 1));
      dots.forEach(function (dot, index) { dot.classList.toggle('active', index === active); });
    }, { passive: true });
  });
  var promoCarousel = document.querySelector('[data-promo-carousel]');
  if (promoCarousel) {
    var promoSlides = Array.from(promoCarousel.querySelectorAll('[data-promo-slide]'));
    var promoDots = Array.from(promoCarousel.querySelectorAll('[data-promo-dot]'));
    var promoIndex = 0;
    var promoTimer;
    function showPromo(index) {
      promoIndex = (index + promoSlides.length) % promoSlides.length;
      promoSlides.forEach(function (slide, slideIndex) {
        var active = slideIndex === promoIndex;
        slide.classList.toggle('active', active);
        slide.setAttribute('aria-hidden', String(!active));
      });
      promoDots.forEach(function (dot, dotIndex) {
        var active = dotIndex === promoIndex;
        dot.classList.toggle('active', active);
        dot.setAttribute('aria-current', String(active));
      });
    }
    function startPromoRotation() {
      window.clearInterval(promoTimer);
      promoTimer = window.setInterval(function () { showPromo(promoIndex + 1); }, 6000);
    }
    promoDots.forEach(function (dot) {
      dot.addEventListener('click', function () { showPromo(Number(dot.dataset.promoDot)); startPromoRotation(); });
    });
    var promoTouchStartX = 0;
    var promoTouchStartY = 0;
    promoCarousel.addEventListener('touchstart', function (event) {
      var touch = event.changedTouches[0];
      promoTouchStartX = touch.clientX;
      promoTouchStartY = touch.clientY;
    }, { passive: true });
    promoCarousel.addEventListener('touchend', function (event) {
      var touch = event.changedTouches[0];
      var deltaX = touch.clientX - promoTouchStartX;
      var deltaY = touch.clientY - promoTouchStartY;
      if (Math.abs(deltaX) > 40 && Math.abs(deltaX) > Math.abs(deltaY)) {
        showPromo(promoIndex + (deltaX < 0 ? 1 : -1));
        startPromoRotation();
      }
    }, { passive: true });
    promoCarousel.addEventListener('mouseenter', function () { window.clearInterval(promoTimer); });
    promoCarousel.addEventListener('mouseleave', startPromoRotation);
    promoCarousel.addEventListener('focusin', function () { window.clearInterval(promoTimer); });
    promoCarousel.addEventListener('focusout', startPromoRotation);
    showPromo(0);
    startPromoRotation();
  }
  $('cartOpenBtn').addEventListener('click', function () { show('viewCart'); open(); });
  $('menuToggle').addEventListener('click', toggleMenu);
  $('mobileMenu').querySelectorAll('a').forEach(function (link) { link.addEventListener('click', closeMenu); });
  window.addEventListener('resize', function () { if (window.innerWidth > 680) closeMenu(); });
  var scrollTopBtn = $('scrollTopBtn');
  if (scrollTopBtn) {
    function toggleScrollTopBtn() { scrollTopBtn.classList.toggle('visible', window.scrollY > 500); }
    window.addEventListener('scroll', toggleScrollTopBtn, { passive: true });
    toggleScrollTopBtn();
    scrollTopBtn.addEventListener('click', function () { window.scrollTo({ top: 0, behavior: 'smooth' }); });
  }
  document.addEventListener('keydown', function (event) { if (event.key === 'Escape') closeMenu(); });
  document.querySelectorAll('[data-close-overlay]').forEach(function (el) { el.addEventListener('click', close); });
  $('toCheckoutBtn').addEventListener('click', function () { if (lineCount()) { show('viewCheckout'); updateMethod(); } });
  $('backToCartBtn').addEventListener('click', function () { show('viewCart'); });
  $('closeSuccessBtn').addEventListener('click', function () { close(); show('viewCart'); });
  $('fulfillment').addEventListener('change', updateMethod);
  $('birthdayDiscount').addEventListener('change', render);
  $('eventDate').min = new Date().toISOString().slice(0, 10);
  $('submitOrderBtn').addEventListener('click', async function () {
    if (!lineCount() || !validate()) return;
    var button = this;
    var payload = {
      name: $('customerName').value.trim(), phone: $('phone').value.trim(), telegramNick: $('tgNick').value.trim(),
      eventDate: $('eventDate').value,
      fulfillment: $('fulfillment').value, address: $('address').value.trim(), comment: $('comment').value.trim(),
      birthdayDiscount: birthdayChecked(),
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
