from django.db import models
from djangotoolbox.fields import ListField
from .forms import StringListField

class StringField(ListField):
    def formfield(self, **kwargs):
        return models.Field.formfield(self, StringListField, **kwargs)

class Comment(models.Model):
    text = models.TextField()  
    def __str__(self):
		return self.text

class Post(models.Model):
	short_description = models.TextField()
	long_description = models.TextField()
	tags = ListField(models.CharField())
	comments = ListField(models.ForeignKey(Comment))
	active = models.BooleanField(default=True)

	def __str__(self):
		return self.short_description

class User(models.Model):
	name = models.CharField(max_length=255)
	email = models.CharField(max_length=255)
	googleID = models.CharField(max_length=255)
	image = models.CharField(max_length=255)

	def __str__(self):
		return self.name