(function(){
  var hdr = document.getElementById('hdr');
  var menu = document.getElementById('menu');
  var mega = document.getElementById('mega');
  var burger = document.getElementById('burger');
  var mnav = document.getElementById('mobileNav');

  /* 현재 섹션 표시 */
  var sec = document.body.dataset.sec;
  if (sec) menu.querySelectorAll('a').forEach(function(a){ if (a.dataset.sec === sec) a.classList.add('is-here'); });

  /* 메가 메뉴 — 메뉴 글자 위에서만 열림, 잠깐 벗어나도 유지 */
  var mt;
  function openMega(){ clearTimeout(mt); hdr.classList.add('mega-open'); }
  function closeMega(){ mt = setTimeout(function(){ hdr.classList.remove('mega-open'); syncHeader(); }, 160); }
  menu.addEventListener('mouseenter', openMega);
  menu.addEventListener('mouseleave', closeMega);
  mega.addEventListener('mouseenter', openMega);
  mega.addEventListener('mouseleave', closeMega);
  document.addEventListener('keydown', function(e){ if (e.key === 'Escape') hdr.classList.remove('mega-open'); });

  /* 모바일 */
  burger.addEventListener('click', function(){
    var open = mnav.classList.toggle('open');
    hdr.classList.toggle('on-light', open || wantsLight());
    document.body.style.overflow = open ? 'hidden' : '';
  });

  /* 헤더 색 — 헤더 아래에 깔린 요소가 어두우면 흰 글씨, 아니면 흰 배경 */
  function wantsLight(){
    var y = hdr.getBoundingClientRect().bottom;
    var light = true;
    document.querySelectorAll('[data-theme]').forEach(function(s){
      var r = s.getBoundingClientRect();
      if (r.top <= y && r.bottom > y){
        light = !(s.dataset.theme === 'dark' && !s.classList.contains('open'));
      }
    });
    return light;
  }
  function syncHeader(){ if (hdr.classList.contains('mega-open')) return; hdr.classList.toggle('on-light', wantsLight()); }
  addEventListener('scroll', syncHeader, {passive:true});
  addEventListener('resize', syncHeader);
  syncHeader();
  window.__syncHeader = syncHeader;
})();
