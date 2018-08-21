# coding:utf8

from django.conf.urls import url
from . import views
from rest_framework_jwt.views import obtain_jwt_token

urlpatterns = [
    # /users/usernames/(?P<username>\w{5,20})/count/
    url(r'^usernames/(?P<username>\w{5,20})/count/$', views.RegisterUsernameCountAPIView.as_view()),
    # /users/phones/(?P<mobile>1[345789]\d{9})/count/
    url(r'^phones/(?P<mobile>1[345789]\d{9})/count/$', views.RegisterPhoneCountAPIView.as_view()),
    # /users/
    url(r'^$', views.RegisterCreateView.as_view()),
    #  /users/auths/
    url(r'^auths/$', obtain_jwt_token),
    # GET /users/infos/
    url(r'^infos/$', views.UserDetailView.as_view()),
    # PUT /users/emails/
    url(r'^emails/$', views.EmailView.as_view()),
]

from .views import AddressViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'addresses', AddressViewSet, base_name='address')
urlpatterns += router.urls
