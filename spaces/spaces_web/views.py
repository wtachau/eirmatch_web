from django.shortcuts import render
from django.core.context_processors import csrf
from spaces_web.models import Post, Comment, User, Tag
from django.http import HttpResponse, HttpResponseRedirect
import json
from django.conf import settings
from django.core import serializers

# Return current user from cookie
def getCurrentUser(request):
	return User.objects.get(googleID=int(request.COOKIES['id']))

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
	# Try to grab user from db if they exist
	try:
		existingUser = User.objects.get(googleID=googleID)
		response.set_cookie('id', existingUser.googleID)
	# otherwise, since we know they are @originate.com, create user
	except User.DoesNotExist:
		email = data['emails[0][value]']
		name = data['displayName']
		image = data['result[image][url]'].split('?')[0]
		newUser = User(name=name, email=email, googleID=googleID, image=image, relevant_tags=[])
		newUser.save()
		response.set_cookie('id', newUser.googleID)
	except Exception as e:
		print "Exception: %s" % e
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
		context.update(csrf(request))

		# generate all tags (for posting suggestions)
		context['tags'] = getAllTags(context['user'])
		return render(request, 'index.html', context)

	# if there was no user logged in
	except:
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
	posts = Post.objects.all()
	postsInfo = []

	userTags = []
	if user:
		userTags = user.relevant_tags

	for post in posts:
		isRelevant = False
		postInfo = {}
		tagnames = []
		for tagID in post.tags:
			# get tag from tag ID
			try:
				tag = Tag.objects.get(id=tagID)
				tagnames.append(tag)
				# Check if tag is relevant to user (if it matches a user tag)
				if user and tagID in userTags:
					isRelevant = True
			except Exception as e:
				print "exception: %s" % e
		# generate dict from model to pass to view
		postInfo['id']=post.id
		postInfo['short_description']=post.short_description
		postInfo['long_description']=post.long_description
		postInfo['numComments']=len(post.comments)
		postInfo['tagnames']=tagnames
		postInfo['poster']=post.poster
		postInfo['email'] = post.poster.email
		postInfo['comments']=post.comments

		# if we're grabbing all posts or is relevant
		if not user or isRelevant:
			postsInfo.append(postInfo)
	return postsInfo


# Receives Ajax request for a new Post.
def addPost(request):
	data = request.POST
	tagIDs = checkIDs(data.getlist('tags'))
	shortDesc = data.getlist('short')[0]
	longDesc = data.getlist('long')[0]	
	try:
		newPost = Post(poster=getCurrentUser(request), short_description=shortDesc, long_description=longDesc, tags=tagIDs, comments=[])
		newPost.save()
		returnPost = {}
		returnPost['postID'] = newPost.id
		returnPost['image'] = newPost.poster.image
		returnPost['short'] = shortDesc
		returnPost['long'] = longDesc
		returnPost['tags'] = ", ".join(map(lambda tag: Tag.objects.get(id=tag).name, newPost.tags))
		returnPost['staticURL'] = settings.STATIC_URL
		returnPost['name'] = newPost.poster.name
		returnPost['email'] = newPost.poster.email
		return HttpResponse(json.dumps(returnPost))
	except Exception as e:
		print e
		return HttpResponse(" error: %s"%e)

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

		returnData = {'postID':postID}
		returnData['numComments'] = len(currentPost.comments)
		returnData['userImage'] = currentUser.image
		returnData['comment'] = comment
		return HttpResponse(json.dumps(returnData))
	except Exception as e:
		return HttpResponse(e)

# Get comments for a Post
def getComments(request):
	data = request.GET

	postID = data.getlist('postID')[0]
	comments = Post.objects.get(id=postID).comments

	returnData = []
	for comment in comments:
		commentData = {}
		commentData['comment'] = comment.text
		commentData['image'] = comment.user.image
	
		returnData.append(commentData)

	# returnData = serializers.serialize('json', returnData)
	return HttpResponse(json.dumps(returnData), mimetype="application/json")


