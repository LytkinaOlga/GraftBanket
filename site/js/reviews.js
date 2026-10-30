// Client reviews carousel (arrows, swipe, counter, keyboard) and the screenshot lightbox.
(function () {
  document.querySelectorAll('[data-reviews]').forEach(function (root) {
    var track = root.querySelector('.reviews-track');
    var cards = track.children;
    var prev = root.querySelector('.reviews-prev');
    var next = root.querySelector('.reviews-next');
    var count = root.querySelector('.reviews-count');
    var dots = root.querySelectorAll('[data-review-dot]');
    function step() { return cards.length > 1 ? cards[1].offsetLeft - cards[0].offsetLeft : track.clientWidth; }
    function atEnd() { return track.scrollLeft + track.clientWidth >= track.scrollWidth - 2; }
    function current() { return Math.min(cards.length - 1, Math.round(track.scrollLeft / step())); }
    function update() {
      // With several cards in view the last ones can't reach the left edge, so the end counts as the last card.
      var i = atEnd() ? cards.length - 1 : current();
      count.textContent = (i + 1) + ' / ' + cards.length;
      dots.forEach(function (dot, k) { dot.setAttribute('aria-current', k === i ? 'true' : 'false'); });
      prev.disabled = track.scrollLeft <= 2;
      next.disabled = atEnd();
    }
    function show(i) { track.scrollTo({ left: Math.max(0, Math.min(cards.length - 1, i)) * step() }); }
    function go(dir) { show(current() + dir); }
    dots.forEach(function (dot) { dot.addEventListener('click', function () { show(Number(dot.dataset.reviewDot)); }); });
    prev.addEventListener('click', function () { go(-1); });
    next.addEventListener('click', function () { go(1); });
    track.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowLeft' || e.key === 'ArrowRight') { e.preventDefault(); go(e.key === 'ArrowLeft' ? -1 : 1); }
    });
    track.addEventListener('scroll', update, { passive: true });
    window.addEventListener('resize', update);
    update();
  });

  var popup = document.querySelector('.review-popup');
  if (popup && popup.showModal) {
    document.querySelectorAll('[data-review-more]').forEach(function (button) {
      button.addEventListener('click', function () {
        var card = button.closest('.review-card');
        popup.querySelector('.review-date').innerHTML = card.querySelector('.review-date').innerHTML;
        popup.querySelector('.review-popup-text').innerHTML = card.querySelector('.review-full-text').innerHTML;
        popup.showModal();
      });
    });
    popup.addEventListener('click', function (e) {
      var r = popup.getBoundingClientRect();
      if (e.target === popup && (e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom)) popup.close();
    });
  }

  var dialog = document.querySelector('.review-lightbox');
  if (!dialog || !dialog.showModal) return;
  var img = dialog.querySelector('img');
  document.querySelectorAll('[data-review-shot]').forEach(function (link) {
    link.addEventListener('click', function (e) {
      e.preventDefault();
      img.src = link.href;
      img.alt = link.querySelector('img').alt;
      dialog.showModal();
    });
  });
  // Escape closes the dialog natively; a click on the backdrop closes it too.
  dialog.addEventListener('click', function (e) { if (e.target === dialog) dialog.close(); });
})();
