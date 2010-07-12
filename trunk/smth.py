# emacs-mode: -*- python-*-
# -*- coding: utf-8 -*-
# author: cangelzz@smth
# last-modified: 2010-07-12

from google.appengine.ext import webapp 
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import urlfetch
#from google.appengine.api.urlfetch import fetch
from google.appengine.api import images
from google.appengine.ext import db
from random import random
import re 
from define import id2board, board2id, favor, favor2chs, Favor
import logging

DEBUG = False
myHeader = """<html><head>
<link rel="Stylesheet" href="/static/my.css" media="screen" type="text/css" />
%s
<meta http-equiv="content-type" content="text/html; charset=utf-8"> 
<meta name="viewport" content="width=device-width, user-scalable=no">
<meta name="viewport" content="initial-scale=1.0; maximum-scale=1.0; user-scalable=0;" /> 
<script>
function setOrientation() {
  var orient = (window.innerWidth||320)==320?"portrait":"landscape";
  var cl = document.body.className;
  cl = cl.replace(/portrait|landscape/, orient);
  document.body.className = cl;
};

window.addEventListener('load', setOrientation, false);
window.addEventListener('orientationchange', setOrientation, false);

</script>
</head><body>""" % (DEBUG and "<script src='/static/jquery.js'></script>" or "")

myFooter = """<h1></h1></body></html>"""
ipadFooter = """</body></html>"""

def fetch(url, payload=None, method=urlfetch.GET, headers={}, allow_truncated=False, follow_redirects=True, deadline=10):
    return urlfetch.fetch(url, payload=payload, method=method, headers=headers, allow_truncated=True, follow_redirects=follow_redirects, deadline=deadline)

def convertFromGB2312ToUTF8(onestr):
    newstr = onestr
    try:
        newstr = unicode(newstr, 'cp936', 'ignore')
    except:
        pass
    return newstr.encode('utf-8', 'ignore')

def print_all(func, li):
    for line in li:
        func(line)

from google.appengine.api import users
def _login_info(request):
    user = users.get_current_user()
    if user:
        url = users.create_logout_url(request.path)
        html = ", %s<a class='login' href='%s'>Out</a><a class='login' href='/config/'>C</a>" % (user.nickname(), url)
    else:
        url = users.create_login_url(request.path)
        html = ", Guest<a class='login' href='%s'>In</a>" % url

    return html

def _user(email="anonymous@gmail.com"):
    user = users.get_current_user()
    if not user:
        user = users.User(email)
    return user
    
