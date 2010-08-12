# emacs-mode: -*- python-*-
# -*- coding: utf-8 -*-
# author: cangelzz@smth
# last-modified: 2010-07-12

from google.appengine.ext import webapp 
from google.appengine.api import images
from google.appengine.ext import db
from google.appengine.runtime.apiproxy_errors import RequestTooLargeError
from google.appengine.runtime import DeadlineExceededError
from google.appengine.api.urlfetch_errors import *
from random import random
import re 
from define import board2chs, favor, Favor, top90_group
from common import *
from util import *
import base64
import logging

DEBUG = False

myHeader = commonHeader + '<script src="/static/mysort.js"></script>' + "</head><body>"

from google.appengine.api import users
def _login_info(request, device=None):
    def _nick(user):
        nick = user.nickname()
        inx = nick.find("@")
        return (inx == -1) and nick or nick[:inx]
    user = users.get_current_user()
    if user:
        url = users.create_logout_url(request.path)
        if device == "ipad":
            html = "<a class='login' href='/config/ipad/'>Config</a><a class='login' href='%s'>Logoff</a>" % url
        else:
            html = ", %s<a class='login' href='%s'>Out</a><a class='login' href='/config/'>C</a>" % (_nick(user), url)
    else:
        url = users.create_login_url(request.path)
        if device == "ipad":
            html = "<a class='login' href='%s'>Login</a>" % url
        else:
            html = ", Guest<a class='login' href='%s'>In</a>" % url
    
    if device == "ipad": return html[html.find("<"):].replace("/config/", "/config/ipad/")
    return html

def _user(email="anonymous@gmail.com"):
    user = users.get_current_user()
    if not user:
        user = users.User(email)
    return user
    
class Config(webapp.RequestHandler):
    def get(self):
        if self.request.path.find("ipad") == -1: addpath = "ipad/"
        else: addpath = ""
        user = users.get_current_user()
        config = db.GqlQuery("SELECT * FROM Favor WHERE user=:1", user).get()
        favorstext = ""
        chk_value = ""
        if config:
            favorstext = ",".join(config.favorlist)
            chk_value = config.sort == "on" and "checked" or ""
        html = """<h1>Favorites</h1>""" + nav_common + """<form action="/config/%s" method="post"><ul>
<li><textarea name="favors" id="favors" />%s</textarea></li>
<li><label for="sort">Sort</label><input type="checkbox" name="sort" id="sort" checked="%s" /></li>
<li><input type="submit" value="Save" /></li></ul>
</form>
""" % (addpath, favorstext, chk_value)

        print_all(self, [myHeader, html, myFooter])

    def post(self):
        user = users.get_current_user()
        if self.request.path.find("ipad") == -1: addpath = "ipad/"
        else: addpath = ""
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
            self.redirect("/" + addpath)
                

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
            newlist = sorted([i.encode() for i in config.favorlist], key=str.lower)
            return False, newlist
        else:
            return False, favor

class MainPage(webapp.RequestHandler):
    def get(self):
        head = "<h1>Welcome%s</h1>" % _login_info(self.request)
        navlink = """<h1 class="navjump"><input id='boardtogo' type="text" /><a onclick="this.href='/board/'+document.getElementById('boardtogo').value+'/6'" class='btnGo'>Go</a></h1>"""
        page = ['<ul class="boards">']

        default, favorlist = _favor()
        for b in ["top10", "top90"] + favorlist:
            chsname = b in board2chs and board2chs[b] or ""
            page.append("<li><a href='/board/%s/6'><div style='display:inline-block'>%s</div><div style='display:inline-block;float:right'>%s</div></a></li>" % (b, b.upper(), chsname))

        page.append("</ul>")
        print_all(self, [myHeader, head, navlink, "".join(page), myFooter.replace("<!-->", copyright.replace("<!-->","<a href='/jj/'>jj</a><a href='/ipad/'>ipad</a>"))])


