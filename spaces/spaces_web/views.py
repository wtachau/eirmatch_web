from django.shortcuts import render
from django.core.context_processors import csrf
from spaces_web.models import Post, Comment, User, Tag
from django.http import HttpResponse, HttpResponseRedirect
import json

# Return current user from cookie
def currentUser(request):
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
		newUser = User(name=name, email=email, googleID=googleID, image=image)
		newUser.save()
		response.set_cookie('id', newUser.googleID)
	except Exception as e:
		print "Exception: %s" % e
	return response

def home(request):
	
	# See if there is a user logged in
	try:	
		context = {}
		context['user'] = currentUser(request)

		# get relevant posts and most recent
		relevant_posts =  getPostsInfo(user=None)#context['user'])
		all_posts = getPostsInfo(user=None)
		context['all_posts'] = all_posts
		context['relevant_posts'] = relevant_posts
		context.update(csrf(request))

		# generate all tags (for posting suggestions)
		context['tags'] = Tag.objects.all()
		return render(request, 'index.html', context)

	# if there was no user logged in
	except:
		return HttpResponseRedirect("login")
	

# Gets information for Posts. 
# If user is set, only include posts specific to that user.
def getPostsInfo(user):
	postsInfo = []
	if not user:
		posts = Post.objects.all()
	else:
		posts = Post.objects.all() #fixme

	for post in posts:
		postInfo = {}
		tagnames = []
		for tagString in post.tags:
			try:
				tag = Tag.objects.get(id=tagString)
				tagnames.append(tag)
			except Exception as e:
				print "exception: %s" % e
		# generate dict from model to pass to view
		postInfo['id']=post.id
		postInfo['short_description']=post.short_description
		postInfo['long_description']=post.long_description
		postInfo['numComments']=len(post.comments)
		postInfo['tagnames']=tagnames
		postsInfo.append(postInfo)
	return postsInfo


# Receives Ajax request for a new Post.
def addPost(request):
	data = request.POST
	tagIDs = checkIDs(data.getlist('tags'))
	try:
		newPost = Post(poster=currentUser(request), short_description=data['short'], long_description=data['long'], tags=tagIDs, comments=[])
		newPost.save()
		return HttpResponse(newPost)
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
