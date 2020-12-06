from django.urls import path
from . import views

urlpatterns = [
    path('',views.home) #when this url called, go to home method in views
    
]