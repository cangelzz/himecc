# emacs-mode: -*- python-*-
# -*- coding: cp936 -*-

from google.appengine.ext import webapp 
from google.appengine.ext.webapp.util import run_wsgi_app 
from google.appengine.api.urlfetch import fetch 
import re 
#from define import id2board, board2id, favor
favor = {"20": "战色逆乐园", "3": "耽美闲情"}
board2name = {"20": "战色逆乐园", "3": "耽美闲情"}

myContentType = "text/html; charset='utf-8'"
myHeader = """<html><header>
<link rel="Stylesheet" href="/static/my.css" media="screen" type="text/css" />
<meta name="viewport" content="width=device-width, user-scalable=no">
<meta name="viewport" content="initial-scale=1.0; maximum-scale=1.0; user-scalable=0;" /> 
</header><body>"""
myFooter = """</body></html>"""

def toUTF8(onestr):
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
        self.response.out.write("<h1>%s</h1>" % toUTF8("晋江文学城"))
        self.response.out.write('<ul class="boards">')
        for b in favor.items():
            self.response.out.write("<li><a href='/jjboard/%s'>%s</a></li>" % (b[0], toUTF8(b[1])))
        self.response.out.write("</ul>")
        self.response.out.write(myFooter)


class Board(webapp.RequestHandler):
    def get(self):
        paras = self.request.path.split('/')
        board = paras[2]
        if (len(paras) == 3):
            isLast = True
            pagetogo = ""
        else:
            isLast = False
            pagetogo = "&page=" + paras[3]
        url = "http://bbs.jjwxc.net/board.php?board=" + board + "&page=" + pagetogo
        result = fetch(url)
        content = toUTF8(result.content)
        p =re.compile("href=\"(show.*?)id=(\\d+).*?\".*?>(.*?)&nbsp.*?<td>&nbsp;(.*?)</td>", re.MULTILINE|re.DOTALL)
        posts = re.findall(p, content)
        pages = re.search("<font color=.#FF0000.>(\\d+)</font>.*?<font color=.#FF0000.>(\\d+)</font>", content)
        totalPage = int(pages.group(1))
        curPage = int(pages.group(2))

        if curPage == 1:
            navlink = "<h1 class='nav'><a href='/jj/' class='btnCenter' style='{width:66px}'>Home</a><a href='/jjboard/%s/2' class='btnRight0'>2</a></h1>" % board;
        else:
            nextPage = curPage + 1
            lastPage = curPage - 1
            navlink = "<h1 class='nav'><a href='/jjboard/%s/%d' class='btnLeft0'>%d</a><a href='/jj/' class='btnCenter' style='{width:66px}'>Home</a><a href='/jjboard/%s/%d' class='btnRight0'>%d</a></h1>" % (board, lastPage, lastPage, board, nextPage, nextPage);


        self.response.headers['Content-Type'] = myContentType
        self.response.out.write(myHeader)
        self.response.out.write("<h1>%s</h1>" % toUTF8(board2name[board]))

        self.response.out.write(navlink)
        self.response.out.write("<ul class='threads'>")
        for p in posts:
            self.response.out.write("<li><a href='/jjsubject/%s/%s'>%s&nbsp;&nbsp;<span class='author'>%s</span></a></li>" % (board, p[1], p[2], p[3]))
        self.response.out.write("</ul>")
        self.response.out.write(navlink)
        self.response.out.write(myFooter)


def getContent(bid, id):
    url = ('http://www.newsmth.net/bbscon.php?bid=%s&id=%s' % (bid, id))
    result = fetch(url)
    content = convertFromGB2312ToUTF8(result.content)
#    m = re.search(r"绔欏唴(.*?)銆", content, (re.MULTILINE | re.DOTALL))
#    if not m:
    au = re.search(r"\xe5\x8f\x91\xe4\xbf\xa1\xe4\xba\xba: (.*?),", content)
    m = re.search(r"绔欏唴(.*?)--", content, (re.MULTILINE | re.DOTALL))
    if m:
        s = re.sub(r"^(\\n)+", "", m.group(1).strip())
        s = re.sub(r"(\\n)+", "<br />", s)
