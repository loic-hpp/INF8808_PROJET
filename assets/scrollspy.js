/* Scroll-spy: highlight sidebar item for the section currently in view. */
(function () {
  function init() {
    var links = Array.from(document.querySelectorAll('#sidebar .nav-link'));
    if (!links.length) {
      // Dash renders after DOMContentLoaded sometimes; retry
      return setTimeout(init, 300);
    }
    var map = {};
    links.forEach(function (a) {
      var t = a.getAttribute('data-target');
      if (t) map[t] = a;
    });

    var targets = Object.keys(map)
      .map(function (id) { return document.getElementById(id); })
      .filter(Boolean);

    if (!targets.length) return setTimeout(init, 300);

    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          links.forEach(function (l) { l.classList.remove('active'); });
          var a = map[entry.target.id];
          if (a) a.classList.add('active');
        }
      });
    }, { rootMargin: '-40% 0px -55% 0px', threshold: 0 });

    targets.forEach(function (el) { io.observe(el); });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
