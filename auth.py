from base_request_handler import BaseRequestHandler

class Login(BaseRequestHandler):
  def get(self):
  
   useremail = 'not logged in'

   if users.get_current_user() is not None:
   	useremail = users.get_current_user().email()
   
   template_values = {
      'page':'a',
      'recentReactions':'a',
      'useremail':useremail,
      }
   self.generate('login.html',template_values)

class GroupLogin(BaseRequestHandler):
  def get(self):
   template_values = {
      'page':'a',
      'recentReactions':'a',
      }
   self.generate('groupLogin.html',template_values)
  def post(self):
   secretWord = self.request.get('secretWord')
   
   
   """
   if secretWord == 'xxxx':
   		self.response.headers.add_header('Set-Cookie', 'groupLoginCode=%s; expires=Fri, 31-Dec-2020 23:59:59 GMT; path=/' % "xxxx")
   		self.redirect("/index.html")
   		return
   if secretWord == 'xxxx':
   		self.response.headers.add_header('Set-Cookie', 'groupLoginCode=%s; expires=Fri, 31-Dec-2020 23:59:59 GMT; path=/' % "xxxx")
   		self.redirect("/index.html")
   		return
   if secretWord == 'xxxx':
   		self.response.headers.add_header('Set-Cookie', 'groupLoginCode=%s; expires=Fri, 31-Dec-2020 23:59:59 GMT; path=/' % "xxxx")
   		self.redirect("/index.html")
   		return
   if secretWord == 'xxxx':
   		self.response.headers.add_header('Set-Cookie', 'groupLoginCode=%s; expires=Fri, 31-Dec-2020 23:59:59 GMT; path=/' % "xxxx")
   		self.redirect("/index.html")
   		return
   if secretWord == 'xxxx':
   		self.response.headers.add_header('Set-Cookie', 'groupLoginCode=%s; expires=Fri, 31-Dec-2020 23:59:59 GMT; path=/' % "xxxx")
   		self.redirect("/index.html")
   		return
   """
   
   self.redirect("/groupLoginNotOK.html")

