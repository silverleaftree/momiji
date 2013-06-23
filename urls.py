from django.conf.urls import patterns, include, url

from playapp import views

urlpatterns = patterns('',
    url(r'^$', views.playing),
    url(r'^add_track/$', views.add_track),
    url(r'^create_playlist/$', views.create_playlist),
    url(r'^curate/$', views.curate),
    url(r'^delete_playlist/$', views.delete_playlist),
    url(r'^generate/$', views.generate),
    url(r'^get_suggestions/$', views.get_suggestions),
    url(r'^get_title/$', views.get_title),
    url(r'^mark_played/$', views.mark_played),
    url(r'^modify_track/$', views.modify_track),
    url(r'^new_playlist/$', views.new_playlist),
)
