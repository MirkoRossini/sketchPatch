import logging
import Cookie
from google.appengine.ext import db
import pagecount
from base_request_handler import BaseRequestHandler
import util
from model import Sketch


class BaseArticleHandler(BaseRequestHandler):
    def get(self,randomID,perm_stem):

        cpedialog = util.getCPedialog()
        sketch = db.Query(Sketch).filter('randomID =',randomID).get()
        if(sketch is None):
            self.redirect('/index.html')
				
        # if the page is viewed for the first time, we don't find the cookie
        # so we add the cookie and we increment the pageviews.
        # otherwise if we find the cookie then it means that the page has been viewed already
        # so we just read the counter without incrementing
        c = Cookie.SimpleCookie(self.request.headers.get('Cookie'))
        if "viewed" not in c.keys():
          # set the "viewed" cookie here so that we don't increment the counter at the next visit
          self.response.headers.add_header('Set-Cookie', 'viewed=%s; expires=Fri, 31-Dec-2020 23:59:59 GMT' % "yes")
          numberOfViews = pagecount.IncrPageCount(randomID, 1)
          if sketch is not None and sketch.author_string_user_id != 'anonymous':
            authorViews = pagecount.IncrPageCount(sketch.author_string_user_id, 1)
        else:
          numberOfViews = pagecount.GetPageCount(randomID)


        # in case the user log-ins from a sketch view page, then when he lands on the same
        # page after the login page, we need to write all the cookies on the client side
        # so this is what we are doing here.
        util.insertUsersideCookies(self)

        template_values = {
          'sketch': sketch,
          'headerTitle':"Playground",
          'numberOfViews':numberOfViews,
          #'blog': blog,
          #'reactions': reactions,
          }
        self.generate(self.template,template_values)
                
class ArticleHandler(BaseArticleHandler):
  template = 'viewSketchTemplate.html'

class ArticleHandlerEmbed(BaseRequestHandler):
  template = 'embedSketchTemplate.html'

"""
    def get(self,randomID,perm_stem):

        # NOTE: this piece of code is out of date. You should refresh it using the
        # latest code of the ArticleHandler class. The only thing that you
        # should re-use is the template of the embed view sketch
        
        cpedialog = util.getCPedialog()
        sketch = db.Query(Sketch).filter('randomID =',randomID).get()
        if(sketch is None):
            self.redirect('/index.html')
				
        # if the page is viewed for the first time, we don't find the cookie
        # so we add the cookie and we increment the pageviews.
        # otherwise if we find the cookie then it means that the page has been viewed already
        # so we just read the counter without incrementing
        c = Cookie.SimpleCookie(self.request.headers.get('Cookie'))
        if "viewed" not in c.keys():
          c["viewed"] = ""
          self.response.headers['Set-cookie'] = str(c)				
          numberOfViews = pagecount.IncrPageCount(randomID, 1)
          if sketch.author_string_user_id != 'anonymous':
            authorViews = pagecount.IncrPageCount(sketch.author_string_user_id, 1)
        else:
          numberOfViews = pagecount.GetPageCount(randomID)

        util.insertUsersideCookies(self)


        forcedNumberOfViewsCounter = self.request.get("forcedNumberOfViewsCounter3141592")
        if forcedNumberOfViewsCounter != '':
        	pagecount.IncrPageCount(randomID, int(forcedNumberOfViewsCounter) - pagecount.GetPageCount(randomID))



        template_values = {
          'sketch': sketch,
          'headerTitle':"Playground",
          'numberOfViews':numberOfViews,
          }
        self.generate(,template_values)

"""