def smartboard(b):
    if b in board2chs.keys(): return b, b
    else:
        for bs in sorted(board2chs.keys()):
            if b in bs:
                return bs, b
        return b, b

def _rss(category, idx=None):
    page = ["<ul class='threads'>"]
    if category == "top10":
        url = "http://www.newsmth.net/rssi.php?h=1"
    else:
        url = "http://www.newsmth.net/rssi.php?h=2&s=%d" % idx
        page.append("<li class='group'>"+ category +"</li>")

    try:
        result = fetch(url)
    except DownloadError:
        return "Download error: <span style='red'>%s</span>" % url
    content = result.content
    bname_and_id = re.findall("<link>.*?(?<=board=)(\w+).*?gid=(\d+)", content)
    title_and_author =  re.findall("<description>.*?:\s(.*?),.*?<br/>.*?:\s(.*?)<br/>",content)

    for g1, g2 in zip(bname_and_id, title_and_author):
        page.append("<li><a href='/subject/%s/%s'>%s&nbsp;&nbsp;<span class='author'>%s</span> <span class='boardinth'>[%s]</span></a></li>" % (g1[0].lower(), g1[1], g2[1], g2[0], g1[0]))
    page.append("</ul>")

    return "".join(page)

def _board(path, rtype=0):
        #  2     3    4
        # /board/type/page
        paras = path.split('/')
        try:
            board = paras[2]
            if (len(paras) == 3):
                paras.append("6")

            if (len(paras) == 4):
                isLast = True
                pagetogo = ""
            else:
                isLast = False
                pagetogo = "&page=" + paras[4]
        except IndexError:
            page = page_404.replace("<!-->", r"路径参数错误；<span style='color:red'>%s</span>" % path)
            return "", nav_common, page

        head = "<h1 id='boardh1'>%s</h1>" % board.upper()
        if rtype == 1:
            navlink = ""
        else:
            navlink = "<h1 class='nav'><a href='javascript:history.go(-1)' class='btnLeft0'>&lt;</a><a class='btnCenter0' href='/'>H </a></h1>"
        navlink_top = head + navlink

        if board == "top10":
            return navlink_top, navlink, _rss(board)

        if board == "top90":
            page = []
            for group, idx in top90_group:
                page.append(_rss(group, idx))
            return navlink_top, navlink, "".join(page)


        board, oldboard = smartboard(board.lower())

        head = "<h1 id='boardh1'>%s</h1>" % board.upper()

        if paras[3] == "0":
            ftype = ""
            boardlink = "<a class='btnCenter0 left36 btnCenterChosen' href='/board/%s/0'>N </a><a class='btnCenter0 left36' href='/board/%s/6'>S </a>" % (board, board)
        else:
            ftype =  "&ftype=" + paras[3]
            boardlink = "<a class='btnCenter0 left36' href='/board/%s/0'>N </a><a class='btnCenter0 left36 btnCenterChosen' href='/board/%s/6'>S </a>" % (board, board)

        url = 'http://www.newsmth.net/bbsdoc.php?board=' + board + ftype + pagetogo

        result = fetch(url)
        content = convertFromGB2312ToUTF8(result.content)
        posts = re.findall("c\\.o\\((\\d+),(\\d+),'(.*?)','(.*?)',(\\d+),'(.*?)',(\\d+),\\d+,\\d+\\)", content)
        m = re.search("docWriter.*?(\\d+),\\d+,\\d+,\\d+,(\\d+),", content)
        if not m:
            msg = r"错误的讨论区: <span style='color:red'>%s</span>" % board
            page = page_404.replace("<!-->", msg)
            return "", nav_common, page
        page = m.group(2)

        lastPage = "/".join(["board", board, paras[3], str(int(page)-1)])
        nextPage = "/".join(isLast and ["board", board, paras[3]] or ["board", board, paras[3], str(int(page) + 1)])

        if (isLast):
            navlink = "<h1 class='nav'><a href='/%s' class='btnLeft0'>&lt;</a><a href='javascript:sortul(\"threads_ul\")' class='btnCenterLeft btnSortAZ'>◇</a><a class='btnCenter0 left50' href='/'>H </a>%s</h1>" % (lastPage, boardlink)
        else:
            navlink = "<h1 class='nav'><a href='/%s' class='btnLeft0'>&lt;</a><a href='javascript:sortul(\"threads_ul\")' class='btnCenterLeft btnSortAZ'>◇</a><a class='btnCenter0 left32' href='/'>H </a>%s<a href='/%s' class='btnRight0'>&gt;</a></h1>" % (lastPage, boardlink.replace("left36","left18"), nextPage)

        navlink_top = head + navlink
        page = ["<ul class='threads' id='threads_ul'>"]

        def _classname(mark, title, rtype):
            classes = []
            if "@" in mark: classes.append("att")
            if rtype == "0" and not title.startswith("Re: "): classes.append("mainsub")
            if len(classes) == 0:
                return ""
            else:
                return " class=\"%s\"" % (" ".join(classes))

        for p in posts:
            classname = _classname(p[3], p[5], paras[3])
            if paras[3] == "0":
                page.append(("<li%s><a href='/post/%s/%s'>%s&nbsp;&nbsp;<span class='author'>%s</span></a></li>" % (classname, m.group(1), p[0], p[5], p[2])))
            else:
                page.append(("<li%s><a href='/subject/%s/%s&lz=%s'>%s&nbsp;&nbsp;<span class='author'>%s</span></a></li>" % (classname, board, p[0], p[2], p[5], p[2])))

        page.append("</ul>")

        return navlink_top, navlink, "".join(page)

