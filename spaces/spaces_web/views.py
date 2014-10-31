from django.shortcuts import render
from django.core.context_processors import csrf
from spaces_web.models import Post, Comment, User
from django.http import HttpResponse

def login(request):
	context = {}
	context.update(csrf(request))
	return render(request, 'login.html', context)

def tryLogin(request):
	data = request.POST
	googleID = data['id']
	response = HttpResponse("success")
	try:
		existingUser = User.objects.get(googleID=googleID)
		response.set_cookie('id', existingUser.googleID)
	except User.DoesNotExist:
		email = data['emails[0][value]']
		name = data['displayName']
		image = data['result[image][url]']
		newUser = User(name=name, email=email, googleID=userID, image=image)
		newUser.save()
		response.set_cookie('id', newUser.googleID)
	return response

def home(request):
	context = {}
	try:
		googleID = int(request.COOKIES['id'])		
		loggedInUser = User.objects.get(googleID=googleID)
		context['user'] = loggedInUser
		# get relevant posts and most recent
		relevant_posts = Post.objects.all() # eventually something about user here
		all_posts = Post.objects.all()
		context['all_posts'] = all_posts
		context['relevant_posts'] = relevant_posts
		context.update(csrf(request))
		return render(request, 'index.html', context)
	except Exception as e:
		print "Exception: %s" % e
		return login(request)

def addPost(request):
	data = request.POST
	newPost = Post(short_description=data['short'], long_description=data['long'], tags=(1,2,3), comments=[])
	newPost.save()
	return  HttpResponse(newPost.id+" saved")
