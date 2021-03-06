from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

from spaces_web import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'spaces.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^$', views.home, name="home"),
    url(r'^login$', views.login, name="login"),
    url(r'^logout$', views.logout, name="logout"),

    # ajax responses
    url(r'^addPost$', views.addPost, name="addPost"),
    url(r'^tryLogin$', views.tryLogin, name="tryLogin"),
    url(r'^updateTags$', views.updateTags, name="updateTags"),
    url(r'^addComment$', views.addComment, name="addComment"),
    url(r'^getPostInfo$', views.getPostInfo, name="getPostInfo"),
    url(r'^getAllTickets$', views.getAllTickets, name="getAllTickets"),
    url(r'^getPostsByTag$', views.getPostsByTag, name="getPostsByTag"),
    url(r'^follow$', views.follow, name="follow"),

    # admin page
    url(r'^admin/', include(admin.site.urls)),
)
