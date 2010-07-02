# emacs-mode: -*- python-*-
# -*- coding: utf-8 -*-
# author: cangelzz@smth
# last-modified: 2010-01-12

from google.appengine.ext import webapp 
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import urlfetch
#from google.appengine.api.urlfetch import fetch
from google.appengine.api import images
from random import random
import re 
from define import id2board, board2id, favor, favor2chs

myContentType = "text/html; charset='utf-8'"
myHeader = """<html><head>
<link rel="Stylesheet" href="/static/my.css" media="screen" type="text/css" />
<meta name="viewport" content="width=device-width, user-scalable=no">
<meta name="viewport" content="initial-scale=1.0; maximum-scale=1.0; user-scalable=0;" /> 
</head><body>"""
myFooter = """</body></html>"""

def fetch(url, payload=None, method=urlfetch.GET, headers={}, allow_truncated=False, follow_redirects=True, deadline=10):
    return urlfetch.fetch(url, payload=None, method=urlfetch.GET, headers={}, allow_truncated=False, follow_redirects=True, deadline=deadline)

def convertFromGB2312ToUTF8(onestr):
    newstr = onestr
    try:
        newstr = unicode(newstr, 'cp936', 'ignore')
    except:
        pass
    return newstr.encode('utf-8', 'ignore')


