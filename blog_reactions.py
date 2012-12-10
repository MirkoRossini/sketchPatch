
import logging
import authorized
from base_request_handler import BaseRequestHandler

class AddBlogReaction(BaseRequestHandler):
  def post(self,randomID):

    self.session = True
    user = UserInfo()
    user.whoIs(self)


    # this key is actually of fixed length
    theKey = "-" + randomID + Sketch.generateKey()
    sketchComment = SketchComment(key_name = theKey)
    sketchComment.randomID = randomID
    sketchComment.body = self.request.get('text_input')

    #sketchComment.author_user = user.user
    sketchComment.author_email = user.email
    sketchComment.author_user_id = user.user_id
    sketchComment.author_string_user_id = util.convDecToBase(string._long(user.user_id),62)
    sketchComment.author_nickname = user.nickname

    # This is necessary cause we need to store in the comment who is the author of the sketch
    # cause we'll have the client browser to independently check whether to allow the author of the sketch to delete any of the comments
    # we could do this check on the server side without storing the sketch author in the comment    
    # BUT we can't do the check on the client side without passing a parameter accross three pages...    
    sketch = Sketch.get_by_randomID(randomID)
    if sketch is None: self.redirect("/403.html")
    sketchComment.sketch_author_user_id = sketch.author_user_id
        
    sketchComment.save()
    self.redirect('/view/'+randomID+"/")



class DeleteBlogReaction(BaseRequestHandler):
  @authorized.role("user")
  def get(self,commentId):

		  logging.info('got in')

		  util.insertUsersideCookies(self)

		  self.session = True
		  user = UserInfo()
		  user.whoIs(self)

		  # anonymous users can't delete comments or sketches
		  if not user.user:
		  	self.redirect("/403.html")
		  	return

		  # does the comment exist?
		  q = SketchComment.get_by_key_name(commentId)
		  if not q:
		  	logging.info('no such comment')
		  	self.redirect("/403.html?no such comment")
		  	return

		  # is the user a) an admin b) the owner of the sketch c) the owner of the comment?
		  if ((user.user_id == q.author_user_id) or (user.is_current_user_admin) or (user.user_id == q.sketch_author_user_id)):
		  	logging.info('ok, deleting now')
		  	q.delete()
		  else:
		  	logging.info('wrong permissions')
		  	self.redirect("/403.html?you cant do that")
		  	return

		  logging.info('redirecting to: ' + self.request.get("backTo"))
		  self.redirect(self.request.get("backTo"))
		  return


