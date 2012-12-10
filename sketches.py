import logging
from admin import UserInfo

from google.appengine.ext import db
from google.appengine.ext.db import Key

from base_request_handler import BaseRequestHandler

ZERO_FILL = '00000000000000000000'
SKETCH_ZEROS = "sketch" + ZERO_FILL

import util


class UploadFullSketchImagePage(BaseRequestHandler):
    def get(self,randomID,perm_stem):

        cpedialog = util.getCPedialog()
        sketch = db.Query(Sketch).filter('randomID =',randomID).get()
        if(sketch is None):
            self.redirect('/index.html')
				

        template_values = {
          'sketch': sketch,
          'headerTitle':"Playground",
          }
        self.generate('uploadFullSketchImagePageTemplate.html',template_values)



class FetchSourceCode(BaseRequestHandler):
    def get(self,randomID):

        cpedialog = util.getCPedialog()
        sketch = db.Query(Sketch).filter('randomID =',randomID).get()
        if(blog is None):
            self.redirect('/index.html')
        template_values = {
          'sketch': sketch,
          }
        self.generate('sourcecode_view.html',template_values)

class showLatestSketches(BaseRequestHandler):

  def get(self):
        next = None
        PAGESIZE = 30

        util.insertUsersideCookies(self)

        user = UserInfo()
        user.whoIs(self)

        if user.email == 'metalmedley1@gmail.com':
        	self.generate('limboPage.html')
        	return;

        bookmark = self.request.get("bookmark")
        if bookmark:
        	bookmark = Key(self.request.get("bookmark"))
        else:
        	bookmark = Key.from_path('GallerySketch',SKETCH_ZEROS)

        logging.info('starting key  ' + str(bookmark))
        logging.info('starting key  name' + bookmark.name())
        q = db.GqlQuery("SELECT * FROM GallerySketch WHERE __key__ >= :1", bookmark)
        sketches = q.fetch(PAGESIZE+1)
        
        if len(sketches) == PAGESIZE + 1:
        	next = str(sketches[-1].key())
        	sketches = sketches[:PAGESIZE]
        	logging.info('next key  ' + next)
        	logging.info('next key name ' + sketches[-1].key().name())

        if next is None:
        	next = ""


        for sketch in sketches:
        	sketch.stringtags = util.shorten(" ".join(sketch.tags),18)
			
        template_values = {
          'sketches':sketches,
          'bookmark':bookmark,
          'next':next,
          'action':"gallery",
          'headerTitle':"Gallery",
          }
        self.generate('galleryTemplate.html',template_values)



class showMySketches(BaseRequestHandler):

  def get(self):
        next = None
        PAGESIZE = 30

        util.insertUsersideCookies(self)

        self.session = True
        user = UserInfo()
        user.whoIs(self)

        bookmark = self.request.get("bookmark")
        if bookmark:
        	bookmark = Key(self.request.get("bookmark"))
        else:
        	if user.user:
        		bookmark = Key.from_path('MySketchesSketch','-%023d' % (int(user.user_id)) + SKETCH_ZEROS)
        	else:
        		bookmark = Key.from_path('MySketchesSketch','-%023d' % (0) + SKETCH_ZEROS)

        if user.user:
        	endKey =  Key.from_path('MySketchesSketch','-%023d' % (int(user.user_id) + 1) + SKETCH_ZEROS)
        else:
        	endKey =  Key.from_path('MySketchesSketch','-%023d' % (1) + SKETCH_ZEROS)
        
        logging.info('starting key  ' + str(bookmark))
        logging.info('starting key  name' + bookmark.name())

        

        q = db.GqlQuery("SELECT * FROM MySketchesSketch WHERE __key__ >= :1 AND __key__ < :2",bookmark,endKey)

        sketches = q.fetch(PAGESIZE+1)
        if len(sketches) == PAGESIZE + 1:
        	next = str(sketches[-1].key())
        	sketches = sketches[:PAGESIZE]
        	logging.info('next key  ' + next)
        	logging.info('next key name ' + sketches[-1].key().name())
        
        if next is None:
        	next = ""

        for sketch in sketches:
        	sketch.stringtags = util.shorten(" ".join(sketch.tags),18)
			
        template_values = {
          'sketches':sketches,
          'bookmark':bookmark,
          'next':next,
          'action':"mySketches",
          'headerTitle':"My sketches",
          }
        self.generate('galleryTemplate.html',template_values)

