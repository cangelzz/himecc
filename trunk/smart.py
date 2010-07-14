# -*- coding: utf-8 -*-

from google.appengine.ext import webapp
from common import *
from util import print_all
import re

class Smart(webapp.RequestHandler):
    html = """<h1>Smart Jump</h1><form action="/smart/" method="post">
<h1 class="nav"><a class="btnCenter" href="/">Home</a></h1>
<ul><!-->
<li><label for="URL">URL</label></li><li><input type="text" name="URL" id="smartinput" /></li>
<li><label for="redirect">Redirect</label><input type="checkbox" name="redirect" id="redirect" /></li>
<li><input type="submit" value="Go" /></li>
<li>Usage: copy the link here as examples below:<p>
SMTH:
<pre>
  http://www.newsmth.net/bbstcon.php?board=MMJoke&gid=87303
  http://www.newsmth.net/bbscon.php?bid=458&id=1036275
  board=Apple&gid=122345
  board:Age,gid:3345667
</pre>
JJ:
<pre>
  http://bbs.jjwxc.net/showmsg.php?board=20&id=150631&msg=%D5%BD%C9%AB%C4%E6%C0%D6%D4%B0
  board=20&id=150631&page=1
</pre></p>
</li>
</ul>
</form>"""

    def get(self):
        print_all(self, [myHeader, self.html, myFooter])

    def post(self):
        url = self.request.get("URL")
        redirect = self.request.get("redirect") == "on" and True or False

        urlgo =""
        m = re.search("board.([\w\d_]+).gid.(\d+)", url)
        if m: urlgo = "/subject/%s/%s" % m.groups()
        m = re.search("bid.(\d+).id.(\d+)", url)
        if m: urlgo = "/post/%s/%s" % m.groups()
        m = re.search("board.(\d+).page.(\d+)", url)
        if m: urlgo = "/jjboard/%s/%s" % m.groups()
        m = re.search("board.(\d+).id.(\d+).*?(page.(\d+))?", url)
        if m: 
            if m.group(3):
                urlgo = "/jjsubject/%s/%s/%s" % (m.group(1),m.group(2),m.group(4))
            else:
                urlgo = "/jjsubject/%s/%s" % (m.groups()[:2])
#        m = re.search("board.(\d+).id.(\d+)", url)
#        if m: urlgo = "/jjsubject/%s/%s" % m.groups()

        if urlgo:
            if redirect: self.redirect(urlgo)
            else: 
                page = self.html.replace("<!-->", "<li><a href='%s' target='_blank' class='urlgo'>Click: %s</a></li>" % (urlgo, urlgo))
                print_all(self, [myHeader, page, myFooter])
                return

        msg = "<li>The URL: <span style='color:red'>%s</span> doesn't match any patter</li>" % url
        print_all(self, [myHeader, self.html.replace("<!-->", msg), myFooter])
