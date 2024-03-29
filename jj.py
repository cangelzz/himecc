﻿# emacs-mode: -*- python-*-
# -*- coding: utf-8 -*-

from google.appengine.ext import webapp
from google.appengine.api.urlfetch import DownloadError
from util import fetch, print_all
from common import tracking, page_404, copyright, commonHeader, myFooter
from define import jj_boards, _jjid
import re 
import logging
import traceback

favor = {"20": "战色逆乐园", "3": "耽美闲情"}
board2name = {"20": "战色逆乐园", "3": "耽美闲情"}

myHeader = commonHeader + "</head><body>"

nav_common = "<h1 class='nav'><a href='javascript:history.go(-1)' class='btnLeft0'>&lt;</a><a class='btnCenter0 btnCenter2' href='/jj/' style='{width:66px}'>Home</a></h1>"

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
#        for b in favor.items():
#            page.append("<li><a href='/jjboard/%s'>%s</a></li>" % (b[0], b[1]))
        for l1 in jj_boards:
            page.append("<li class='group'>%s</li>" % l1[0])
            for l2 in l1[1:]:
                page.append("<li><a href='/jjboard/%s'>%s</a></li>" % l2)
        page.append("</ul>")

        print_all(self, [myHeader,"\r\n".join(page), myFooter.replace("<!-->", copyright.replace("<!-->", "<a href='/'>smth</a>"))])

def _board(path):
        paras = path.split('/')
        try:
            board = paras[2]
            if (len(paras) == 3):
                isLast = True
                pagetogo = ""
            else:
                isLast = False
                pagetogo = "&page=" + paras[3]
        except IndexError:
            return page_404.replace("<!-->", r"路径参数错误；<span style='color:red'>%s</span>" % path)

        url = "http://bbs.jjwxc.net/board.php?board=" + board + "&page=" + pagetogo
        try:
            result = fetch(url)
        except DownloadError:
            return page_404.replace("<!-->", r"下载错误,请重试")
        content = toUTF8(result.content)
        p =re.compile("href=\"(show.*?)id=(\\d+).*?\".*?>(.*?)&nbsp.*?<td>&nbsp;(.*?)</td>", re.MULTILINE|re.DOTALL)
        posts = re.findall(p, content)
        pages = re.search("<font color=.#FF0000.>(\\d+)</font>.*?<font color=.#FF0000.>(\\d+)</font>", content)
        try:
            totalPage = int(pages.group(1))
            curPage = int(pages.group(2))
        except AttributeError:
            return page_404.replace("<!-->", r"非正常错误；<pre>%s\r\n%s</pre>" % (traceback.format_exc(), content))

        if curPage == 1:
            navlink = "<h1 class='nav'><a class='btnLeft0' href='javascript:history.go(-1)'>&lt;</a><a href='/jj/' class='btnCenter0' style='{width:66px}'>Home</a><a href='/jjboard/%s/2' class='btnRight0'>2</a></h1>" % board;
        else:
            nextPage = curPage + 1
            lastPage = curPage - 1
            navlink = "<h1 class='nav'><a href='/jjboard/%s/%d' class='btnLeft0'>%d</a><a href='/jj/' class='btnCenter0' style='{width:66px}'>Home</a><a href='/jjboard/%s/%d' class='btnRight0'>%d</a></h1>" % (board, lastPage, lastPage, board, nextPage, nextPage);

        boardname = re.search("<title>(.*?)bbs.jjwxc.net</title>", content).group(1)
        navlink_top = "<h1>%s</h1>" % boardname + navlink
        page = ["<ul class='threads'>"]
        for p in posts:
            page.append("<li><a href='/jjsubject/%s/%s'>%s&nbsp;&nbsp;<span class='author'>%s</span></a></li>" % (board, p[1], p[2], p[3]))
        page.append("</ul>")

        return navlink_top, navlink, "\r\n".join(page)

class Board(webapp.RequestHandler):
    def get(self):
        c = _board(self.request.path)
        if type(c) == str:
            print_all(self, [myHeader, c, nav_common, myFooter])
        else:
            print_all(self, [myHeader, c[0], c[2], c[1], myFooter])

def _subject(path):
        paras = path.split('/')
        try:
            board,id = paras[2],paras[3]
            if (len(paras) == 4):
                pagenum = ""
            else:
                pagenum = "&page=" + paras[4]
        except IndexError:
            return page_404.replace("<!-->", r"路径参数错误；<span style='color:red'>%s</span>" % path)

        url = 'http://bbs.jjwxc.net/showmsg.php?board=%s&id=%s%s' % (board, id, pagenum)
        try: 
            result = fetch(url)
        except DownloadError:
            return page_404.replace("<!-->", "<pre>%s</pre>" % traceback.format_exc())

        content = toUTF8(result.content)
        if re.search(r"本贴已经被删除", content):
            return page_404.replace("<!-->", r"本贴已经被删除")

        try:
            subj = re.search("主题：(.*?)</td>", content).group(1)
        except AttributeError:
            return page_404.replace("<!-->", "<pre>%s</pre>" % traceback.format_exc())

        header = "<h1>" + subj + "</h1>"
        
        #boardname = re.search('<td>(.*?)<hr align=.center. width=.760.', content).group(1) seems the boardname is generated by javascript, not on th epage
        boardname = _jjid(board)

        boardLink = "<a class='btnCenter0 left18' href='/jjboard/%s' style='{width:%dpx}'>%s</a>" % (board, len(boardname)*8, boardname)

        p_total = re.search("共(\d+)页.*?<b>\[(\\d+)\]</b>", content)
        if p_total:
            totalPage = int(p_total.group(1))
            curPage = int(p_total.group(2))
            if curPage == 1:
                nextpage = "/jjsubject/" + board + "/" + id + "/" + "1"
                navlink = "<h1 class='nav'><a class='btnLeft0' href='javascript:history.go(-1)'>&lt;</a>%s<a href='%s' class='btnRight0'>2</a></h1>" % (boardLink, nextpage)

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
        
        msgform = """<form action="/jjcomment/" method="post"><ul>
<li><input type="text" name="nick" /></li>
<li><textarea name="msg"></textarea></li>
<li><input type="submit" value="Post" /><input type="hidden" name="board" value="%s" />
<input type="hidden" name="id" value="%s" /></li>
</ul></form>""" % (board, id)


        return header+navlink, navlink, page

class Comment(webapp.RequestHandler):
    def post(self):
        board = self.request.get("board")
        id = self.request.get("id")
        msg = self.request.get("msg")
        nick = self.request.get("nick")

        form_fields = { "username": nick,
                        "body": msg,
                        "pic": "0"
                        }
        import urllib
        from google.appengine.api import urlfetch
        
        url = "http://bbs.jjwxc.net/reply.php?board=%s&id=%s" % (board, id)
        payload = urllib.urlencode(form_fields)

        result = fetch(url, method=urlfecth.POST, payload=payload)
        self.redirect("/jjsubject/%s/%s" % (board, id))

#        print_all(self, [myHeader, board, id, msg, nick, myFooter])

class Subject(webapp.RequestHandler):
    def get(self):
        c = _subject(self.request.path)
        if type(c) == str:
            print_all(self, [myHeader, c, nav_common, myFooter])
        else:
            print_all(self, [myHeader, c[0], c[2], c[1], myFooter])
