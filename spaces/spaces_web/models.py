from django.db import models
from djangotoolbox.fields import EmbeddedModelField, ListField
from datetime import datetime 

class Tag(models.Model):
	name = models.CharField(max_length=255)
	times_used = models.IntegerField(null=True, default=1)

	def __str__(self):
		return self.name

class User(models.Model):
	name = models.CharField(max_length=255)
	email = models.CharField(max_length=255)
	googleID = models.CharField(max_length=255)
	image = models.CharField(max_length=255)
	relevant_tags = ListField(models.CharField(max_length=255))
	following = ListField(models.CharField(max_length=255))

	def __str__(self):
		return self.name

class Comment(models.Model):
	text = models.TextField()
	user = models.ForeignKey(User)
	def __str__(self):
		return self.text

class Post(models.Model):
	poster = models.ForeignKey(User)
	short_description = models.TextField()
	long_description = models.TextField()
	followers = ListField(models.CharField(max_length=255))
	tags = ListField(models.CharField(max_length=255))
	comments = ListField(EmbeddedModelField(Comment))
	active = models.BooleanField(default=True)
	date_created = models.DateTimeField(default=datetime.now)
	date_updated = models.DateTimeField(default=datetime.now)

	def __str__(self):
		return self.short_description
