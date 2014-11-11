from django.contrib import admin

from spaces_web.models import Post

# Wrapper to see if item is active
# class ActivateAdmin(admin.ModelAdmin):
#     actions=['activate','deactivate']
    
#     def activate(self, request, queryset):
#         for c in queryset:
#             c.active = True
#             c.save()
            
#     def deactivate(self, request, queryset):
#         for c in queryset:
#             c.active = False
#             c.save()    

# class PostAdmin(ActivateAdmin):
# 	list_display = ['short_description', 'long_description']


# admin.site.register(Post, PostAdmin)