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

    # admin page
    url(r'^admin/', include(admin.site.urls)),
)
