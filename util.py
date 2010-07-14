# -*- coding: utf-8 -*-

from google.appengine.api import urlfetch


def fetch(url, payload=None, method=urlfetch.GET, headers={}, allow_truncated=False, follow_redirects=True, deadline=10):
    return urlfetch.fetch(url, payload=payload, method=method, headers=headers, allow_truncated=True, follow_redirects=follow_redirects, deadline=deadline)

def convertFromGB2312ToUTF8(onestr):
    newstr = onestr
    try:
        newstr = unicode(newstr, 'cp936', 'ignore')
    except:
        pass
    return newstr.encode('utf-8', 'ignore')

def print_all(handler, li):
    for line in li:
        handler.response.out.write(line)

