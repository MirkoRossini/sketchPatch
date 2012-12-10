from base_request_handler import BaseRequestHandler
import util
from admin import UserInfo
from model import Sketcher,Weblog,WeblogReactions,Sketch,GallerySketch,MySketchesSketch,\
                  AuthorSketchesSketch,SketchComment,DeletedSketch
from functions import clean_sourcecode, is_suspicious, sourcecode_for_text_area
import logging

class EditBlog(BaseRequestHandler):
    template_path = 'newSketchTemplate.html'

    def get(self,randomID):
    
      util.insertUsersideCookies(self)

      randomID = randomID.replace("/","")
      sketch = Sketch.get_by_randomID(randomID)
      
      # this big blot inserted by Davide Della Casa
      self.session = True
      user = UserInfo()
      user.whoIs(self)

      sketch.sourceCodeForTextArea = sourcecode_for_text_area(sketch.sourceCode)

      if ((sketch.author_user_id == user.user_id) or (user.is_current_user_admin)):
			template_values = {
			'sketch': sketch,
			'published': sketch.published,
			'action': "editBlog",
			'headerTitle':"Edit sketch",
			}
			self.generate(self.template_path,template_values)
      else:
			if self.request.method == 'GET':
				self.redirect("/403.html")
			else:
				self.error(403)   # User didn't meet role.

    def post(self,randomID):

      logging.info('editing the sketch')
      randomID = randomID.replace("/","")
      sketch = Sketch.get_by_randomID(randomID)


      # this big blot inserted by Davide Della Casa
      self.session = True
      user = UserInfo()
      user.whoIs(self)

      if ((sketch.author_user_id == user.user_id) or (user.is_current_user_admin)):
			if(sketch is None):
				self.redirect('/index.html')

			################################################################################
			################################################################################ 
			# and now for some serious tiptapping. On top of the sketch table, there are other
			# tables to change.
			# first, if the published flag changes, then the entries in the gallery and in the by_author
			# table need to either be inserted or be deleted
			# that said, also if the title or the tags change, then you need to modify the entries
			# in all the three tables (unless you just deleted or added them)
			

			AuthorSketchesSketch_add = False
			AuthorSketchesSketch_change = False
			AuthorSketchesSketch_delete = False
			
			GallerySketch_add = False
			GallerySketch_change = False
			GallerySketch_delete = False
			
			if 'published' in self.request.arguments():
				logging.info('editing a sketch and the published field has been sent')
			
			# check if the edited sketch has become suspicious
			sketch_title = self.request.get('title_input')
			sketch_tags_commas = self.request.get('tags')
			suspiciousContent = False
                        if is_suspicious(sketch_title,sketch_tags_commas):
                          suspiciousContent = True
			if util.doesItContainProfanity(sketch_title):
				suspiciousContent = True
				logging.info('this sketch is dirrrrrrrty')

			# Anonymous users can't create unpublished sketches,
			# so we override the flag of the form if the case
			if suspiciousContent == True:
				logging.info('forcing the sketch to unpublishing because it is so dirty')
				shouldItBePublished = False
			elif user.user:
				shouldItBePublished = ('published' in self.request.arguments())
			else:
				shouldItBePublished = True
			

			# first, check if the title or the tags changed
			# if so, then you modify the MySketchesSketch table right away
			# and you mark the AuthorSketchesSketch and the GallerySketch table as
			# *potentially* to be modified ( *potentially* because you might have to just add those
			# entries anew or delete them, depending on whether the published flag has changed)
			if ((sketch.title != sketch_title) or (sketch.tags_commas != self.request.get('tags'))):
				q0 = db.GqlQuery("SELECT * FROM MySketchesSketch WHERE randomID = :1", randomID).fetch(1)
				q0[0].title = sketch_title
				q0[0].tags_commas = self.request.get('tags')
				q0[0].published = (shouldItBePublished)
				q0[0].put()
				#
				AuthorSketchesSketch_change = True
				GallerySketch_change = True

			# now you check how the published flag changes to see if the entries
			# in the other two tables need to be added or deleted
			
			if ((sketch.published == True) and (shouldItBePublished==False)):
				logging.info('unpublishing a sketch')
				AuthorSketchesSketch_delete = True
				GallerySketch_delete = True

			if ((sketch.published == False) and (shouldItBePublished==True)):
				logging.info('making a sketch public')
				AuthorSketchesSketch_add = True
				GallerySketch_add = True
				
			# if you have to add, add, and set the "change" flag to false so that
			# you don't blindly change this record soon after you've added it
			if AuthorSketchesSketch_add	:
				authorSketchesSketch = AuthorSketchesSketch(key_name = '-%023d' % int(user.user_id) + sketch.key().name())
				authorSketchesSketch.title = self.request.get('title_input')
				authorSketchesSketch.published = shouldItBePublished
				authorSketchesSketch.randomID = sketch.randomID
				authorSketchesSketch.tags_commas = self.request.get('tags')
				authorSketchesSketch.put()
				AuthorSketchesSketch_change = False

			if GallerySketch_add	:
				gallerySketch = GallerySketch(key_name = sketch.key().name())
				if user.user:
					gallerySketch.author_nickname = user.nickname
				else:
					gallerySketch.author_nickname = "anonymous"
				gallerySketch.title = self.request.get('title_input')
				gallerySketch.published = shouldItBePublished
				gallerySketch.randomID = sketch.randomID
				gallerySketch.tags_commas = self.request.get('tags')
				gallerySketch.put()
				GallerySketch_change = False

			# if you have to delete, delete, and set the "change" flag to false so that
			# you don't blindly change those entries soon after you've added
			if AuthorSketchesSketch_delete	:
				q1 = db.GqlQuery("SELECT * FROM AuthorSketchesSketch WHERE randomID = :1", randomID).fetch(1)
				q1[0].delete()
				AuthorSketchesSketch_change = False

			if GallerySketch_delete	:
				q2 = GallerySketch.get_by_key_name(sketch.key().name())
				q2.delete()
				GallerySketch_change = False

			
			
			# any change to the AuthorSketches or GallerySketch tables only happens if the sketch is public,
			# cause otherwise those two sketch records aren't just going to be there in the first place!
			if (sketch.published) :
				# ok now check the "change" flags. If they are still on, it means that the title or
				# tag have changed, and the published flag hasn't changed (so it's not like you just
				# added or deleted the records), so you have to effectively
				# go and fish the records out of the database and change them
				if AuthorSketchesSketch_change	:
					# need to fetch the other tables (gallery, my page and by author) and change them
					q3 = db.GqlQuery("SELECT * FROM AuthorSketchesSketch WHERE randomID = :1", randomID).fetch(1)
					q3[0].title = self.request.get('title_input')
					q3[0].tags_commas = self.request.get('tags')
					q3[0].put()
				if GallerySketch_change	:
					q4 = GallerySketch.get_by_key_name(sketch.key().name())
					q4.title = self.request.get('title_input')				
					q4.tags_commas = self.request.get('tags')				
					q4.put()

				
			################################################################################
			################################################################################
			
			sketch.set_title(self.request.get('title_input'))
			sketch.description = util.Sanitize(self.request.get('text_input'))
			sketch.published = (shouldItBePublished)

			sketch.sourceCode = self.request.get('text_input2').rstrip().lstrip()
			sketch.sourceCode = sketch.sourceCode.replace('&','&amp;')
			sketch.sourceCode = sketch.sourceCode.replace('<','&lt;')
			sketch.sourceCode = sketch.sourceCode.replace(' ','&nbsp;')
			sketch.sourceCode = sketch.sourceCode.replace('\r\n','<br>')
			sketch.sourceCode = sketch.sourceCode.replace('\n','<br>')
			sketch.sourceCode = sketch.sourceCode.replace('\r','<br>')
			sketch.sourceCode = sketch.sourceCode.replace('\t','&nbsp;&nbsp;&nbsp;&nbsp;')
			sketch.sourceCode = sketch.sourceCode.replace('"','&quot;')
			sketch.sourceCode = sketch.sourceCode.replace("'", '&#39;')
			
			sketch.tags_commas = self.request.get('tags')
			
			sketch.update()
			
			
			
			
			## now, finally, this uploads the thumbnail
			thumbnailData = self.request.get('thumbnailData')
			#logging.info('thumbnail data: ' + thumbnailData)
			if thumbnailData != "":
				logging.info('thumbnail data not empty - adding/overwriting thumbnail')
				thumbnailUploaderObject = thumbnailUploaderClass()
				thumbnailUploaderObject.doTheUpload(sketch.randomID,thumbnailData)
			else:
				logging.info('no thumbnail data')


			# note that we don't tell anonymous users what happened - this is to make
			# bots' life a tiny little bit more complicated
			if user.user and suspiciousContent and ('published' in self.request.arguments()):
				self.redirect("/sketchNotMadePublicNotice.html?sketchID="+sketch.randomID)
			else:
				self.redirect(sketch.full_permalink())

      else:
			if self.request.method == 'GET':
				self.redirect("/403.html")
			else:
				self.error(403)   # User didn't meet role.

