# emacs-mode: -*- python-*-
# -*- coding: utf-8 -*-

from google.appengine.ext import webapp
from util import fetch, print_all
from common import tracking, page_404, copyright
import re 
import logging

favor = {"20": "战色逆乐园", "3": "耽美闲情"}
board2name = {"20": "战色逆乐园", "3": "耽美闲情"}

myHeader = """<link rel="Stylesheet" href="/static/my.css" media="screen" type="text/css" />
<meta http-equiv="content-type" content="text/html; charset=utf-8"> 
<meta name="viewport" content="width=device-width, user-scalable=no">
<meta name="viewport" content="initial-scale=1.0; maximum-scale=1.0; user-scalable=0;" />
</header><body>"""
myFooter = """<div id="footer"></div><!--></body></html>"""

nav_common = "<h1 class='nav'><a href='javascript:history.go(-1)' class='btnLeft0'>&lt;</a><a class='btnCenter btnCenter2' href='/jj/' style='{width:66px}'>Home</a></h1>"

def toUTF8(onestr):
    newstr = onestr
    try:
        newstr = unicode(newstr, 'cp936', 'ignore')
    except:
        pass
    return newstr.encode('utf-8', 'ignore')


class MainPage(webapp.RequestHandler):
    def get(self):
        page = ["<h1>晋江文学城</h1>"]
        page.append('<ul class="boards">')
        for b in favor.items():
            page.append("<li><a href='/jjboard/%s'>%s</a></li>" % (b[0], b[1]))
        page.append("</ul>")

        print_all(self, [myHeader,"\r\n".join(page), myFooter.replace("<!-->", copyright.replace("<!-->", "<a href='/'>smth</a>"))])


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
            navlink = "<h1 class='nav'><a href='/jj/' class=' btnCenter3 btnCenter' style='{width:66px}'>Home</a><a href='/jjboard/%s/2' class='btnRight0'>2</a></h1>" % board;
        else:
            nextPage = curPage + 1
            lastPage = curPage - 1
            navlink = "<h1 class='nav'><a href='/jjboard/%s/%d' class='btnLeft0'>%d</a><a href='/jj/' class='btnCenter' style='{width:66px}'>Home</a><a href='/jjboard/%s/%d' class='btnRight0'>%d</a></h1>" % (board, lastPage, lastPage, board, nextPage, nextPage);

        self.response.out.write(myHeader)
        self.response.out.write("<h1>%s</h1>" % board2name[board])

        self.response.out.write(navlink)
        self.response.out.write("<ul class='threads'>")
        for p in posts:
            self.response.out.write("<li><a href='/jjsubject/%s/%s'>%s&nbsp;&nbsp;<span class='author'>%s</span></a></li>" % (board, p[1], p[2], p[3]))
        self.response.out.write("</ul>")
        self.response.out.write(navlink)
        self.response.out.write(myFooter)

def _subject(path):
        paras = path.split('/')
        board,id = paras[2],paras[3]
        if (len(paras) == 4):
            pagenum = ""
        else:
            pagenum = "&page=" + paras[4]

        url = 'http://bbs.jjwxc.net/showmsg.php?board=%s&id=%s%s' % (board, id, pagenum)
        result = fetch(url)
        content = toUTF8(result.content)
        if re.search(r"本贴已经被删除", content):
            return page_404.replace("<!-->", r"本贴已经被删除")

        try:
            sub = re.search("主题：(.*?)</td>", content).group(1)
        except AttributeError:
            import traceback
            return page_404.replace("<!-->", "<pre>%s</pre>" % traceback.format_exc())

        boardLink = "<a class='btnCenter' href='/jjboard/%s' style='{width:%dpx}'>%s</a>" % (board, len(board2name[board])*8, board2name[board])
        p_total = re.search("共(\d+)页.*?<b>\[(\\d+)\]</b>", content)
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
            navlink = "<h1 class='nav'><a name='top' href='javascript:history.go(-1)' class='btnLeft0'>&lt;</a>%s</h1>" % boardLink

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
        
        return navlink, navlink, page


class Subject(webapp.RequestHandler):
    def get(self):
        c = _subject(self.request.path)
        if type(c) == str:
            print_all(self, [myHeader, c, nav_common, myFooter])
        else:
            print_all(self, [myHeader, c[0], c[2], c[1], myFooter])
