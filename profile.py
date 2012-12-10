from base_request_handler import BaseRequestHandler
import logging

class showProfile(BaseRequestHandler):

  def get(self, id):
        next = None
        PAGESIZE = 3

        logging.info("profile handler - being called by"  + self.request.path)

        util.insertUsersideCookies(self)

        self.session = True
        user = UserInfo()
        user.whoIs(self)
        

        if id==None: id=""
        logging.info("id from URL: " + id)
        userIDasString = id.partition('-')[2]
        logging.info('most weird: sometimes this ends with justcorners.js : ' + userIDasString)
        userIDasString = userIDasString.partition('/')[0]
        logging.info("userIDasString: >" + userIDasString +"<")

		# this test below checks if an anonymous user is going to http://www.sketchpatch.net/profile/
		# cause (s)he shouldn't. (s)He just shouldn't see the link. (s)He should be redirected to the login
		# page really, but we are lazy here.
        if userIDasString == "" and (not user.user):
          logging.info("user is not logged in and trying to access his own profile, kicking him/her out")
          self.redirect("/")
          return

		# this happens when a user is logged in and goes to http://www.sketchpatch.net/profile/
		# we fill in the missing information that identifies the user. In order to make
		# the flow of things more uniform
        if userIDasString == "" and user.user:
        	userIDasString = util.convDecToBase(string._long(user.user_id),62)
        
        logging.info('looking for profile with userID = ' + userIDasString)
        query = db.GqlQuery("SELECT * FROM Sketcher WHERE userID = :1", userIDasString)
        sketcher = query.get();
        
		# we'll be using this variable later and it better not be null
        if user.user_id == None:
        	user.user_id = "0";
        
        # if no profile has been found, then there are two cases:
        # 1) anyone for any reason is going to the profile page specifying a userID that
        #    doesn't exist
        # 2) the owner of the profile is going to his own profile page and there is no profile
        #    record yet.
        # We are going to check which case we are in and if we are in case 2) then we create
        # a record for the user. In case he sends his profile URL to his mates, they should
        # see the newly created record there even if he didn't edit his profile.
        # Basically the idea is to create his profile record at the earliest convenience
        
        if sketcher == None:
        	logging.info('comparing ' + util.convDecToBase(string._long(user.user_id),62) + " to " + userIDasString)
        	if util.convDecToBase(string._long(user.user_id),62) != userIDasString:
        		logging.info("no sketcher found - returning an empty record")
        		sketcher = Sketcher()
        		# we are not creating a record here, we can populate this data
        		# with funny data :-)
        		sketcher.name = "No profile for this user yet :-("
        		sketcher.profileText = "nothing"
        		sketcher.url1 = "nada"
        		sketcher.url2 = "nisba"
        		sketcher.url3 = "zilch"
        		sketcher.url4 = "zip"
        		sketcher.location = "so sad!"
        	else:
        		logging.info("user is checking his profile and it's empty")
        		logging.info("quick, let's create one!")
        		sketcher = Sketcher()
        		sketcher.userID = userIDasString
        		sketcher.name = user.nickname
        		sketcher.profileText = ""
        		sketcher.url1 = ""
        		sketcher.url2 = ""
        		sketcher.url3 = ""
        		sketcher.url4 = ""
        		sketcher.put()

        # the table we fetch the thumbnails from depends on whether the author is looking
        # at his own page. In that case, we show all the sketches from the MySketchesSketch table
        # which includes private sketches too.
        # Otherwise if the user is looking at the profile of someone else
        # then we only show the public sketches in the AuthorSketchesSketch table.
        if util.convDecToBase(string._long(user.user_id),62) != userIDasString:
        	logging.info('user is looking at someone else\'s sketches, showing only public sketches from AuthorSketchesSketch table')
        	bookmark = Key.from_path('AuthorSketchesSketch',"-"+ ('%023d' % (util.toBase10(userIDasString,62))) + ZERO_FILL)        	
        	endKey =  Key.from_path('AuthorSketchesSketch','-%023d' % (int(util.toBase10(userIDasString,62)) + 1) + ZERO_FILL)
        	logging.info('starting key  ' + str(bookmark))
        	logging.info('end key  ' + str(endKey))
        	q = db.GqlQuery("SELECT * FROM AuthorSketchesSketch WHERE __key__ >= :1 AND __key__ < :2",bookmark,endKey)
        else:
        	logging.info('user is looking at his own sketches, showing private and public sketches from MySketchesSketch table')
        	bookmark = Key.from_path('MySketchesSketch','-%023d' % (int(user.user_id)) + SKETCH_ZEROS)
        	endKey =  Key.from_path('MySketchesSketch','-%023d' % (int(user.user_id) + 1) + SKETCH_ZEROS)
        	logging.info('starting key  ' + str(bookmark))
        	logging.info('end key  ' + str(endKey))
        	q = db.GqlQuery("SELECT * FROM MySketchesSketch WHERE __key__ >= :1 AND __key__ < :2",bookmark,endKey)
        
        sketches = q.fetch(PAGESIZE+1)
        
        # if there are more sketches than the ones shown here, we show a "more" link
        # that links to the mySketches page
        if len(sketches) == PAGESIZE + 1:
        	next = "yes"
        else:
        	next = ""

        for sketch in sketches:
        	sketch.stringtags = util.shorten(" ".join(sketch.tags),18)
			
        template_values = {
          'sketches':sketches,
          'bookmark':bookmark,
          'next':next,
          'action':"gallery",
          'headerTitle':"Gallery",
          'name':sketcher.name,
          'profileText':sketcher.profileText,
          'location':sketcher.location,
          'url1':sketcher.url1,
          'url2':sketcher.url2,
          'url3':sketcher.url3,
          'url4':sketcher.url4,
          'user_nick_and_id':id,
          'userNickname':sketcher.name,
          'user_id':util.toBase10(sketcher.userID,62),
          'userIDasString':userIDasString
          }
        self.generate('profileTemplate.html',template_values)
        
