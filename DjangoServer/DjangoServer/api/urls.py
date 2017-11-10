'''
Created on 2017/10/25

@author: CSYSBP01
'''

from rest_framework import routers
# from .views import CountViewSet

from django.conf.urls import url
from django.contrib import admin

from .views import (
    CountListAPIView,
#     CountDetailAPIView
    )

urlpatterns = [
#     url(r'^.*',CountListAPIView.as_view(),name='list'),
    url(r'',CountListAPIView.as_view()),
#     url(r'^(?P<cnt>[\w-]+)/$', CountDetailAPIView.as_view(), name='detail'),
]

# router = routers.DefaultRouter()
# router.register(r'counts', CountViewSet)