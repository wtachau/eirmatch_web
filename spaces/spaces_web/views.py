from django.shortcuts import render
from django.core.context_processors import csrf
from spaces_web.models import Post, Comment, User, Tag
from django.http import HttpResponse, HttpResponseRedirect
import json
from django.conf import settings
from django.core import serializers

# Return current user from cookie
def getCurrentUser(request):
	try:
		return User.objects.get(googleID=int(request.COOKIES['id']))
	except Exception as e:
		print "Error getting current user: %s" % e

def login(request):
	context = {}
	context.update(csrf(request))
	return render(request, 'login.html', context)

def logout(request):
	response = HttpResponseRedirect("login")
	response.delete_cookie('id')
	return response

def tryLogin(request):
	data = request.POST
	googleID = data['id']
	response = HttpResponse("success")
	# Try to grab user from db if they have already logged in
	try:
		existingUser = User.objects.get(googleID=googleID)
		response.set_cookie('id', existingUser.googleID)
	except User.DoesNotExist:
		try:
			# otherwise, look for pre-created user to match
			precreatedUser = User.objects.get(email=data['emails[0][value]'])
			precreatedUser.name = data['displayName']
			precreatedUser.image = data['result[image][url]'].split('?')[0]
			precreatedUser.googleID=googleID
			precreatedUser.save()
			response.set_cookie('id', googleID)
			response.set_cookie('first_login', True)

		except Exception as e:
			try:
				print "Exception: %s (user not in database)" % e
				# user is not in database at all
				name = data['displayName']
				image = data['result[image][url]'].split('?')[0]
				email = data['emails[0][value]']
				newUser = User(name=name, email=email, googleID=googleID, image=image, relevant_tags=[])
				newUser.save()
				response.set_cookie('id', newUser.googleID)
				response.set_cookie('first_login', True)
			except Exception as e:
				print e
	except Exception as e:
		print "Exception: %s (unexpected error)" % e
	return response

def home(request):

	# See if there is a user logged in
	try:	
		context = {}
		context['user'] = getCurrentUser(request)
		# get relevant posts and most recent
		relevant_posts =  getPostsInfo(user=context['user'])
		all_posts = getPostsInfo(user=None)
		context['all_posts'] = all_posts
		context['relevant_posts'] = relevant_posts
		if all_posts:
			context['display_post'] = relevant_posts[0] if len(relevant_posts) > 0 else all_posts[0]
		context.update(csrf(request))

		# if this is their first time logging in 
		if ('first_login' in request.COOKIES):
			context['first_login'] = True

		# generate all tags (for posting suggestions)
		context['tags'] = getAllTags(context['user'])
		context['STATIC_URL'] = settings.STATIC_URL
		response =  render(request, 'index.html', context)
		# make sure first login cookie is gone
		if ('first_login' in request.COOKIES):
			response.delete_cookie('first_login')
		return response
	
	# if there was no user logged in
	except Exception as e:
		print "Error in home login: %s" % e
		return HttpResponseRedirect("login")
	

# Return all tags, noting those that are relevant to the user
def getAllTags(user):
	allTags = Tag.objects.all()
	userTags = user.relevant_tags
	
	tagObjects = []
	for tag in allTags:
		tagObject = {}
		tagObject['name'] = tag.name
		if tag.id in userTags:
			tagObject['userRelevant'] = True
		else:
			tagObject['userRelevant'] = False
		tagObjects.append(tagObject)
	return tagObjects


# Gets information for Posts. 
# If user is set, only include posts specific to that user.
def getPostsInfo(user):
	posts = Post.objects.all().order_by('date_updated').reverse()
	postsInfo = []

	userTags = []
	if user:
		userTags = user.relevant_tags
	for post in posts:
		isRelevant = False
		postInfo = {}
		# get tag names from ids
		tagnames = " ".join(map(lambda tagID: Tag.objects.get(id=tagID).name, post.tags))
		# see if there are any user tags in the post
		if len(filter(lambda x: x in userTags, post.tags)) > 0:
			isRelevant = True
		# if we're grabbing all posts or is relevant
		if not user or isRelevant:
			postsInfo.append(getSinglePostInfo(post))
	return postsInfo

