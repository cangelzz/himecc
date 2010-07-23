# -*- coding: utf-8 -*-

tracking = """<script type="text/javascript">
  var _gaq = _gaq || [];
  _gaq.push(['_setAccount', 'UA-17431453-1']);
  _gaq.push(['_trackPageview']);

  (function() {
    var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
    ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
    var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
  })();
</script>"""
#"<script src='/static/jquery.js'></script>
commonHeader = """<html><head>
<title>HIME</title>
<link rel="Stylesheet" href="/static/my.css" media="screen" type="text/css" />
<meta http-equiv="content-type" content="text/html; charset=utf-8">
<meta name="robots" content="noindex,nofollow,noarchive,nosnippet">
<meta name="viewport" content="width=device-width, user-scalable=no">
<meta name="viewport" content="initial-scale=1.0; maximum-scale=1.0; user-scalable=0;" />""" + tracking + """<script>
function setOrientation() {
  var orient = (window.innerWidth||320)==320?"portrait":"landscape";
  var cl = document.body.className;
  cl = cl.replace(/portrait|landscape/, orient);
  document.body.className = cl;
};

window.addEventListener('load', setOrientation, false);
window.addEventListener('orientationchange', setOrientation, false);
</script> """

myFooter = """<div id="footer"></div><!--></body></html>"""
copyright = """<div id="copyright"><!--><a href="/smart/">smart</a><a href="http://code.google.com/p/himecc/" target="_blank">code</a><a href="/static/about.html">about</a><div>"""
ipadFooter = """</body></html>"""

nav_common = "<h1 class='nav'><a href='javascript:history.go(-1)' class='btnLeft0'>&lt;</a><a class='btnCenter0 left18' href='/' style='{width:66px}'>Home</a></h1>"

page_404 = """<h1 class="error">Error</h1><ul><li><!--></li></ul>"""