class Board(webapp.RequestHandler):
    def get(self):
        navlink_top, navlink, page = _board(self.request.path.rstrip("/"))
        print_all(self, [myHeader, navlink_top, page, navlink, myFooter])

class iBoard(webapp.RequestHandler):
    def get(self):
        navlink_top, navlink, page = _board(self.request.path.rstrip("/"), 1)
        print_all(self, [navlink_top, page, navlink])

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
    try:
        result = fetch(url)
    except DownloadError:
        return "Download error: <span style='red'>%s</span>" % url
    content = filterText(convertFromGB2312ToUTF8(result.content))
    if re.search(r"<title>发生错误</title>", content):
        return r"错误的文章号,原文可能已经被删除"
    try:
        title = re.search(r"标  题: (.*?)\\n", content).group(1)
        ids = re.search(r"conWriter.*?'([\w\d]+)',\s(\d+),\s(\d+),\s(\d+),\s(\d+)", content).groups()
        au = re.search(r"[发寄]信人: (.*?\)),?", content).group(1) #search author
        m = re.search(r"(来  源|, 站内|, 转信).*?(\\n)+(.*?)(\\n)+--", content, (re.MULTILINE | re.DOTALL))  #search StationIn #fix zhannei in nickname
    except AttributeError:
        import traceback
        return "<pre>%s</pre>" % traceback.format_exc()

    reply = ""
    refer = ""
    attpart = ""
    if m:
        s = re.sub(r"(\\n)+", "<br/>", m.group(3).strip("\\n "))
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
            if int(att[1]) > 1000000:
                attpart = attpart + "<br><span style='color:crimson'>[TOO_LARGE_IMAGE]</span>"
                continue
            fname = att[0]
            ext = fname[fname.rfind("."):]
            extL = ext.lower()
            if extL == ".jpg" or extL == ".jpeg" or extL == ".bmp" or extL == ".png" or extL == ".gif":
                att_url = "http://att.newsmth.net/att.php?n.%s.%s.%s" % (bid, id, att[2]) + ext
                try:
                    bindata = fetch(url=att_url, method=urlfetch.GET, deadline=10).content
                except DownloadError:
                    attpart = attpart + "<br><span style='color:red'>[DOWNLOAD_ERROR]</span>"
                    continue
                except DeadlineExceededError:
                    attpart = attpart + "<br><span style='color:red'>[DEADLINE_EXCEEDED_ERROR]</span>"
                    continue
                img = images.Image(bindata)
                if img.width > 300:
                    img.resize(300)
                else:
                    img.resize(img.width)
                try:
                    resizedata = img.execute_transforms(images.JPEG)
                    base64data = base64.encodestring(resizedata)
                    attpart = attpart + "<br/><img src=\"data:image/jpeg;base64," + base64data + "\">"
                except RequestTooLargeError: 
                    attpart = attpart + "<br><span style='color:red'>[TOO_LARGE_IMAGE]</span>"
                except Exception, err:
                    attpart = attpart + "<br>%s" % err.message
    
    return list(ids) + [title, au, reply, refer, attpart]
    # board, bid, id, gid, reid, title, author, reply, refer, attach
    # 0      1    2   3    4     5      6       7      8      9
    #                                   0       1      2      3
