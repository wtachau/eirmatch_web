from django.shortcuts import render
from django.core.context_processors import csrf
from spaces_web.models import Post, Comment
from django.http import HttpResponse

def login(request):
	return render(request, 'login.html', {})

def home(request):

	# get relevant posts and most recent
	relevant_posts = Post.objects.all()
	all_posts = Post.objects.all()
	context = {'all_posts': all_posts, 'relevant_posts':relevant_posts}
	context.update(csrf(request))
	return render(request, 'index.html', context)

def addPost(request):
	data = request.POST
	newPost = Post(short_description=data['short'], long_description=data['long'], tags=(1,2,3), comments=[])
	newPost.save()
	return  HttpResponse(newPost.id+" saved")

	# temporary -- create posts
	# comments = []
	# for x in range(3):
	# 	comment = Comment(text="comment")
	# 	comment.save()
	# 	comments.append(comment.id)