(function(){
  // Simple translator toggler: looks for elements with data-translator-en and data-translator-es
  function setLanguage(lang){
    document.documentElement.lang = (lang === 'es') ? 'es' : 'en';
    var nodes = document.querySelectorAll('[data-translator-en]');
    nodes.forEach(function(n){
      var en = n.getAttribute('data-translator-en');
      var es = n.getAttribute('data-translator-es');
      if(!en) return;
      if(lang === 'es' && es !== null){
        if(n.tagName === 'INPUT' || n.tagName === 'TEXTAREA'){
          n.value = es;
        } else {
          n.innerText = es;
        }
      } else {
        if(n.tagName === 'INPUT' || n.tagName === 'TEXTAREA'){
          n.value = en;
        } else {
          n.innerText = en;
        }
      }
    });
  }

  function toggle(){
    var current = document.documentElement.lang === 'es' ? 'es' : 'en';
    var next = current === 'en' ? 'es' : 'en';
    setLanguage(next);
    try{ localStorage.setItem('site-lang', next); }catch(e){}
  }

  document.addEventListener('DOMContentLoaded', function(){
    var btn = document.getElementById('lang-toggle');
    if(btn){ btn.addEventListener('click', function(e){ e.preventDefault(); toggle(); }); }
    var pref = null;
    try{ pref = localStorage.getItem('site-lang'); }catch(e){}
    if(pref) setLanguage(pref); else setLanguage('en');
  });
})();
