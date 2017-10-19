from django.conf.urls import url
from . import views

app_name = 'collab_profile'
urlpatterns = [
    url(r'^profile/$', views.Detail.as_view(), name='detail'),
    url(r'^profile/(?P<user_pk>[-\w]+)/$', views.Detail.as_view(), name='detail'),
    url(r'^profile/(?P<user_pk>[-\w]+)/edit/$', views.Edit.as_view(), name='edit'),
    url(r'^profile/(?P<user_pk>[-\w]+)/to_manager/$', views.PromoteToManager.as_view(), name='promote_to_manager'),
    url(r'^profile/(?P<user_pk>[-\w]+)/change_password/$', views.PasswordEdit.as_view(), name='edit_password'),
]