def _content_html(li, rtype, lz=None, option={}):
    if lz and li[0].find(lz) != -1:
        au_html = "<span class='authorlz'>%s</span>: " % li[0]
    else:
        au_html = "<span class='author'>%s</span>: " % li[0]

    if rtype == 1:
        return au_html + "<span style='margin:0px;padding:0px;'>%s<span style='color:grey;'><br/>%s</span>%s</span>" % (li[1], li[2], li[3])
    elif rtype == 2:
        refer = ""
        if li[2] != "":
            if option.get("hideRefer", True):
                random_id = str(random())[2:]
                refer = "<a id='%s' class='normal' href=\"javascript:document.getElementById('%s').firstElementChild.style.display='inline'\">+" % (random_id, random_id) + "<span style='color:grey;display:none;'><br/>" + li[2] + "</span></a>"
            else:
                refer = "<span style='color:grey'><br/>" + li[2] + "</span>"
        return au_html + "<span style='margin:0px;padding:0px;'>%s" % (li[1]) + refer + li[3] + "</span>"

def _check_lz(m):
    if lz and m.group(1).find(lz) != -1:
        return "<span class='authorlz'>%s</span>: " % m.group(1)
    else:
        return "<span class='author'>%s</span>: " % m.group(1)

def _content_collection(bid, id, option={}):
    url = ('http://www.newsmth.net/bbscon.php?bid=%s&id=%s' % (bid, id))
    try:
        result = fetch(url)
    except DownloadError:
        return "Download error: <span style='red'>%s</span>" % url
    content = filterText(convertFromGB2312ToUTF8(result.content))
    m = re.search(r"站内(.*)o.h\(0\)", content, (re.MULTILINE | re.DOTALL))
    if m:
        s = re.sub(r"(\\n)+", "<br/>", m.group(1).strip("\\n "))
        s = re.sub("<br/>\s+", "", s)
        hl = "☆─────────────────────────────────────☆"
        ps = s.split(hl)[1:]
        lz = re.search("(^[\w\d]+.*?\)).*?提到:", ps[0]).group(1)
        result = []
        for p in ps:
            inx = p.find("【")
            if inx > 0:
                st = p[inx:]
                refergroup = st.split("<br/>")
                st = len(refergroup) > 3 and "<br/>".join(refergroup[:3]) or st
                if option.get("hideRefer", True):
                    random_id = str(random())[2:]
                    p = p[:inx].replace("<br/>", "") + "<a id='%s' class='normal' href=\"javascript:document.getElementById('%s').firstElementChild.style.display='inline'\">+" % (random_id, random_id) + "<span style='color:grey;display:none;'>" + "<br/>" + st + "</span></a>"
                else:
                    p = p[:inx].replace("<br/>", "") + "<span style='color:grey'><br/>" + st + "</span>"
            au = re.search("(^[\w\d]+.*?\)).*?提到:", p)
            if au.group(1).find(lz) != -1:
                result.append(re.sub("(^[\w\d]+.*?\)).*?提到:", r"<span class='authorlz'>\1</span>: ", p))
            else:
                result.append(re.sub("(^[\w\d]+.*?\)).*?提到:", r"<span class='author'>\1</span>: ", p))

            #r"<span class='author'>\1</span>: "
            #result.append(re.sub("(^[\w\d]+.*?\)).*?提到:", _check_lz(lz), p))
        return "<li>" + "</li><li>".join(result) + "</li>"

