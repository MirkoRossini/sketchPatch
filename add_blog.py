from base_request_handler import BaseRequestHandler
import util
from admin import UserInfo
from model import Sketcher,Weblog,WeblogReactions,Sketch,GallerySketch,MySketchesSketch,\
                  AuthorSketchesSketch,SketchComment,DeletedSketch
from functions import clean_sourcecode, is_suspicious, sourcecode_for_text_area
import logging


class AddBlog(BaseRequestHandler):
#  @authorized.role("admin")
  template_path = 'newSketchTemplate.html'
                
  def get(self):
      
      util.insertUsersideCookies(self)

      template_values = {
      	'action': "addBlog",
      	'isNew': True, # DDC
      	'published': True, # DDC
      	'headerTitle':"Add a sketch",
      }
      #self.generate('blog_add.html',template_values)
      self.generate(self.template_path,template_values)

#  @authorized.role("admin")
  def post(self):

			self.session = True
			user = UserInfo()
			user.whoIs(self)

			if 'published' in self.request.arguments():
				logging.info('adding a sketch and the published field has been sent')

			preview = self.request.get('preview')
			submitted = self.request.get('submitted')
			published = ('published' in self.request.arguments())
			
			theKey = Sketch.generateKey()
			sketch = Sketch(key_name = theKey)
			sketch.sourceCode = self.request.get('text_input2').rstrip().lstrip()
			sketch.description = util.Sanitize(self.request.get('text_input'))
			
			# minimal protection against spammers, redirect to root if the program contains too many urls
			#logging.info('occurrences of http ' + str(sketch.sourceCode.count("http")))
			sketch_sourceCode_count_http = sketch.sourceCode.count("http://")
			sketch_sourceCode_count_url_http = sketch.sourceCode.count("[url=http://")
			sketch_description_count_http = sketch.description.count("http://")

			if sketch_sourceCode_count_http > 10:
				self.redirect("/")
				return
			if sketch_sourceCode_count_url_http > 0:
				self.redirect("/")
				return
			if sketch_description_count_http > 7:
				self.redirect("/")
				return
			if sketch_description_count_http + sketch_sourceCode_count_http > 12:
				self.redirect("/")
				return

			sketch_title = self.request.get('title_input')

			# now let's check in some other ways if the content is suspicious
			suspiciousContent = False
			sketch_title = self.request.get('title_input')
			sketch_tags_commas = self.request.get('tags')
			suspiciousContent = False
                        if is_suspicious(sketch_title,sketch_tags_commas):
                          suspiciousContent = True

			if any(util.doesItContainProfanity(text)\
                                for text in(sketch_title,
                                            sketch.sourceCode,
                                            sketch.description)
                               ):
				suspiciousContent = True
			
			gallerySketch = GallerySketch(key_name = theKey) # the gallery must be ordered by time, most recent first
			if user.user:
				#authorSketchesSketch = AuthorSketchesSketch(key_name = "-"+util.convDecToBase(string._long(user.user_id),62) + theKey)
				#mySketchesSketch = MySketchesSketch(key_name = "-"+util.convDecToBase(string._long(user.user_id),62) + theKey)
				user_id_in_fixed_digits = '-%023d' % (int(user.user_id))
				authorSketchesSketch = AuthorSketchesSketch(key_name = user_id_in_fixed_digits + theKey)
				mySketchesSketch = MySketchesSketch(key_name = user_id_in_fixed_digits + theKey)
				authorSketchesSketch.user_id_string = util.convDecToBase(string._long(user.user_id),62)
				mySketchesSketch.user_id_string = util.convDecToBase(string._long(user.user_id),62)
			else:
				authorSketchesSketch = AuthorSketchesSketch(key_name = '-%023d' % (0) + theKey)
				mySketchesSketch = MySketchesSketch(key_name = '-%023d' % (0) + theKey)
				authorSketchesSketch.user_id_string = "anonymous"
				mySketchesSketch.user_id_string = "anonymous"

			# propagate the "suspicious" flag in all the records that we are adding
			sketch.suspiciousContent = suspiciousContent
			gallerySketch.suspiciousContent = suspiciousContent
			authorSketchesSketch.suspiciousContent = suspiciousContent
			mySketchesSketch.suspiciousContent = suspiciousContent
			

			sketch.set_title(sketch_title)
			gallerySketch.title = sketch.title
			authorSketchesSketch.title = sketch.title
			mySketchesSketch.title = sketch.title
			
			if suspiciousContent == True:
				sketch.published = False
				authorSketchesSketch.published = False
				mySketchesSketch.published = False
			elif user.user:
				sketch.published = published
				authorSketchesSketch.published = published
				mySketchesSketch.published = published
			else:
				sketch.published = True
				authorSketchesSketch.published = True
				mySketchesSketch.published = True
			sketch.sourceCode = clean_sourcecode(sketch.sourceCode)
				
			#sketch.author_user = user.user
			sketch.author_email = user.email
			sketch.author_user_id = user.user_id
			if user.user:
				sketch.author_string_user_id = util.convDecToBase(string._long(user.user_id),62)
				sketch.author_nickname = user.nickname
			else:
				sketch.author_string_user_id = "anonymous"
				sketch.author_nickname = "anonymous"



			if user.user:
				gallerySketch.author_nickname = user.nickname
			else:
				gallerySketch.author_nickname = "anonymous"
			
			sketch.tags_commas = self.request.get('tags')
			gallerySketch.tags_commas = self.request.get('tags')
			authorSketchesSketch.tags_commas = self.request.get('tags')
			mySketchesSketch.tags_commas = self.request.get('tags')


			template_values = {
			  'sketch': sketch,
			  'published': sketch.published,
			  'preview': preview,
			  'submitted': submitted,
			  'action': "addBlog",
			  'tags': self.request.get('tags'),
			  }

			sketch.set_randomID()

			sketch.parentSketchRandomID = self.request.get('parentSketchRandomID')
			
			if sketch.parentSketchRandomID is None:
				sketch.parentSketchRandomID = ''
				
			if sketch.parentSketchRandomID == '':
				sketch.oldestParentSketchRandomID = sketch.randomID;
			else:
				sketch.oldestParentSketchRandomID = self.request.get('oldestParentSketchRandomID')			
			sketch.set_parents(self.request.get('parent_idList'),self.request.get('parent_nicknamesList'))


			gallerySketch.randomID = sketch.randomID
			authorSketchesSketch.randomID = sketch.randomID
			mySketchesSketch.randomID = sketch.randomID

			sketch.save()
			
			# if this is an anonymous user adding a sketch, we have forced this flag to True
			if sketch.published:
				authorSketchesSketch.save()
				gallerySketch.save()

			mySketchesSketch.save()
			
			
			
			## now, finally, this uploads the thumbnail
			thumbnailData = self.request.get('thumbnailData')
			#logging.info('add blog, thumbnail data: ' + thumbnailData)
			if thumbnailData != "":
				logging.info('add blog, thumbnail data not empty - adding/overwriting thumbnail')
				thumbnailUploaderObject = thumbnailUploaderClass()
				thumbnailUploaderObject.doTheUpload(sketch.randomID,thumbnailData)
			else:
				logging.info('add blog, no thumbnail data')



			if user.user and suspiciousContent and ('published' in self.request.arguments()):
				self.redirect("/sketchNotMadePublicNotice.html?sketchID="+sketch.randomID)
			else:
				self.redirect(sketch.full_permalink())

