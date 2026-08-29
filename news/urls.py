from django.urls import path
from . import views

urlpatterns = [
    path('', views.food_news, name='food_news'),
]