class showProfileEdit(BaseRequestHandler):
  def get(self):
        next = None
        PAGESIZE = 24

        util.insertUsersideCookies(self)

        self.session = True
        user = UserInfo()
        user.whoIs(self)
        
        if user.nickname == None:
          logging.info("not logged in so redirecting")
          self.redirect("/")
          return
        
        # we try to fetch the profile record of the user
        # the record might not be there if the user visits his edit profile page without having ever seen his
        # profile page. Which is really rare, it should't happen, but we cover all the corners
        query = db.GqlQuery("SELECT * FROM Sketcher WHERE userID = :1", util.convDecToBase(string._long(user.user_id),62))
        sketcher = query.get();


        # if there is no profile record we create one. Again, this really shouldn't happen in
        # practice
        if (sketcher == None):
          logging.info("Creating new empty sketcher")
          sketcher = Sketcher()
          sketcher.name = user.nickname
          sketcher.profileText = ""
          sketcher.url1 = ""
          sketcher.url2 = ""
          sketcher.url3 = ""
          sketcher.url4 = ""

        sketcher.profileText = sourcecode_for_text_area(sketcher.profileText)

        template_values = {
          'action':"gallery",
          'headerTitle':"Gallery",
          'name':sketcher.name,
          'profileText':sketcher.profileText,
          'location':sketcher.location,
          'url1':sketcher.url1,
          'url2':sketcher.url2,
          'url3':sketcher.url3,
          'url4':sketcher.url4,
          'userNickname':user.nickname,
          'userIDasString':util.convDecToBase(string._long(user.user_id),62)
          }
        self.generate('profileEditTemplate.html',template_values)
        
  def post(self):
    util.insertUsersideCookies(self)

    self.session = True
    user = UserInfo()
    user.whoIs(self)
    
    if user == None:
      logging.info("not logged in so redirecting")
      self.redirect("/")
      return
      
    logging.info("Saving profile for: " + user.user_id)
    
    query = db.GqlQuery("SELECT * FROM Sketcher WHERE userID = :1", util.convDecToBase(string._long(user.user_id),62))
    if query.count() > 0:
      logging.info("found existing profile for user")
      sketcher = query.get();
    else:
      sketcher = Sketcher()
      
    sketcher.userID = util.convDecToBase(string._long(user.user_id),62)
    sketcher.name = self.request.get('title_input')
    sketcher.profileText = self.request.get('text_input')
    sketcher.url1 = self.request.get('url1_input')
    sketcher.url2 = self.request.get('url2_input')
    sketcher.url3 = self.request.get('url3_input')
    sketcher.url4 = self.request.get('url4_input')

    sketcher.profileText = clean_sourcecode(sketcher.profileText)


    #sketcher.avatar = db.Blob(self.request.get("avatarPic"))
    if self.request.get("avatarPic") != "":
    	avatarPic = images.Image(self.request.get("avatarPic"))
    	
    	originalWidth = avatarPic.width
    	originalHeight = avatarPic.height
    	logging.info('originalWidth: ' + str(originalWidth))
    	logging.info('originalHeigth: ' + str(originalHeight))
    	logging.info('difference: ' + str(originalWidth - originalHeight))
    	logging.info('proportion of difference: ' + str(float(originalWidth - originalHeight)/float(originalWidth)))
    	logging.info('going to crop this way: ' + str((float(originalWidth - originalHeight)/float(originalWidth))/2.0) + " ,0.0, "+ str(1.0-(float(originalWidth - originalHeight)/float(originalWidth))/2.0) + " , 1.0")
    	
    	if originalWidth > originalHeight:
    		# if the image is wider than tall, then we cut away the two sides of the image so we make it square
    		avatarPic.crop((float(originalWidth - originalHeight)/float(originalWidth))/2.0,0.0,1-(float(originalWidth - originalHeight)/float(originalWidth))/2.0,1.0);
    	
    	elif originalWidth < originalHeight:
    		# if the image is taller than wide, then we cut away top and bottom of the image so we make it square
    		avatarPic.crop(0.0,(float(originalHeight - originalWidth)/float(originalHeight))/2.0,1.0,1-(float(originalHeight - originalWidth)/float(originalHeight))/2.0);
    		
    	squareSideSize = min(originalWidth,originalHeight)
    	
    	# we resize the image only if it's too big
    	# if it's too small we resize it to its own dimensions. This is a dirty
    	# trick so that we do at least one transformation and can invoke
    	# execute_transforms and convert the image to png without getting errors.
    	# The reason is that I want to make sure that all images in the database
    	# are proper .png files and if I don't do at least one transformation I get
    	# an error when invoking "execute_transforms"
    	if squareSideSize > 200:
    		avatarPic.resize(200,200);
    	else:
    		avatarPic.resize(squareSideSize,squareSideSize);


    	# this is because square iages smaller than 200px undergo no transformations, and I get
    	# an error if I invoke "execute_transforms" with no transformations in the pipeline
    	sketcher.avatar = db.Blob(avatarPic.execute_transforms(output_encoding=images.PNG))
    
    sketcher.put()
    
    logging.info('title: ' + self.request.get('title_input'))
    logging.info('text: ' + self.request.get('text_input'))
    logging.info('url1: ' + self.request.get('url1_input'))
    logging.info('url2: ' + self.request.get('url2_input'))
    logging.info('url3: ' + self.request.get('url3_input'))
    logging.info('url4: ' + self.request.get('url4_input'))
    self.redirect("/myPage/" + user.nickname + "-" + util.convDecToBase(string._long(user.user_id),62))


class avatarImage(BaseRequestHandler):
  def get(self, id):
    logging.info("avatar image handler: id from URL: " + id)
    userIDasString = id.replace('.png','')
    userIDasString = userIDasString.partition('-')[2]
    logging.info('most weird: sometimes this ends with justcorners.js : ' + userIDasString)
    userIDasString = userIDasString.partition('/')[0]
    
    query = db.GqlQuery("SELECT * FROM Sketcher WHERE userID = :1", userIDasString)
    logging.info(query.count())
    sketcher = query.get();
    
    # if there is no profile record for this userid
    # or if there is a record but the avatar image is empty
    # then redirect to the no avatar image
    if sketcher == None or sketcher.avatar=="" or sketcher.avatar==None:
      logging.info('got no avatar image, redirecting to default no avatar image')
      self.redirect('/imgs/noAvatar.png')
    else:
      logging.info('got avatar image')
      self.response.headers['Content-Type'] = "image/png"
      self.response.out.write(sketcher.avatar)