class MainPage(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = myContentType
        self.response.out.write(myHeader)
        self.response.out.write("<h1>Newsmth</h1>")
        self.response.out.write("""<h1 class="navjump"><input id='boardtogo' type="text" /><a onclick="this.href='/board/6'+document.getElementById('boardtogo').value" class='btnRight0'>Go</a></h1>""")
        self.response.out.write('<ul class="boards">')
        for b in favor:
            self.response.out.write("<li><a href='/board/%s/6'><div style='display:inline-block'>%s</div><div style='display:inline-block;float:right'>%s</div></a></li>" % (b, b.upper(), favor2chs[b]))
        self.response.out.write("</ul>")
        self.response.out.write(myFooter)


class Board(webapp.RequestHandler):
    def get(self):
        #  2     3    4
        # /board/type/page
        paras = self.request.path.split('/')
        board = paras[2]
        if (len(paras) == 4):
            isLast = True
            pagetogo = ""
        else:
            isLast = False
            pagetogo = "&page=" + paras[4]

        if board == "top10":
            url = "http://www.newsmth.net/rssi.php?h=1"
            result = fetch(url)
            #content = convertFromGB2312ToUTF8(result.content)
            content = result.content
            bname_and_id = re.findall("<link>.*?(?<=board=)(\w+).*?gid=(\d+)", content)
            title_and_author =  re.findall("<description>.*?:\s(.*?),.*?<br/>.*?:\s(.*?)<br/>",content)

            self.response.headers['Content-Type'] = myContentType
            self.response.out.write(myHeader)
            self.response.out.write("<h1>%s</h1>" % board.upper())
            navlink = "<h1 class='nav'><a href='javascript:history.go(-1)' class='btnLeft0'>&lt;</a><a class='btnCenter' href='/' style='{width:66px}'>Home</a></h1>"
            self.response.out.write(navlink)
            self.response.out.write("<ul class='threads'>")
            for g1, g2 in zip(bname_and_id, title_and_author):
                self.response.out.write(("<li><a href='/subject/%s/%s'>%s&nbsp;&nbsp;<span class='author'>%s</span> <span class='boardinth'>[%s]</span></a></li>" % (g1[0], g1[1], g2[1], g2[0], g1[0])))
            self.response.out.write("</ul>")
            self.response.out.write(navlink)
            self.response.out.write(myFooter)
            return

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
        #lastPage = "/board/" + board + "/" + paras[3] + "/" + str(int(page) - 1)
        #nextPage = isLast and "/board/" + board + paras[3] or "/board/" + board + "/" + paras[3] + "/" + str(int(page) + 1)
        lastPage = "/".join(["board", board, paras[3], str(int(page)-1)])
        nextPage = "/".join(isLast and ["board", board, paras[3]] or ["board", board, paras[3], str(int(page) + 1)])

        self.response.headers['Content-Type'] = myContentType
        self.response.out.write(myHeader)
        self.response.out.write("<h1>%s</h1>" % board.upper())

        if (isLast):
            navlink = "<h1 class='nav'><a href='/%s' class='btnLeft0'>&lt;</a><a class='btnCenter' href='/' style='{width:66px}'>Home</a>%s</h1>" % (lastPage, boardlink)
        else:
            navlink = "<h1 class='nav'><a href='/%s' class='btnLeft0'>&lt;</a><a class='btnCenter' href='/' style='{width:66px}'>Home</a>%s<a href='/%s' class='btnRight0'>&gt;</a></h1>" % (lastPage, boardlink, nextPage)

        self.response.out.write(navlink)
        self.response.out.write("<ul class='threads'>")
        for p in posts:
            if paras[3] == "0":
                self.response.out.write(("<li><a href='/post/%s/%s'>%s&nbsp;&nbsp;<span class='author'>%s</span></a></li>" % (m.group(1), p[0], p[5], p[2])))
            else:
                self.response.out.write(("<li><a href='/subject/%s/%s'>%s&nbsp;&nbsp;<span class='author'>%s</span></a></li>" % (board, p[0], p[5], p[2])))

        self.response.out.write("</ul>")
        self.response.out.write(navlink)
        self.response.out.write(myFooter)

def filterText(s):
    telnet_ctrl = re.compile("[[0-9;]+m")
    http_link = re.compile("(http://.*?)[^\w\d.+-=/_&^%?<]")
    #s = re.sub("(http://.*?)[^\w\d.+-=/_&^%?]", r"<a href='\1' target='_blank' class='httplink'>\1</a>", s.replace("\\r","").replace(r"\/", "/"))
    s = re.sub(r"\\/(?!\>)", "/", s)
    s = telnet_ctrl.sub("", s.replace("\\r",""))
    s = re.sub(r"【 在 (\w+).*? 的大作中提到: 】\\n", r"【\1】 ", s)
    return s
    return re.sub("(http://.*?)[^\w\d\s.+-=/_&^%?<]", r"<a href='\1' target='_blank' class='httplink'>|\1|</a>", s)

def getContent(bid, id, single=None, page=""):
    url = ('http://www.newsmth.net/bbscon.php?bid=%s&id=%s%s' % (bid, id, page))
    result = fetch(url)
    content = filterText(convertFromGB2312ToUTF8(result.content))
    if single:
        title = re.search(r"标  题: (.*?)\\n", content).group(1)
        ids = re.search(r"conWriter.*?'([\w\d]+)',\s(\d+),\s(\d+),\s(\d+),\s(\d+)", content).groups()
    au = re.search(r"发信人: (.*?),", content) #search author
    m = re.search(r", 站内(.*?)(\\n)+--", content, (re.MULTILINE | re.DOTALL))  #search StationIn #fix zhannei in nickname
    if m:
#        s = re.sub(r"^(\\n)+", "", m.group(1).strip("\\n "))
        s = re.sub(r"(\\n)+", "<br/>", m.group(1).strip("\\n "))
#        s = m.group(1).replace(r"\n", "<br/>")
        inx = s.find("【")
        if inx > 0:
            st = s[inx:]
            refergroup = st.split("<br/>")
            st = len(refergroup) > 3 and "<br/>".join(refergroup[:3]) or st
            #add expand comment
            random_id = str(random())[2:]
            if single:
                s = s[:inx].replace("<br/>", "") + "<span style='color:grey;'><br/>" + st + "</span>"
            else:
                s = s[:inx].replace("<br/>", "") +  "<a id='%s' class='normal' href=\"javascript:document.getElementById('%s').firstElementChild.style.display='inline'\">+" % (random_id, random_id) + "<span style='color:grey;display:none;'><br/>" + st + "</span></a>"
            #s = s[:inx] + "<span style='color:grey;'>" + st + "</span>"
        
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
                resizedata = img.execute_transforms(images.JPEG)
                import base64
                base64data = base64.encodestring(resizedata)
                s = s + "<br/><img src=\"data:image/jpeg;base64," + base64data + "\">"

    if single:
        return list(ids) + [title, "<span class='author'>" + au.group(1) + "</span>: " + "<span style='margin:0px;padding:0px;'>" + s+ "</span>"]
    else:
        return "<span class='author'>" + au.group(1) + "</span>: " + "<span style='margin:0px;padding:0px;'>" + s+ "</span>" #m.group(1)

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

class Subject(webapp.RequestHandler):
    def get(self):
        paras = self.request.path.split('/')
        board,gid = paras[2],paras[3]
        if (len(paras) == 4):
            pagenum = ""
        else:
            pagenum = "&start=" + gid + "&pno=" + paras[4]

        self.response.headers['Content-Type'] = myContentType
        url = 'http://www.newsmth.net/bbstcon.php?board=%s&gid=%s%s' % (board, gid, pagenum)
#        self.response.out.write(((board + '  ') + gid))
        result = fetch(url)
        t = re.search("<title>(.*?)</title>", convertFromGB2312ToUTF8(result.content))
        m = re.search("tconWriter.*?\\d+,\\d+,\\d+,(\\d+),(\\d+),", result.content)

        totalPage = int(m.group(1))
        curPage = int(m.group(2))
        self.response.out.write(myHeader)
        self.response.out.write("<h1>%s</h1>" % t.group(1))

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
                navlink = "<h1 class='nav'><a href='javascript:history.go(-1)' class='btnLeft0'>&lt;</a>%s</h1>" % boardLink
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

        self.response.out.write(navlink)

        posts = re.findall('''\[(\d+),'(.*?)'\]''', result.content)
        page = "<ul class='posts'>"

        #different handle SameSubject posts
        if t.group(1).find("合集") > 0:
            result = getContentHeji(board2id[board.lower()], posts[0][0])
            page += result
            posts = posts[1:]

        for p in posts:
            result = getContent(board2id[board.lower()], p[0])
            page += "<li>%s</li>" % result
        page += "</ul>"
        self.response.out.write(page)
        self.response.out.write(navlink_bottom)
        self.response.out.write(myFooter)


class Post(webapp.RequestHandler):
    def get(self):
        paras = self.request.path.split('/')
        bid,id = paras[2],paras[3]
        if len(paras) == 5:
            page = "&p=" + paras[4]
        else:
            page = ""

        self.response.headers['Content-Type'] = myContentType
        board, bid, id, gid, reid, title, content = getContent(bid, id, "single", page)
        lastSubPost = "/".join(["post", bid, id, "tp"])
        nextSubPost = "/".join(["post", bid, id, "tn"])
        firstPost = "/".join(["post", bid, gid])
        expandPost = "/".join(["subject", board, gid])
        boardlink = "/".join(["board", board, "0"])
        navlink = "<h1 class='nav'><a href='/%s' class='btnLeft0'>&lt;</a><a href='/%s' class='btnCenterLeft'>1</a><a href='/%s' class='btnCenterLeft'>+</a><a href='/%s' class='btnCenter'>%s</a><a href='/%s' class='btnRight0'>&gt;</a></h1>" % (lastSubPost,firstPost,expandPost,boardlink,board.upper(),nextSubPost)

        self.response.out.write(myHeader)
        self.response.out.write("<h1>%s</h1>" % title)
        self.response.out.write(navlink)
        self.response.out.write("<ul class='posts'><li>" + content + "</li></ul>")
        self.response.out.write(myFooter)


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
<script type="text/javascript">
  function init() {
    $('#divThreads').load('/');
    $('#divPosts').load('/board/apple/6');
  }

  function loadBoard(board)
  {
    $('#divThreads').load('/board/' + board + '/6')
  }
</script>
</head><body onload="init()">"""

def makenav():
    s = []
    for b in favor:
        s.append("<div class='hBoard'><a href=\"javascript:loadBoard('%s')\">%s</a></div>" % (b, b.capitalize()))
    return "|".join(s)
    #return " ".join(favor)

ipadBody = """
<div id="navboard"><p>%s</p></div>
<div id="main">

  <div id="divThreads"></div>
  <div id="divPosts"></div>

</div>
""" % makenav()


class iPad(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = myContentType
        self.response.out.write(ipadHeader)
        self.response.out.write(ipadBody)


        self.response.out.write(myFooter)


application = webapp.WSGIApplication([('/',  MainPage),
                                      ('/smth/.*',  MainPage),
                                      ('/board/.*', Board),
                                      ('/subject/.*', Subject),
                                      ('/post/.*', Post),
                                      ('/test/.*', Test),
                                      ('/ipad/.*', iPad),
                                      ], debug=True)

def main():
    run_wsgi_app(application)

if (__name__ == '__main__'):
    main()