def _subject(path, rtype=0, lz=None, option={}):
        m_lz = re.search("%26lz%3D(.*)", path)
        if (m_lz):
            lz = m_lz.group(1)
            path = path.replace(m_lz.group(), "")
        paras = path.split('/')
        try:
            board,gid = paras[2],paras[3]
            if (len(paras) == 4):
                pagenum = ""
            else:
                pagenum = "&start=" + gid + "&pno=" + paras[4]
        except IndexError:
            page = page_404.replace("<!-->", r"路径参数错误；<span style='color:red'>%s</span>" % path)
            return "", nav_common, page

        url = 'http://www.newsmth.net/bbstcon.php?board=%s&gid=%s%s' % (board, gid, pagenum)
        try:
            result = fetch(url)
        except DownloadError:
            return "", nav_common, page_404.replace("<!-->", "Download error: <span style='red'>%s</span>" % url)
        t = re.search("<title>.*?-.*?-(.*?)</title>", convertFromGB2312ToUTF8(result.content))
        m = re.search("tconWriter.*?,(\\d+),\\d+,\\d+,(\\d+),(\\d+),", result.content)

        if not m:
            msg = r"错误的文章号,原文可能已经被删除"
            page = page_404.replace("<!-->", msg)
            return "", nav_common, page

        totalPage = int(m.group(2))
        curPage = int(m.group(3))

        posts = re.findall('''\[(\d+),'(.*?)'\]''', result.content)
        lz = (curPage == 1) and posts[0][1] or lz
        lz_link = lz and "&lz="+lz or ""

        def makejumplist(c, t, bname, gid, lz=lz_link):
            s = []
            i = 1
            while i <= t:
                if i == c:
                    s.append(str(i))
                else:
                    s.append("<a href='/subject/%s/%s/%d%s'>%s</a>" % (bname, gid, i, lz,i))
                i = i + 1
            return "&nbsp;&nbsp;".join(s)
        boardLink = "<a href='javascript:sortul(\"posts_ul\")' class='btnCenterLeft btnSortAZ'>◇</a><a class='btnCenter0' href='/board/%s/6' style='{width:%dpx}'>%s</a>" % (board, len(board)*8,board.upper())
        if curPage == 1:
            if curPage == totalPage:
                navlink = "<h1 class='nav' id='snavtop'><a href='javascript:history.go(-1)' class='btnLeft0'>&lt;</a>%s</h1>" % boardLink.replace("btnCenter0", "btnCenter0 left36")
                navlink_bottom = navlink
            else:
                nextPage = "/".join(["subject", board, gid, "2"]) + lz_link
                navlink = "<h1 class='nav'><a href='javascript:history.go(-1)' class='btnLeft0'>&lt;</a>%s<a href='/%s' class='btnRight0'>2</a><a class='btnCenterRight' href=\"javascript:document.getElementById('hidejump').style.display='block'\">J</a></h1><div id='hidejump' class='hidediv'>%s</div>" % (boardLink, nextPage, makejumplist(curPage, totalPage, board, gid))
                navlink_bottom = "<div id='hidejump2' class='hidediv'>%s</div><h1 class='nav'><a href='javascript:history.go(-1)' class='btnLeft0'>&lt;</a>%s<a href='/%s' class='btnRight0'>2</a><a class='btnCenterRight' href=\"javascript:document.getElementById('hidejump2').style.display='block'\">J</a></h1>" % (makejumplist(curPage, totalPage, board, gid), boardLink, nextPage)
        else:
            if curPage == totalPage:
                lastnum = curPage - 1
                lastPage = "/".join(["subject", board, gid, str(lastnum)]) + lz_link
                navlink = "<h1 class='nav'><a href='/%s' class='btnLeft0'>%d</a>%s<a class='btnCenterRight' href=\"javascript:document.getElementById('hidejump').style.display='block'\">J</a></h1><div id='hidejump' class='hidediv'>%s</div>" % (lastPage, lastnum, boardLink.replace("btnCenter0","btnCenter0 left18"), makejumplist(curPage, totalPage, board, gid))
                navlink_bottom = "<div id='hidejump2' class='hidediv'>%s</div><h1 class='nav'><a href='javascript:history.go(-1)' class='btnLeft0'>%d</a>%s<a class='btnCenterRight' href=\"javascript:document.getElementById('hidejump2').style.display='block'\">J</a></h1>" % (makejumplist(curPage, totalPage, board, gid), lastnum, boardLink.replace("btnCenter0","btnCenter0 left18"))
            else:
                lastnum = curPage - 1
                nextnum = curPage + 1
                lastPage = "/".join(["subject", board, gid, str(lastnum)]) + lz_link
                nextPage = "/".join(["subject", board, gid, str(nextnum)]) + lz_link
                navlink = "<h1 class='nav'><a href='/%s' class='btnLeft0'>%s</a>%s<a href='/%s' class='btnRight0'>%s</a><a class='btnCenterRight' href=\"javascript:document.getElementById('hidejump').style.display='block'\">J</a></h1><div id='hidejump' class='hidediv'>%s</div>" % (lastPage, str(lastnum), boardLink, nextPage, str(nextnum), makejumplist(curPage, totalPage, board, gid))
                navlink_bottom = "<div id='hidejump2' class='hidediv'>%s</div><h1 class='nav'><a href='/%s' class='btnLeft0'>%s</a>%s<a href='/%s' class='btnRight0'>%s</a><a class='btnCenterRight' href=\"javascript:document.getElementById('hidejump2').style.display='block'\">J</a></h1>" % (makejumplist(curPage, totalPage, board, gid), lastPage, str(lastnum), boardLink, nextPage, str(nextnum))

        navlink =  "<h1>%s</h1>" % t.group(1) + navlink
        navlink_bottom = navlink_bottom.replace("snavtop", "snavbottom")

        page = "<ul class='posts' id='posts_ul'>"

        #different handle SameSubject posts
        bid = m.group(1)
        if t.group(1).find("合集") > 0:
            result = _content_collection(bid, posts[0][0], option=option)
            page += result
            posts = posts[1:]

        for p in posts:
            try:
                content = _content(bid, p[0])
                if type(content) == str:
                    page = page_404.replace("<!-->", content)
                    return "", nav_common, page
                result = _content_html(content[6:], 2, lz=lz, option=option)
            except DeadlineExceededError:
                result = r"<span style='color:red'>[DEADLINE EXCEEDED]</span>"
            page += "<li>%s</li>" % result
        page += "</ul>"

        return navlink, navlink_bottom, page

