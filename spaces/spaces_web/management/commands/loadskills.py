from django.core.management.base import BaseCommand, CommandError
from spaces_web.models import Post, Comment, User, Tag
from pymongo import MongoClient
import os

class Command(BaseCommand):
	help = "Imports skills from mongo dump and updates current collection of users"

	def handle(self, *args, **options):
		try:
			mongo_file = args[0]
			# use mongoimport bash tool to import multiple JSON objects into db
			os.system("mongoimport --db spaces_db --collection spaces_web_users_test --jsonArray %s" % mongo_file)
			
			client = MongoClient()
			new_users = client.spaces_db.spaces_web_users_test
			all_skills = []
			for user in new_users.find():
				# remember all user's skills
				user_skills = map(lambda skill: skill['name'], user['skills'])
				
				# add all new skills to tag db, or update count of existing skill
				tagIDs = []
				for skill in user_skills:
					try:
						existingSkill = Tag.objects.get(name=skill)
						existingSkill.times_used = existingSkill.times_used + 1
						existingSkill.save()
						tagIDs.append(existingSkill.id)
					except Tag.DoesNotExist:
						newTag = Tag(name=skill)
						newTag.save()
						tagIDs.append(newTag.id)

				# if the user is already in our system
				try:
					existing_user = User.objects.get(email=user['email'])
					print "existing user: %s" % user['email']
				# if is a new user
				except:
					print "user created: %s" % user['email']
					email = user['email']
					newUser = User(email=email, relevant_tags=tagIDs)
					newUser.save()

			# drop test db we created
			new_users.drop()
		except Exception as e:
			print "Error: No file given (%s)" % e