(function () {
  "use strict";

  var CART_STORAGE_KEY = "draftbanket_cart_v1";
  var CART_TTL_MS = 48 * 60 * 60 * 1000; // 48 часов

  var itemsById = {};
  ITEMS.forEach(function (it) { itemsById[it.id] = it; });

  var cart = loadCart(); // { itemId: qty }

  // ---------- storage ----------

  function loadCart() {
    try {
      var raw = localStorage.getItem(CART_STORAGE_KEY);
      if (!raw) return {};
      var data = JSON.parse(raw);
      if (!data || typeof data !== "object") return {};
      if (typeof data.savedAt !== "number" || Date.now() - data.savedAt > CART_TTL_MS) {
        localStorage.removeItem(CART_STORAGE_KEY);
        return {};
      }
      return data.items || {};
    } catch (e) {
      return {};
    }
  }

  function saveCart() {
    try {
      localStorage.setItem(CART_STORAGE_KEY, JSON.stringify({ savedAt: Date.now(), items: cart }));
    } catch (e) {
      /* ignore quota / privacy-mode errors */
    }
  }

  function clearCart() {
    cart = {};
    try { localStorage.removeItem(CART_STORAGE_KEY); } catch (e) {}
  }

  // ---------- cart helpers ----------

  function cartCount() {
    var n = 0;
    for (var id in cart) n += cart[id];
    return n;
  }

  function cartTotal() {
    var sum = 0;
    for (var id in cart) {
      var it = itemsById[id];
      if (it) sum += it.price * cart[id];
    }
    return sum;
  }

  function formatPrice(n) {
    return n.toLocaleString("ru-RU", { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + " BYN";
  }

  function setQty(id, qty) {
    if (qty <= 0) delete cart[id];
    else cart[id] = qty;
    saveCart();
    renderAll();
  }

  function addOne(id) { setQty(id, (cart[id] || 0) + 1); }
  function removeOne(id) { setQty(id, (cart[id] || 0) - 1); }

  // ---------- rendering: catalog ----------

  var catalogEl = document.getElementById("catalog");
  var categoryNavEl = document.getElementById("categoryNav");

  function buildCatalog() {
    categoryNavEl.innerHTML = CATEGORIES.map(function (c) {
      return '<a class="chip" data-cat="' + c.id + '" href="#cat-' + c.id + '">' + c.title + "</a>";
    }).join("");

    catalogEl.innerHTML = CATEGORIES.map(function (c) {
      var items = ITEMS.filter(function (it) { return it.category === c.id; });
      return (
        '<section class="category-section" id="cat-' + c.id + '">' +
        "<h2>" + c.title + "</h2>" +
        '<div class="grid">' +
        items.map(renderCard).join("") +
        "</div>" +
        "</section>"
      );
    }).join("");
  }

  function renderCard(it) {
    return (
      '<article class="card" data-id="' + it.id + '">' +
      '<div class="card-photo"><img src="' + it.img + '" alt="' + escapeHtml(it.name) + '" loading="lazy" /></div>' +
      '<div class="card-body">' +
      '<div class="card-name">' + escapeHtml(it.name) + "</div>" +
      '<div class="card-weight">' + escapeHtml(it.weight) + "</div>" +
      '<div class="card-desc">' + escapeHtml(it.description) + "</div>" +
      '<div class="card-composition">' + escapeHtml(it.composition) + "</div>" +
      '<div class="card-footer">' +
      '<div class="card-price">' + formatPrice(it.price) + "</div>" +
      '<div class="card-action" data-action-for="' + it.id + '"></div>' +
      "</div>" +
      "</div>" +
      "</article>"
    );
  }

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function renderCardActions() {
    document.querySelectorAll(".card-action").forEach(function (el) {
      var id = el.getAttribute("data-action-for");
      var qty = cart[id] || 0;
      if (qty === 0) {
        el.innerHTML = '<button class="add-btn" data-add="' + id + '">Добавить</button>';
      } else {
        el.innerHTML =
          '<div class="qty-stepper">' +
          '<button data-minus="' + id + '" aria-label="Уменьшить">−</button>' +
          "<span>" + qty + "</span>" +
          '<button data-plus="' + id + '" aria-label="Увеличить">+</button>' +
          "</div>";
      }
    });
  }

  // ---------- rendering: cart panel ----------

  var cartCountEl = document.getElementById("cartCount");
  var cartBodyEl = document.getElementById("cartBody");
  var cartTotalEl = document.getElementById("cartTotal");
  var cartFooterEl = document.getElementById("cartFooter");
  var toCheckoutBtn = document.getElementById("toCheckoutBtn");

  function renderCartPanel() {
    var count = cartCount();
    if (count > 0) {
      cartCountEl.hidden = false;
      cartCountEl.textContent = String(count);
    } else {
      cartCountEl.hidden = true;
    }

    var ids = Object.keys(cart);
    if (ids.length === 0) {
      cartBodyEl.innerHTML = '<div class="cart-empty">Корзина пока пуста.<br>Добавьте блюда из каталога.</div>';
      cartFooterEl.hidden = true;
      return;
    }

    cartFooterEl.hidden = false;
    cartBodyEl.innerHTML = ids.map(function (id) {
      var it = itemsById[id];
      var qty = cart[id];
      if (!it) return "";
      return (
        '<div class="cart-line">' +
        '<img src="' + it.img + '" alt="" />' +
        '<div class="cart-line-info">' +
        '<div class="cart-line-name">' + escapeHtml(it.name) + "</div>" +
        '<div class="cart-line-price">' + formatPrice(it.price) + " × " + qty + " = " + formatPrice(it.price * qty) + "</div>" +
        '<div class="cart-line-controls">' +
        '<div class="qty-stepper">' +
        '<button data-minus="' + id + '" aria-label="Уменьшить">−</button>' +
        "<span>" + qty + "</span>" +
        '<button data-plus="' + id + '" aria-label="Увеличить">+</button>' +
        "</div>" +
        '<button class="remove-btn" data-remove="' + id + '">Удалить</button>' +
        "</div>" +
        "</div>" +
        "</div>"
      );
    }).join("");

    cartTotalEl.textContent = formatPrice(cartTotal());
  }

  function renderAll() {
    renderCardActions();
    renderCartPanel();
  }

  // ---------- delegated click handling ----------

  document.addEventListener("click", function (e) {
    var addId = e.target.closest("[data-add]");
    var plusId = e.target.closest("[data-plus]");
    var minusId = e.target.closest("[data-minus]");
    var removeId = e.target.closest("[data-remove]");

    if (addId) addOne(addId.getAttribute("data-add"));
    else if (plusId) addOne(plusId.getAttribute("data-plus"));
    else if (minusId) removeOne(minusId.getAttribute("data-minus"));
    else if (removeId) setQty(removeId.getAttribute("data-remove"), 0);
  });

  // ---------- category nav active state ----------

  document.addEventListener("click", function (e) {
    var chip = e.target.closest(".chip");
    if (!chip) return;
    document.querySelectorAll(".chip").forEach(function (c) { c.classList.remove("active"); });
    chip.classList.add("active");
  });

  // ---------- overlay: open/close & views ----------

  var cartOverlay = document.getElementById("cartOverlay");
  var viewCart = document.getElementById("viewCart");
  var viewCheckout = document.getElementById("viewCheckout");
  var viewSuccess = document.getElementById("viewSuccess");

  function showView(view) {
    [viewCart, viewCheckout, viewSuccess].forEach(function (v) { v.hidden = v !== view; });
  }

  function openOverlay() {
    cartOverlay.classList.add("open");
    document.body.style.overflow = "hidden";
  }

  function closeOverlay() {
    cartOverlay.classList.remove("open");
    document.body.style.overflow = "";
  }

  document.getElementById("cartOpenBtn").addEventListener("click", function () {
    showView(viewCart);
    renderCartPanel();
    openOverlay();
  });

  document.querySelectorAll("[data-close-overlay]").forEach(function (el) {
    el.addEventListener("click", closeOverlay);
  });

  // ---------- checkout ----------

  var checkoutSummary = document.getElementById("checkoutSummary");
  var tgNickInput = document.getElementById("tgNick");
  var phoneInput = document.getElementById("phone");
  var fieldName = document.getElementById("fieldName");
  var fieldPhone = document.getElementById("fieldPhone");
  var submitBtn = document.getElementById("submitOrderBtn");

  toCheckoutBtn.addEventListener("click", function () {
    if (cartCount() === 0) return;
    checkoutSummary.textContent = cartCount() + " поз. на сумму " + formatPrice(cartTotal());
    showView(viewCheckout);
  });

  document.getElementById("backToCartBtn").addEventListener("click", function () {
    showView(viewCart);
  });

  document.getElementById("closeSuccessBtn").addEventListener("click", function () {
    closeOverlay();
    showView(viewCart);
  });

  function validatePhone(value) {
    var digits = value.replace(/\D/g, "");
    return digits.length >= 10 && digits.length <= 15;
  }

  function validateForm() {
    var nickOk = tgNickInput.value.trim().length >= 2;
    var phoneOk = validatePhone(phoneInput.value);
    fieldName.classList.toggle("invalid", !nickOk);
    fieldPhone.classList.toggle("invalid", !phoneOk);
    return nickOk && phoneOk;
  }

  submitBtn.addEventListener("click", function () {
    if (!validateForm()) return;

    var payload = {
      telegramNick: tgNickInput.value.trim(),
      phone: phoneInput.value.trim(),
      items: Object.keys(cart).map(function (id) {
        var it = itemsById[id];
        return { name: it.name, quantity: cart[id], price: it.price, sum: it.price * cart[id] };
      }),
      total: cartTotal(),
    };

    submitBtn.disabled = true;
    submitBtn.textContent = "Отправляем…";

    fetch("/api/order", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    })
      .then(function (res) {
        if (!res.ok) throw new Error("request failed");
        return res.json();
      })
      .then(function () {
        clearCart();
        renderAll();
        tgNickInput.value = "";
        phoneInput.value = "";
        submitBtn.disabled = false;
        submitBtn.textContent = "Отправить заявку";
        showView(viewSuccess);
      })
      .catch(function () {
        submitBtn.disabled = false;
        submitBtn.textContent = "Отправить заявку";
        alert("Не удалось отправить заявку. Попробуйте ещё раз или свяжитесь с нами по телефону.");
      });
  });

  // ---------- init ----------

  buildCatalog();
  renderAll();
})();