# Receives Ajax request for a new Post.
def addPost(request):
	data = request.POST
	tagIDs = checkIDs(data.getlist('tags'))
	shortDesc = data.getlist('short')[0]
	longDesc = data.getlist('long')[0]	
	try:
		post = Post(poster=getCurrentUser(request), short_description=shortDesc, long_description=longDesc, tags=tagIDs, comments=[])
		post.save()
		return HttpResponse(json.dumps(getSinglePostInfo(post)))
	except Exception as e:
		return HttpResponse(" error: %s"%e)

# Get a view-friendly version of the Post info we need
def getSinglePostInfo(post):
	return {	'id':post.id,
				'image': post.poster.image,
				'short_description': post.short_description,
				'long_description': post.long_description,
				'tags': map(lambda tag: {'id': Tag.objects.get(id=tag).id, 'name':Tag.objects.get(id=tag).name}, post.tags),
				'staticURL': settings.STATIC_URL,
				'poster': post.poster.name,
				'displayName': post.poster.name.split(" ")[0],
				'email': post.poster.email,
				'numComments': len(post.comments)
			}

# Helper function for adding a Post
# Input: list of strings used as tags in a post
# Output: list of those tags' IDs. Adds any new tags to db.
def checkIDs(tagStrings):
	tagIDs = []
	for tagString in tagStrings:
		try:
			# if it exists already
			existingTag = Tag.objects.get(name=tagString)
			tagIDs.append(existingTag.id)
		except Tag.DoesNotExist:
			# if we create it
			newTag = Tag(name=tagString)
			newTag.save()
			tagIDs.append(newTag.id)
	return tagIDs


# Receives an Ajax request from the webpage to update the user's tags
def updateTags(request):
	data = request.POST
	tagIDs = checkIDs(data.getlist('tags'))
	user = getCurrentUser(request)
	try:
		user.relevant_tags = tagIDs
		user.save()
		return HttpResponse("success")
	except Exception as e:
		return HttpResponse(e)

# Add a comment to a Post
def addComment(request):
	data = request.POST
	postID = data.getlist('postID')[0]
	comment = data.getlist('comment')[0]
	currentUser = getCurrentUser(request)
	try:
		currentPost = Post.objects.get(id=postID)
		currentPost.comments.append(Comment(text=comment, user=currentUser))
		currentPost.save()

		returnData = {	'postID': postID, 
						'numComments': len(currentPost.comments),
						'userImage': currentUser.image,
						'userFirstName': currentUser.name.split(" ")[0],
						'comment': comment }
		return HttpResponse(json.dumps(returnData))
	except Exception as e:
		return HttpResponse(e)

# Get Info for a Post
def getPostInfo(request):
	data = request.GET

	# fetch the Post Object and current User
	postID = data.getlist('postID')[0]
	returnData = {}

	# get post info (todo)

	# is the user following this post?
	returnData["following"] = postID in getCurrentUser(request).following
	
	# get all comments
	returnComments = []
	comments = Post.objects.get(id=postID).comments
	for comment in comments:
		commentData = { 'comment': comment.text,
						'image': comment.user.image,
						'userFirstName': comment.user.name.split(" ")[0] }
		returnComments.append(commentData)
	returnData["comments"] = returnComments

	return HttpResponse(json.dumps(returnData), mimetype="application/json")

def getRelevantTickets(request):
	print json.dumps(getPostsInfo(user=getCurrentUser(request)))
	return HttpResponse(json.dumps(getPostsInfo(user=getCurrentUser(request))))

def getPostsByTag(request):
	tagID = request.GET.getlist('tagID')[0]
	print request.GET
	print tagID
	relevantPosts = []
	for post in Post.objects.all():
		if tagID in post.tags:
			relevantPosts.append(post)
	relevantPostsJSON = map(lambda post: getSinglePostInfo(post), relevantPosts)
	return HttpResponse(json.dumps(relevantPostsJSON))
def follow(request):
	data = request.POST
	user = getCurrentUser(request)
	if data['postID'] in user.following:
		user.following.remove(data['postID'])
		user.save()
		return HttpResponse("unfollowed")
	else:
		user.following.append(data['postID'])
		user.save()
		return HttpResponse("followed")
	