class Config(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()
        config = db.GqlQuery("SELECT * FROM Favor WHERE user=:1", user).get()
        favorstext = ""
        chk_value = ""
        if config:
            favorstext = ",".join(config.favorlist)
            chk_value = config.sort == "on" and "checked" or ""
        html = """<form action="/config/" method="post">
<label for="favors">Favors </lable><input type="text" name="favors" id="favors"/ value="%s"><br/>
<lable for="sort">Sort <input type="checkbox" name="sort" id="sort" checked="%s" /><br/>
<input type="submit" value="Submit" />
</form>
""" % (favorstext, chk_value)

        print_all(self.response.out.write, [myHeader, html, myFooter])

    def post(self):
        user = users.get_current_user()
        if not user:
            self.redirect("/")
        else:
            favors = re.split("[^\w\d_]", str(self.request.get("favors")))
            sort = self.request.get("sort") == "on" and True or False
            config = db.GqlQuery("SELECT * FROM Favor WHERE user=:1", user).get()
            if config:
                config.favorlist = favors
                config.sort = sort
            else:
                config = Favor(user=user, favorlist=favors, sort=sort)
            config.put()
            self.redirect("/")
                

def _favor():
    user = users.get_current_user()
    if not user:
        return True, favor

    config = db.GqlQuery("SELECT * FROM Favor WHERE user=:1", user).get()
    if not config:
        return True, favor
    if config.favorlist in [[],[""],None]:
        return True, favor
    else:
        if config.sort:
            return False, ["top10"] + sorted(config.favorlist, key=unicode.encode)
        else:
            return False, favor

class MainPage(webapp.RequestHandler):
    def get(self):
#        self.response.headers['Content-Type'] = myContentType
        head = "<h1>Welcome%s</h1>" % _login_info(self.request)
        navlink = """<h1 class="navjump"><input id='boardtogo' type="text" /><a onclick="this.href='/board/6'+document.getElementById('boardtogo').value" class='btnGo'>Go</a></h1>"""
        page = ['<ul class="boards">']

        default, favorlist = _favor()
        for b in favorlist:
            if default:
                page.append("<li><a href='/board/%s/6'><div style='display:inline-block'>%s</div><div style='display:inline-block;float:right'>%s</div></a></li>" % (b, b.upper(), favor2chs[b]))
            else:
                page.append("<li><a href='/board/%s/6'><div style='display:inline-block'>%s</div></a></li>" % (b, b.upper()))
        page.append("</ul>")
        print_all(self.response.out.write, [myHeader, head, navlink, "".join(page), myFooter])

def _board(path, type=0):
        #  2     3    4
        # /board/type/page
        paras = path.split('/')
        board = paras[2]
        if (len(paras) == 4):
            isLast = True
            pagetogo = ""
        else:
            isLast = False
            pagetogo = "&page=" + paras[4]

        head = "<h1 id='boardh1'>%s</h1>" % board.upper()

        if board == "top10":
            url = "http://www.newsmth.net/rssi.php?h=1"
            result = fetch(url)
            #content = convertFromGB2312ToUTF8(result.content)
            content = result.content
            bname_and_id = re.findall("<link>.*?(?<=board=)(\w+).*?gid=(\d+)", content)
            title_and_author =  re.findall("<description>.*?:\s(.*?),.*?<br/>.*?:\s(.*?)<br/>",content)

            if type == 1:
                navlink = ""
            else:
                navlink = "<h1 class='nav'><a href='javascript:history.go(-1)' class='btnLeft0'>&lt;</a><a class='btnCenter' href='/' style='{width:66px}'>Home</a></h1>"

            navlink_top = head + navlink

            page = ["<ul class='threads'>"]
            for g1, g2 in zip(bname_and_id, title_and_author):
#                if type == 1:
#                    page.append("<li><a href=\"javascript:loadSmart('/isubject/%s/%s')\">%s&nbsp;&nbsp;<span class='author'>%s</span> <span class='boardinth'>[%s]</span></a></li>" % (g1[0], g1[1], g2[1], g2[0], g1[0]))
#                else:
                    page.append("<li><a href='/subject/%s/%s'>%s&nbsp;&nbsp;<span class='author'>%s</span> <span class='boardinth'>[%s]</span></a></li>" % (g1[0], g1[1], g2[1], g2[0], g1[0]))
            page.append("</ul>")

            return [navlink_top, navlink, "".join(page)]

        if paras[3] == "0":
            ftype = ""
            boardlink = "<a class='btnCenter' href='/board/%s/6'>Subject</a>" % board
        else:
            ftype =  "&ftype=" + paras[3]
            boardlink = "<a class='btnCenter' href='/board/%s/0'>Normal</a>" % board

        url = 'http://www.newsmth.net/bbsdoc.php?board=' + board + ftype + pagetogo

        result = fetch(url)
        content = convertFromGB2312ToUTF8(result.content)
        posts = re.findall("c\\.o\\((\\d+),(\\d+),'(.*?)','(.*?)',(\\d+),'(.*?)',(\\d+),\\d+,\\d+\\)", content)
        m = re.search("docWriter.*?(\\d+),\\d+,\\d+,\\d+,(\\d+),", content)
        page = m.group(2)

        lastPage = "/".join(["board", board, paras[3], str(int(page)-1)])
        nextPage = "/".join(isLast and ["board", board, paras[3]] or ["board", board, paras[3], str(int(page) + 1)])

        if (isLast):
            navlink = "<h1 class='nav'><a href='/%s' class='btnLeft0'>&lt;</a><a class='btnCenter' href='/' style='{width:66px}'>Home</a>%s</h1>" % (lastPage, boardlink)
        else:
            navlink = "<h1 class='nav'><a href='/%s' class='btnLeft0'>&lt;</a><a class='btnCenter' href='/' style='{width:66px}'>Home</a>%s<a href='/%s' class='btnRight0'>&gt;</a></h1>" % (lastPage, boardlink, nextPage)

        navlink_top = head + navlink
        page = ["<ul class='threads'>"]

        def _classname(mark, title, type):
            classes = []
            if "@" in mark: classes.append("att")
            if type == "0" and not title.startswith("Re: "): classes.append("mainsub")
            if len(classes) == 0:
                return ""
            else:
                return " class=\"%s\"" % (" ".join(classes))

        for p in posts:
            classname = _classname(p[3], p[5], paras[3])
            if paras[3] == "0":
                page.append(("<li%s><a href='/post/%s/%s'>%s&nbsp;&nbsp;<span class='author'>%s</span></a></li>" % (classname, m.group(1), p[0], p[5], p[2])))
            else:
                page.append(("<li%s><a href='/subject/%s/%s'>%s&nbsp;&nbsp;<span class='author'>%s</span></a></li>" % (classname, board, p[0], p[5], p[2])))

        page.append("</ul>")

        return [navlink_top, navlink, "".join(page)]

class Board(webapp.RequestHandler):
    def get(self):
        navlink_top, navlink, page = _board(self.request.path)
        print_all(self.response.out.write, [myHeader, navlink_top, page, navlink, myFooter])

class iBoard(webapp.RequestHandler):
    def get(self):
        navlink_top, navlink, page = _board(self.request.path, 1)
        print_all(self.response.out.write, [navlink_top, page, navlink])

def filterText(s):
    telnet_ctrl = re.compile("[[0-9;]+m")
    http_link = re.compile("(http://.*?)[^\w\d.+-=/_&^%?<]")
    #s = re.sub("(http://.*?)[^\w\d.+-=/_&^%?]", r"<a href='\1' target='_blank' class='httplink'>\1</a>", s.replace("\\r","").replace(r"\/", "/"))
    s = re.sub(r"\\/(?!\>)", "/", s)
    s = telnet_ctrl.sub("", s.replace("\\r",""))
    s = re.sub(r"【 在 (\w+).*? 的大作中提到: 】\\n", r"【\1】 ", s)
    return s
    return re.sub("(http://.*?)[^\w\d\s.+-=/_&^%?<]", r"<a href='\1' target='_blank' class='httplink'>|\1|</a>", s)

def _content(bid, id, page=""):
    url = ('http://www.newsmth.net/bbscon.php?bid=%s&id=%s%s' % (bid, id, page))
    result = fetch(url)
    content = filterText(convertFromGB2312ToUTF8(result.content))
    title = re.search(r"标  题: (.*?)\\n", content).group(1)
    ids = re.search(r"conWriter.*?'([\w\d]+)',\s(\d+),\s(\d+),\s(\d+),\s(\d+)", content).groups()
    au = re.search(r"发信人: (.*?),", content) #search author
    m = re.search(r", 站内(\\n)+(.*?)(\\n)+--", content, (re.MULTILINE | re.DOTALL))  #search StationIn #fix zhannei in nickname
    reply = ""
    refer = ""
    attpart = ""
    if m:
        s = re.sub(r"(\\n)+", "<br/>", m.group(2).strip("\\n "))
        reply = s #first post
        inx = s.find("【")
        if inx > 0:
            st = s[inx:]
            refergroup = st.split("<br/>")
            st = len(refergroup) > 3 and "<br/>".join(refergroup[:3]) or st
            reply = s[:inx].strip("<br/>")
            refer = st
        
        atts = re.findall("attach\('(.*?)',\s(\d+),\s(\d+)\);", content)
        for att in atts:
            fname = att[0]
            ext = fname[fname.find("."):]
            extL = ext.lower()
            if extL == ".jpg" or extL == ".jpeg" or extL == ".bmp" or extL == ".png" or extL == ".gif":
                att_url = "http://att.newsmth.net/att.php?n.%s.%s.%s" % (bid, id, att[2]) + ext
                bindata = fetch(url=att_url, method=urlfetch.GET, deadline=10).content
                img = images.Image(bindata)
                if img.width > 300:
                    img.resize(300)
                else:
                    img.resize(img.width)
                resizedata = img.execute_transforms(images.JPEG)
                import base64
                base64data = base64.encodestring(resizedata)
                attpart = attpart + "<br/><img src=\"data:image/jpeg;base64," + base64data + "\">"
    
    return list(ids) + [title, au.group(1), reply, refer, attpart]
    # board, bid, id, gid, reid, title, author, reply, refer, attach
    # 0      1    2   3    4     5      6       7      8      9
    #                                   0       1      2      3
def _content_html(li, type):
    if type == 1:
        return "<span class='author'>%s</span>: <span style='margin:0px;padding:0px;'>%s<span style='color:grey;'><br/>%s</span>%s</span>" % (li[0], li[1], li[2], li[3])
    elif type == 2:
        random_id = str(random())[2:]
        refer = ""
        if li[2] != "":
            refer = "<a id='%s' class='normal' href=\"javascript:document.getElementById('%s').firstElementChild.style.display='inline'\">+" % (random_id, random_id) + "<span style='color:grey;display:none;'><br/>" + li[2] + "</span></a>"
        return "<span class='author'>%s</span>: <span style='margin:0px;padding:0px;'>%s" % (li[0], li[1]) + refer + li[3] + "</span>"

def getContentHeji(bid, id):
    url = ('http://www.newsmth.net/bbscon.php?bid=%s&id=%s' % (bid, id))
    result = fetch(url)
    content = filterText(convertFromGB2312ToUTF8(result.content))
    m = re.search(r"站内(.*)o.h\(0\)", content, (re.MULTILINE | re.DOTALL))
    if m:
#        s = re.sub(r"^(\\n)+", "", m.group(1).strip())
        s = re.sub(r"(\\n)+", "<br/>", m.group(1).strip("\\n "))
        #s = re.sub(r"(\\n)+", "<br/>", s)
        s = re.sub("<br/>\s+", "", s)
        hl = "☆─────────────────────────────────────☆"
        ps = s.split(hl)[1:]
        result = []
        for p in ps:
            inx = p.find("【")
            if inx > 0:
                st = p[inx:]#.replace(">>", ">")
                refergroup = st.split("<br/>")
                st = len(refergroup) > 3 and "<br/>".join(refergroup[:3]) or st
                #p = p[:inx] + "<span style='color:grey'>" + st + "</span>"
                random_id = str(random())[2:]
                p = p[:inx].replace("<br/>", "") + "<a id='%s' class='normal' href=\"javascript:document.getElementById('%s').firstElementChild.style.display='inline'\">+" % (random_id, random_id) + "<span style='color:grey;display:none;'>" + "<br/>" + st + "</span></a>"

            result.append(re.sub("(^[\w\d]+.*?\)).*?提到:", r"<span class='author'>\1</span>: ",p))
        #s = "<li>" + "</li><li>".join(s.split(hl)[1:]) + "</li>"
        #return s
        return "<li>" + "</li><li>".join(result) + "</li>"

def _subject(path, type=0):
        paras = path.split('/')
        board,gid = paras[2],paras[3]
        if (len(paras) == 4):
            pagenum = ""
        else:
            pagenum = "&start=" + gid + "&pno=" + paras[4]

        url = 'http://www.newsmth.net/bbstcon.php?board=%s&gid=%s%s' % (board, gid, pagenum)
#        self.response.out.write(((board + '  ') + gid))
        result = fetch(url)
        t = re.search("<title>.*?-.*?-(.*?)</title>", convertFromGB2312ToUTF8(result.content))
        m = re.search("tconWriter.*?\\d+,\\d+,\\d+,(\\d+),(\\d+),", result.content)

        totalPage = int(m.group(1))
        curPage = int(m.group(2))

        def makejumplist(c, t, bname, gid):
            s = []
            i = 1
            while i <= t:
                if i == c:
                    s.append(str(i))
                else:
                    s.append("<a href='/subject/%s/%s/%d'>%s</a>" % (bname, gid, i, i))
                i = i + 1
            return "&nbsp;&nbsp;".join(s)
        boardLink = "<a class='btnCenter' href='/board/%s/6' style='{width:%dpx}'>%s</a>" % (board, len(board)*8,board.upper())
        if curPage == 1:
            if curPage == totalPage:
                navlink = "<h1 class='nav' id='snavtop'><a href='javascript:history.go(-1)' class='btnLeft0'>&lt;</a>%s</h1>" % boardLink
                navlink_bottom = navlink
            else:
                nextPage = "/".join(["subject", board, gid, "2"])
                navlink = "<h1 class='nav'><a href='javascript:history.go(-1)' class='btnLeft0'>&lt;</a>%s<a href='/%s' class='btnRight0'>2</a><a class='btnCenterRight' href=\"javascript:document.getElementById('hidejump').style.display='block'\">J</a></h1><div id='hidejump' class='hidediv'>%s</div>" % (boardLink, nextPage, makejumplist(curPage, totalPage, board, gid))
                navlink_bottom = "<div id='hidejump2' class='hidediv'>%s</div><h1 class='nav'><a href='javascript:history.go(-1)' class='btnLeft0'>&lt;</a>%s<a href='/%s' class='btnRight0'>2</a><a class='btnCenterRight' href=\"javascript:document.getElementById('hidejump2').style.display='block'\">J</a></h1>" % (makejumplist(curPage, totalPage, board, gid), boardLink, nextPage)
        else:
            if curPage == totalPage:
                lastnum = curPage - 1
                navlink = "<h1 class='nav'><a href='javascript:history.go(-1)' class='btnLeft0'>%d</a>%s<a class='btnCenterRight' href=\"javascript:document.getElementById('hidejump').style.display='block'\">J</a></h1><div id='hidejump' class='hidediv'>%s</div>" % (lastnum, boardLink, makejumplist(curPage, totalPage, board, gid))
                navlink_bottom = "<div id='hidejump2' class='hidediv'>%s</div><h1 class='nav'><a href='javascript:history.go(-1)' class='btnLeft0'>%d</a>%s<a class='btnCenterRight' href=\"javascript:document.getElementById('hidejump2').style.display='block'\">J</a></h1>" % (makejumplist(curPage, totalPage, board, gid), lastnum, boardLink)
            else:
                lastnum = curPage - 1
                nextnum = curPage + 1
                lastPage = "/".join(["subject", board, gid, str(lastnum)])
                nextPage = "/".join(["subject", board, gid, str(nextnum)])
                navlink = "<h1 class='nav'><a href='/%s' class='btnLeft0'>%s</a>%s<a href='/%s' class='btnRight0'>%s</a><a class='btnCenterRight' href=\"javascript:document.getElementById('hidejump').style.display='block'\">J</a></h1><div id='hidejump' class='hidediv'>%s</div>" % (lastPage, str(lastnum), boardLink, nextPage, str(nextnum), makejumplist(curPage, totalPage, board, gid))
                navlink_bottom = "<div id='hidejump2' class='hidediv'>%s</div><h1 class='nav'><a href='/%s' class='btnLeft0'>%s</a>%s<a href='/%s' class='btnRight0'>%s</a><a class='btnCenterRight' href=\"javascript:document.getElementById('hidejump2').style.display='block'\">J</a></h1>" % (makejumplist(curPage, totalPage, board, gid), lastPage, str(lastnum), boardLink, nextPage, str(nextnum))

        navlink =  "<h1>%s</h1>" % t.group(1) + navlink
        navlink_bottom = navlink_bottom.replace("snavtop", "snavbottom")

        posts = re.findall('''\[(\d+),'(.*?)'\]''', result.content)
        page = "<ul class='posts'>"

        #different handle SameSubject posts
        if t.group(1).find("合集") > 0:
            result = getContentHeji(board2id[board.lower()], posts[0][0])
            page += result
            posts = posts[1:]

        for p in posts:
            result = _content_html(_content(board2id[board.lower()], p[0])[6:], 2)
            page += "<li>%s</li>" % result
        page += "</ul>"

        return [navlink, navlink_bottom, page]

class Subject(webapp.RequestHandler):
    def get(self):
        navlink, navlink_bottom, page = _subject(self.request.path)
        print_all(self.response.out.write, [myHeader, navlink, page, navlink_bottom, myFooter])

class iSubject(webapp.RequestHandler):
    def get(self):
        navlink, navlink_bottom, page = _subject(self.request.path, 1)
        print_all(self.response.out.write, [navlink, page, navlink_bottom])

def _post(path, type=0):
        paras = path.split('/')
        bid,id = paras[2],paras[3]
        if len(paras) == 5:
            page = "&p=" + paras[4]
        else:
            page = ""

        c = _content(bid, id, page)
        board, bid, id, gid, reid, title = c[:6]

#        if type == 1:
#            lastSubPost = "/".join(["ipost", bid, id, "tp"])
#            nextSubPost = "/".join(["ipost", bid, id, "tn"])
#            firstPost = "/".join(["ipost", bid, gid])
#            expandPost = "/".join(["isubject", board, gid])
#            boardlink = "/".join(["iboard", board, "0"])
#        else:
        lastSubPost = "/".join(["post", bid, id, "tp"])
        nextSubPost = "/".join(["post", bid, id, "tn"])
        firstPost = "/".join(["post", bid, gid])
        expandPost = "/".join(["subject", board, gid])
        boardlink = "/".join(["board", board, "0"])
#        if type == 1:
        navlink = "<h1>%s</h1>" %title + "<h1 class='nav'><a href='/%s' class='btnLeft0'>&lt;</a><a href='/%s' class='btnCenterLeft'>1</a><a href='/%s' class='btnCenterLeft'>+</a><a href='/%s' class='btnCenter'>%s</a><a href='/%s' class='btnRight0'>&gt;</a></h1>" % (lastSubPost,firstPost,expandPost,boardlink,board.upper(),nextSubPost)
#        else:
#            navlink = "<h1>%s</h1><h1 class='nav'><a href=\"javascript:loadPost('/%s')\" class='btnLeft0'>&lt;</a><a href=\"javascript:loadPost('/%s')\" class='btnCenterLeft'>1</a><a href=\"javascript:loadPost('/%s')\" class='btnCenterLeft'>+</a><a href=\"javascript:loadPost('/%s')\" class='btnCenter'>%s</a><a href=\"javascript:loadPost('/%s')\" class='btnRight0'>&gt;</a></h1>" % (title,lastSubPost,firstPost,expandPost,boardlink,board.upper(),nextSubPost)

        return [navlink, "<ul class='posts'><li>" + _content_html(c[6:], 1) + "</li></ul>"]

class Post(webapp.RequestHandler):
    def get(self):
        navlink, page = _post(self.request.path)
        print_all(self.response.out.write, [myHeader, navlink, page, myFooter])

class iPost(webapp.RequestHandler):
    def get(self):
        navlink, page = _post(self.request.path, type=1)
        print_all(self.response.out.write, [navlink, page])

class Test(webapp.RequestHandler):
    def get(self):
        url = "http://www.newsmth.net/rssi.php?h=1"
        result = fetch(url)
        content = convertFromGB2312ToUTF8(result.content)
        #navlink = "<h1 class='nav'><a href='%s' class='btnLeft0'>%s</a>%s<a href='%s' class='btnRight0'>%s</a><a class='btnCenterRight' href=\"javascript:document.getElementById('hidejump').style.display='block'\">J</a></h1><div id='hidejump' class='hidediv'>%s</div>" % (lastPage, str(lastnum), boardLink, nextPage, str(nextnum), makejumplist(curPage, totalPage, board, gid))
        self.response.out.write(myHeader)
        self.response.out.write(content)

ipadHeader = """<html><head>
<link rel="Stylesheet" href="/static/my.css" media="screen" type="text/css" />
<meta name="viewport" content="width=device-width, user-scalable=no">
<meta name="viewport" content="initial-scale=1.0; maximum-scale=1.0; user-scalable=0;" /> 
<script src="/static/jquery.js"></script>
<script src="/static/jScrollTouch.js"></script>
<script src="/static/ipad.js"></script>
</head><body class="webkit">"""

def makenav():
    s = []
    for b in favor:
        s.append("<a class='hBoard' href=\"javascript:loadBoard('/iboard/%s/6')\">%s</a>" % (b, b.upper()))
    return "<span style='color:gray;'>|</span>".join(s)
    #return " ".join(favor)

ipadBody = """
<div id="navboard"><div class="navleft"><a href="javascript:nav2left()">&lt;</a></div><div id="navcon">%s</div><div class="navright"><a href="javascript:nav2right()">&gt;</a></div></div>
<div id="progress" style="display:none"><span>loading ...</span></div>
<div id="main">

  <div id="divThreads"></div>
  <div id="divPosts"></div>

</div>
""" % makenav()


class iPad(webapp.RequestHandler):
    def get(self):
        print_all(self.response.out.write, [ipadHeader, ipadBody, ipadFooter])


application = webapp.WSGIApplication([('/',  MainPage),
                                      ('/smth/.*',  MainPage),
                                      ('/board/.*', Board),
                                      ('/subject/.*', Subject),
                                      ('/post/.*', Post),
                                      ('/test/.*', Test),
                                      ('/ipad/.*', iPad),
                                      ('/ipost/.*', iPost),
                                      ('/iboard/.*', iBoard),
                                      ('/isubject/.*', iSubject),
                                      ('/config/.*', Config),
                                      ], debug=True)

def main():
    run_wsgi_app(application)

if (__name__ == '__main__'):
    main()
