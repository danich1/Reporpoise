from django.conf.urls import url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from . import views
# These are all the available urls for django
# Add all the urls that belong to drug_search here
urlpatterns = [
    url(r'^$', views.initialize, name="start"),
    url(r'^search$', views.search, name="search"),
    url(r'^grab_data$', views.grab_data, name="grab_data"),
    url(r'^network$',views.network, name="network"),
    url(r'^networktize$',views.networktize, name="networktize"),
    url(r'^reference$', views.reference, name="references"),
    url(r'^test$', views.test,name="test")
]
#This last part is important so django can find static files in the static folder
urlpatterns += staticfiles_urlpatterns()