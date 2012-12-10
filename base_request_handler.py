from google.appengine.ext import webapp
from admin import UserInfo
import view
import os

class BaseRequestHandler(webapp.RequestHandler):
  """Supplies a common template generation function.

  When you call generate(), we augment the template variables supplied with
  the current user in the 'user' variable and the current webapp request
  in the 'request' variable.
  """
  def generate(self, template_name, template_values={}):

    self.session = True
    user = UserInfo()
    user.whoIs(self)    
    if user.user:
    	values = {
    	  'usernickname': user.nickname,
    	  'useremail': user.email,
    	  'usersiscurrentuseradmin' : user.is_current_user_admin,
    	  'userid': user.user_id,
    	}
    else:
    	values = {
    	  'usernickname': "anonymous",
    	  'useremail': None,
    	  'usersiscurrentuseradmin' : False,
    	  'userid': "anonymous",
    	}

    
    values.update(template_values)
    directory = os.path.dirname(__file__)
    view.ViewPage(cache_time=0).render(self, template_name,values)

