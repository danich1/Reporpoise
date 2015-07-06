from django.conf.urls import *
from tribe_client import views

urlpatterns = patterns('',
    url(r'^$', views.connect_to_tribe, name='connect_to_tribe'),
    url(r'^logout$', views.logout_from_tribe, name='logout_from_tribe'),
    url(r'^access_genesets$', views.access_genesets, name='access_genesets'),
    url(r'^display_genesets/(?P<access_token>[-_\w]+)/$', views.display_genesets, name='display_genesets'),
    url(r'^display_geneset_versions/(?P<access_token>[-_\w]+)/(?P<geneset>[-_\w]+)/$', views.display_versions, name='display_versions'),
    url(r'^token$', views.return_access_token, name='return_access_token'),
    url(r'^return_user$', views.return_user_obj, name='return_user'),
    url(r'^create_geneset$', views.create_geneset, name='create_geneset'),

)

