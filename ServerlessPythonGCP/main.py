import webapp2
import urllib

class ListAuthors(webapp2.RequestHandler):
  def get(self):
    self.response.headers["Content-Type"] = "text/plain"
    self.response.write("List authors...")

class ListEbooksByAuthor(webapp2.RequestHandler):
  def get(self, author):
    self.response.headers["Content-Type"] = "text/plain"
    self.response.write('Show ebooks by "%s"...' % (urllib.unquote_plus(author)))

app = webapp2.WSGIApplication([
  ("/", ListAuthors),
  ("/(.*)", ListEbooksByAuthor),
], debug=True)