class Subject(webapp.RequestHandler):
    def get(self):
        if re.search("(webkit|safari|chrome)", self.request.headers["User-Agent"], re.I):
            hideRefer = True
        else:
            hideRefer = False
        navlink, navlink_bottom, page = _subject(self.request.path.rstrip("/"), option={"hideRefer": hideRefer})
        print_all(self, [myHeader, navlink, page, navlink_bottom, myFooter])

class iSubject(webapp.RequestHandler):
    def get(self):
        navlink, navlink_bottom, page = _subject(self.request.path.rstrip("/"), 1)
        print_all(self, [navlink, page, navlink_bottom])

def _post(path, rtype=0):
        paras = path.split('/')
        try:
            bid,id = paras[2],paras[3]
            if len(paras) == 5:
                page = "&p=" + paras[4]
            else:
                page = ""
        except IndexError:
            page = page_404.replace("<!-->", r"路径参数错误；<span style='color:red'>%s</span>" % path)
            return "", nav_common, page

        c = _content(bid, id, page)
        if type(c) == str:
            page = page_404.replace("<!-->", c)
            return page, nav_common

        board, bid, id, gid, reid, title = c[:6]
        lastSubPost = "/".join(["post", bid, id, "tp"])
        nextSubPost = "/".join(["post", bid, id, "tn"])
        firstPost = "/".join(["post", bid, gid])
        expandPost = "/".join(["subject", board, gid])
        boardlink = "/".join(["board", board, "0"])
        navlink = "<h1>%s</h1>" %title + "<h1 class='nav'><a href='/%s' class='btnLeft0'>&lt;</a><a href='/%s' class='btnCenterLeft'>1</a><a href='/%s' class='btnCenterLeft'>+</a><a href='/%s' class='btnCenter0 btnCenter2'>%s</a><a href='/%s' class='btnRight0'>&gt;</a></h1>" % (lastSubPost,firstPost,expandPost,boardlink,board.upper(),nextSubPost)
        return navlink, "<ul class='posts'><li>" + _content_html(c[6:], 1) + "</li></ul>"