#        s = m.group(1).replace(r"\n", "<br />")
        inx = s.find("\xe3\x80\x90")
        if inx:
            s = s[:inx] + "<span style='color:grey'>" + s[inx:].replace(">>", ">") + "</span>"

    return "<span class='author'>" + au.group(1) + "</span>: " + s #m.group(1)


class Subject(webapp.RequestHandler):
    def get(self):
        paras = self.request.path.split('/')
        board,id = paras[2],paras[3]
        if (len(paras) == 4):
            pagenum = ""
        else:
            pagenum = "&page=" + paras[4]

        self.response.headers['Content-Type'] = myContentType
        url = 'http://bbs.jjwxc.net/showmsg.php?board=%s&id=%s%s' % (board, id, pagenum)
        result = fetch(url)
        content = toUTF8(result.content)
        sub = re.search("\xe4\xb8\xbb\xe9\xa2\x98\xef\xbc\x9a(.*?)</td>", content).group(1)
        p_total = re.search("\xe5\x85\xb1(\\d+)\xe9\xa1\xb5.*?<b>\[(\\d+)\]</b>", content)
        boardLink = "<a class='btnCenter' href='/jjboard/%s' style='{width:%dpx}'>%s</a>" % (board, len(board2name[board])*8, toUTF8(board2name[board]))
        if p_total:
            totalPage = int(p_total.group(1))
            curPage = int(p_total.group(2))
            if curPage == 1:
                nextpage = "/jjsubject/" + board + "/" + id + "/" + "1"
                navlink = "<h1 class='nav'>%s<a href='%s' class='btnRight0'>2</a></h1>" % (boardLink, nextpage)

            else:
                if curPage == totalPage:
                    lastnum = curPage - 1
                    navlink = "<h1 class='nav'><a href='javascript:history.go(-1)' class='btnLeft0'>%d</a>%s</h1>" % (lastnum, boardLink)
                else:
                    lastnum = curPage - 2
                    nextnum = curPage
                    if lastnum == 0:
                        lastPage = "/jjsubject/" + board + "/" + id
                    else:
                        lastPage = "/jjsubject/" + board + "/" + id + "/" + str(lastnum)
                    nextPage = "/jjsubject/" + board + "/" + id + "/" + str(nextnum)
                    navlink = "<h1 class='nav'><a href='%s' class='btnLeft0'>%s</a>%s<a href='%s' class='btnRight0'>%s</a></h1>" % (lastPage, str(lastnum+1), boardLink, nextPage, str(nextnum+1))
        else:
            navlink = "<h1 class='nav'><a name='top' href='javascript:history.go(-1)' class='btnLeft0'>Back</a>%s</h1>" % boardLink

        p = re.compile("<td class=.read.>(.*?)</td>.*?<td>(.*?)</td>", re.MULTILINE|re.DOTALL)
        posts = re.findall(p, content)
        page = "<ul class='posts'>"
        for p in posts:
            u = p[1].replace(r"\t", "")
            c = p[0].replace(r"\t", "")
            page += "<li><span class='author'>%s</span><a href='#top' class='normal'>\xe2\x96\xb3</a><br />%s</li>" % (u, c)
        page += "</ul>"
        page = re.sub("</?font.*?>", "", page)
        page = re.sub("</?div.*?>", "", page)
        self.response.out.write(myHeader)
        self.response.out.write("<h1>%s</h1>" % sub)
        self.response.out.write(navlink)
        self.response.out.write(page)
        self.response.out.write(navlink)
        self.response.out.write(myFooter)


class Post(webapp.RequestHandler):
    def get(self):
        paras = self.request.path.split('/')
        bid,id = paras[2],paras[3]
        self.response.headers['Content-Type'] = myContentType
        content = getContent(bid, id)
        self.response.out.write(myHeader)
        self.response.out.write(content)
        self.response.out.write(myFooter)


application = webapp.WSGIApplication([('/jj/.*',  MainPage),
                                      ('/jjboard/.*', Board),
                                      ('/jjsubject/.*', Subject),
                                      ], debug=True)

def main():
    run_wsgi_app(application)

if (__name__ == '__main__'):
    main()
