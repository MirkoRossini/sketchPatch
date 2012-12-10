# !/usr/bin/env python
#
# Copyright 2008 CPedia.com, sketchPatch.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

__author__ = 'Ping Chen, Davide Della Casa'

import cgi
import wsgiref.handlers
import os
import re
import datetime
import calendar
import logging
import string
import urllib
import util
import pagecount
import Cookie

from xml.etree import ElementTree

from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.api import memcache
from google.appengine.ext import search
from google.appengine.api import images

from model import Sketcher,Weblog,WeblogReactions,Sketch,GallerySketch,MySketchesSketch,\
                  AuthorSketchesSketch,SketchComment,DeletedSketch
import authorized
import view
from admin import UserInfo

#After refactoring
from functions import clean_sourcecode, is_suspicious, sourcecode_for_text_area
from base_request_handler import BaseRequestHandler
from auth import Login,GroupLogin
from add_blog import AddBlog
from edit_blog import EditBlog
from thumbnailUpload import thumbnailUploaderClass
from profile import showProfile, showProfileEdit, avatarImage
from blog_reactions import AddBlogReaction, DeleteBlogReaction
from articles import ArticleHandler, ArticleHandlerEmbed
from sketches import UploadFullSketchImagePage, FetchSourceCode, showLatestSketches, showMySketches,\
                     showAnonymousSketches, showSketchesByUploader

# session library for when we override the true user identity, we store
# the fake one in session
from appengine_utilities.sessions import Session
from google.appengine.ext.db import Key





class NotFoundHandler(webapp.RequestHandler):
    def get(self):
        self.error(404)
        view.ViewPage(cache_time=36000).render(self)

class UnauthorizedHandler(webapp.RequestHandler):
    def get(self):
        self.error(403)
        view.ViewPage(cache_time=36000).render(self)








class CopyBlog(BaseRequestHandler):
#    @authorized.role("admin")
    def get(self,randomID):

      util.insertUsersideCookies(self)

      randomID = randomID.replace("/","")
      sketch = Sketch.get_by_randomID(randomID)
      
      # this big blot inserted by Davide Della Casa
      self.session = True
      user = UserInfo()
      user.whoIs(self)

      sketch.sourceCodeForTextArea = sourcecode_for_text_area(sketch.sourceCode)
      sketch.blogdate = "";
      sketch.entrytype="";
      sketch.status="published";

      sketch.author_email = user.email
      sketch.author_user_id = user.user_id
      if user.user:
      	sketch.author_nickname = user.nickname
      else:
      	sketch.author_nickname = "anonymous"

      
      # this big blot inserted by Davide Della Casa
      template_values = {
      	'sketch': sketch,
      	'action': "copyBlog",
      	'published': sketch.published,
      	'headerTitle':"Copy sketch",

      }
      self.generate('newSketchTemplate.html',template_values)



class DeleteBlog(BaseRequestHandler):
  def get(self,randomID):

      randomID = randomID.replace("/","")
      sketch = Sketch.get_by_randomID(randomID)
      if sketch is None: self.redirect("/403.html")
      
      # this big blot inserted by Davide Della Casa
      self.session = True
      user = UserInfo()
      user.whoIs(self)

      if ((sketch.author_user_id == user.user_id) or (user.is_current_user_admin)):

           q0 = db.GqlQuery("SELECT * FROM MySketchesSketch WHERE randomID = :1", randomID).fetch(1)
           q1 = db.GqlQuery("SELECT * FROM AuthorSketchesSketch WHERE randomID = :1", randomID).fetch(1)
           logging.info('key stuff: '+ str(sketch.key()))
           logging.info('key stuff: '+ sketch.key().name())
           q2 = GallerySketch.get_by_key_name(sketch.key().name())

           DeletedSketch(key_name = 'sketchRandomID'+randomID).put()
           if(q0) : q0[0].delete()
           if(q1) : q1[0].delete()
           if(q2) : q2.delete()
           if(sketch): sketch.delete()           		
           # deletion of comments is missing

           self.redirect('/mySketches')
      else:
			if self.request.method == 'GET':
				self.redirect("/403.html")
			else:
				self.error(403)   # User didn't meet role.



class showFrontPage(BaseRequestHandler):

  def get(self):

        util.insertUsersideCookies(self)
        
        user = UserInfo()
        user.whoIs(self)

        if user.email == 'metalmedley1@gmail.com':
        	self.generate('limboPage.html')
        	return;
        
        q = db.GqlQuery("SELECT * FROM GallerySketch")
        sketches = q.fetch(28)

        counter = 28
        for sketch in sketches:
        	sketch.stringtags = util.shorten(" ".join(sketch.tags),18)
        	sketch.counter = counter
        	counter = counter + 1
			
        template_values = {
          'sketches':sketches,
          }
        self.generate('frontPageTemplate.html',template_values)