class Post(webapp.RequestHandler):
    def get(self):
        navlink, page = _post(self.request.path)
        print_all(self, [myHeader, navlink, page, myFooter])

class iPost(webapp.RequestHandler):
    def get(self):
        navlink, page = _post(self.request.path, 1)
        print_all(self, [navlink, page])

class Test(webapp.RequestHandler):
    def get(self):
        url = "http://www.newsmth.net/rssi.php?h=1"
        result = fetch(url)
        content = convertFromGB2312ToUTF8(result.content)
        self.response.out.write(myHeader)
        self.response.out.write(content)

ipadHeader = """<html><head>
<title>HIME - iPad</title>
<link rel="Stylesheet" href="/static/my.css" media="screen" type="text/css" />
<meta http-equiv="content-type" content="text/html; charset=utf-8">
<meta name="viewport" content="width=device-width, user-scalable=no">
<meta name="viewport" content="initial-scale=1.0; maximum-scale=1.0; user-scalable=0;" /> 
<script src="/static/jquery.js"></script>
<script src="/static/jScrollTouch.js"></script>
<script src="/static/jquery.ba-hashchange.min.js"></script>
<script src="/static/ipad.js"></script>
<script src="/static/mysort.js"></script>
""" + tracking + """</head><body class="webkit">"""

def makenav(favorlist):
    s = []
    for b in favorlist:
        s.append("<li><a id='%s' class='hBoard' href=\"/board/%s/6\">%s</a></li>" % ("hb"+b.lower(), b.lower(), b.upper()))
    return "<ul id='example-two'>" + "".join(s) + "</ul>"
    #return "<span style='color:gray;'>|</span>".join(s)

ipadBody = """
<div id="navboard"><div class="navleft"><a href="javascript:nav2left()">&lt;</a></div><div id="navcon"><!--B></div><div class="navright"><a href="javascript:nav2right()">&gt;</a></div><div class="navright"><a href="javascript:showTool();">+</a></div></div>
<div id="progress" style="display:none"><span>loading ...</span></div>
<div id="main">

  <div id="divThreads"></div>
  <div id="divPosts"></div>
</div>
<div id="toolbox"><!--T></div>"""

ipadJump = """<h1 class="navjump"><input id='boardtogo' type="text" /><a href="javascript:loadBoard('/board/'+$('#boardtogo').val()+'/6')" class='btnGo'>Go</a></h1>"""

class iPad(webapp.RequestHandler):
    def get(self):
        default, favorlist = _favor()
        body = ipadBody.replace("<!--B>", makenav(["top10","top90"] + favorlist))
        loginhtml = "<div id='ipadcon'>" + _login_info(self.request, "ipad") + "</div>"
        toolhtml = ipadJump + loginhtml
        print_all(self, [ipadHeader, body.replace("<!--T>", toolhtml), ipadFooter])
