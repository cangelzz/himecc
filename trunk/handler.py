# -*- coding: utf-8 -*-

from google.appengine.ext import webapp 
from google.appengine.ext.webapp.util import run_wsgi_app
import smth, jj, smart


application = webapp.WSGIApplication([('/',  smth.MainPage),
                                      ('/smth/?',  smth.MainPage),
                                      ('/board/.*', smth.Board),
                                      ('/subject/.*', smth.Subject),
                                      ('/post/.*', smth.Post),
                                      ('/test/.*', smth.Test),
                                      ('/ipad/?', smth.iPad),
                                      ('/ipost/.*', smth.iPost),
                                      ('/iboard/.*', smth.iBoard),
                                      ('/isubject/.*', smth.iSubject),
                                      ('/config/?.*', smth.Config),
                                      ('/smart/?', smart.Smart),
                                      ('/jj/?',  jj.MainPage),
                                      ('/jjboard/?.*', jj.Board),
                                      ('/jjsubject/.*', jj.Subject),
                                      ('/jjcomment/', jj.Comment),
                                      ], debug=True)

def main():
    run_wsgi_app(application)

if (__name__ == '__main__'):
    main()