class showAnonymousSketches(BaseRequestHandler):

  def get(self):
        
        originaluserIDasString = "anonymous"
        # this big blot inserted by Davide Della Casa
        self.session = True
        user = UserInfo()
        user.whoIs(self)

        if not user.is_current_user_admin:
        	self.redirect('/index.html')

        next = None
        PAGESIZE = 30

        util.insertUsersideCookies(self)

        # we get it in the form davidedc-2jaidlbSQRSE and we only want 2jaidlbSQRSE
        userIDasString = "anonymous"
        userIDasString = '%023d' % (0)
        logging.info('searching for anonymous sketches, user id is 23 zeroes')

        self.session = True
        user = UserInfo()
        user.whoIs(self)

		# we'll be using this variable later and it better not be null
        if user.user_id == None:
        	user.user_id = "0";
			
        logging.info('comparing ' + ('%023d' % int(user.user_id)) + " to " + userIDasString)
        logging.info('admin looking at anonymous sketches')
        # note that we can fetch the sketches from the AuthorSketchesSketch table
        # because all anonymous sketches are public.
        bookmark = self.request.get("bookmark")
        if self.request.get("bookmark"):
        	bookmark = Key(self.request.get("bookmark"))
        else:
        	bookmark = Key.from_path('AuthorSketchesSketch',"-"+userIDasString + ZERO_FILL)
        endKey =  Key.from_path('AuthorSketchesSketch','-%023d' % (int(userIDasString) + 1) + ZERO_FILL)
        q = db.GqlQuery("SELECT * FROM AuthorSketchesSketch WHERE __key__ >= :1 AND __key__ < :2",bookmark,endKey)


        logging.info('starting key  ' + str(bookmark))
        logging.info('end key  ' + str(endKey))


        ANONYMOUSSKETCHESFETCHSIZE = 1000
        sketches = q.fetch(ANONYMOUSSKETCHESFETCHSIZE+1)
        logging.info('number of sketches found: ' + str(len(sketches)))
        if len(sketches) == ANONYMOUSSKETCHESFETCHSIZE + 1:
        	next = str(sketches[-1].key())
        	sketches = sketches[:ANONYMOUSSKETCHESFETCHSIZE]
        
        if next is None:
        	next = ""

        for sketch in sketches:
        	sketch.stringtags = util.shorten(" ".join(sketch.tags),18)
			
        template_values = {
          'sketches':sketches,
          'bookmark':bookmark,
          'next':next,
          'action':"sketchesByUploader",
          'userIDasString':originaluserIDasString,
          'headerTitle':"By submitter",
          }
        self.generate('allAnonymousSketchesTemplate.html',template_values)


class showSketchesByUploader(BaseRequestHandler):

  def get(self,originaluserIDasString):
        next = None
        PAGESIZE = 30

        util.insertUsersideCookies(self)

        # we get it in the form davidedc-2jaidlbSQRSE and we only want 2jaidlbSQRSE
        userIDasString = originaluserIDasString.partition('-')[2]
        logging.info('most weird: sometimes this ends with justcorners.js : ' + userIDasString)
        userIDasString = userIDasString.partition('/')[0]
        
        if userIDasString != "anonymous":
        	userIDasString = '%023d' % (util.toBase10(userIDasString,62))
        	logging.info('coverting to 23 digits: ' + userIDasString)
        	logging.info('after cleanup, query starts from ' + "-"+userIDasString + ZERO_FILL)
        	logging.info('query ends at ' + '-%023d' % (int(userIDasString) + 1) + ZERO_FILL)
        else:
        	userIDasString = '%023d' % (0)
        	logging.info('searching for anonymous sketches, user id is 23 zeroes')

        self.session = True
        user = UserInfo()
        user.whoIs(self)

		# we'll be using this variable later and it better not be null
        if user.user_id == None:
        	user.user_id = "0";
			
        logging.info('comparing ' + ('%023d' % int(user.user_id)) + " to " + userIDasString)
        if ('%023d' % int(user.user_id)) != userIDasString:
        	logging.info('user is looking at someone else\'s sketches, showing only public sketches from AuthorSketchesSketch table')
        	bookmark = self.request.get("bookmark")
        	if self.request.get("bookmark"):
        		bookmark = Key(self.request.get("bookmark"))
        	else:
        		bookmark = Key.from_path('AuthorSketchesSketch',"-"+userIDasString + ZERO_FILL)
        	endKey =  Key.from_path('AuthorSketchesSketch','-%023d' % (int(userIDasString) + 1) + ZERO_FILL)
        	q = db.GqlQuery("SELECT * FROM AuthorSketchesSketch WHERE __key__ >= :1 AND __key__ < :2",bookmark,endKey)
        else:
        	logging.info('user is looking at his own sketches, showing private and public sketches from MySketchesSketch table')
        	if self.request.get("bookmark"):
        		bookmark = Key(self.request.get("bookmark"))
        	else:
        		bookmark = Key.from_path('MySketchesSketch','-%023d' % (int(user.user_id)) + SKETCH_ZEROS)
        	endKey =  Key.from_path('MySketchesSketch','-%023d' % (int(user.user_id) + 1) + SKETCH_ZEROS)
        	q = db.GqlQuery("SELECT * FROM MySketchesSketch WHERE __key__ >= :1 AND __key__ < :2",bookmark,endKey)


        logging.info('starting key  ' + str(bookmark))
        logging.info('end key  ' + str(endKey))


        sketches = q.fetch(PAGESIZE+1)
        logging.info('number of sketches found: ' + str(len(sketches)))
        if len(sketches) == PAGESIZE + 1:
        	next = str(sketches[-1].key())
        	sketches = sketches[:PAGESIZE]
        
        if next is None:
        	next = ""

        for sketch in sketches:
        	sketch.stringtags = util.shorten(" ".join(sketch.tags),18)
			
        template_values = {
          'sketches':sketches,
          'bookmark':bookmark,
          'next':next,
          'action':"sketchesByUploader",
          'userIDasString':originaluserIDasString,
          'headerTitle':"By submitter",
          }
        self.generate('galleryTemplate.html',template_values)

