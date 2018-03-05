from django.conf.urls import include
from django.urls import path

from manager.views import manager, subscribers, publishers

urlpatterns = [
    path('', include('manager.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/signup/', manager.SignUpView.as_view(), name='signup'),
    path('accounts/signup/subscriber/', subscribers.SubscriberSignUpView.as_view(), name='subscriber_signup'),
    path('accounts/signup/publisher/', publishers.PublisherSignUpView.as_view(), name='publisher_signup'),
]
