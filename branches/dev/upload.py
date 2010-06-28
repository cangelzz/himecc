from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
import cgi

class Task(db.Model):
    id = db.StringProperty()
    filename = db.StringProperty()
    data = db.BlobProperty()

class MainPage(webapp.RequestHandler):
    def get(self):
        self.response.out.write("""
<html>
<body>
<form enctype="multipart/form-data" action="/add" method="post">
<input type="text" value="" name="id">
<input type="text" value="" name="filename">
<input type="file" name="torrent">
<input type="submit" value="Add">
</form>""")

        q = db.Query(Task)
        self.response.out.write("<table border='1'>")
        for t in q.fetch(limit=100):
            self.response.out.write("<tr><td>" + t.id + "</td><td><a href='/down?id=%s'>" % t.id + t.filename + "</a></td></tr>")

        self.response.out.write("</table>")

        self.response.out.write("""
</body>
</html>""")

class AddTask(webapp.RequestHandler):
    def post(self):
        t = Task()
        t.id = self.request.get('id')
        t.filename = self.request.get('filename')
        f = self.request.get("torrent")
        t.data = db.Blob(f)
        t.put()
        self.redirect('/upload')

class DownloadFile(webapp.RequestHandler):
    def get(self):
        id = self.request.get('id')
        query = db.Query(Task)
        query.filter('id =', id)
        file = query.fetch(limit=1)
#        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write(file[0].data)

class ListTask(webapp.RequestHandler):
    def get(self):
        q = db.Query(Task)
        for t in q.fetch(limit=100):
            self.response.out.write("*" + t.id + "|" + t.filename + "\n")

application = webapp.WSGIApplication([('/upload', MainPage), 
    ('/add', AddTask),
    ('/down', DownloadFile),
    ('/list', ListTask)
    ], debug=True)

if __name__ == "__main__":
    run_wsgi_app(application)
