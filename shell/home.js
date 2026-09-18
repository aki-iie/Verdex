
(function(){
  var about = document.querySelector('.about');
  if (!about) return;
    var cells = [].slice.call(document.querySelectorAll('.cell'));
  var panels= [].slice.call(document.querySelectorAll('.panel'));

  function select(i){
    cells.forEach(function(c){ c.classList.toggle('is-on', +c.dataset.i === i); });
    panels.forEach(function(p){ p.classList.toggle('is-on', +p.dataset.i === i); });
  }
  cells.forEach(function(c){
    c.addEventListener('click', function(){
      select(+c.dataset.i);
      about.classList.add('open');
      window.__syncHeader && window.__syncHeader();
    });
  });
  document.querySelector('.close').addEventListener('click', function(){
    about.classList.remove('open');
    window.__syncHeader && window.__syncHeader();
  });

  // 헤더 색: 지금 헤더 아래에 깔린 섹션이 밝은지 어두운지로 결정
    
})();
