from django.urls import path
from . import views
urlpatterns = [
    path('', views.home, name="home"),
    path('add/', views.add_recipe, name='add_recipe'),
    path('recipe/<int:recipe_id>/', views.recipe_detail, name='recipe_detail'),
    path('recipe/<int:recipe_id>/like/', views.toggle_like, name='toggle_like'),
    path('recipe/<int:recipe_id>/edit/', views.edit_recipe, name='edit_recipe'),
    path('recipe/<int:recipe_id>/delete/', views.delete_recipe, name='delete_recipe'),
    path('recipe/<int:recipe_id>/rate/', views.rate_recipe, name='rate_recipe'),
    path('recipe/<int:recipe_id>/comment/', views.add_comment, name='add_comment'),
    path('signup/',views.signup_view,name='signup'),
    path('login/',views.login_view,name='login'),
    path('logout/',views.logout_view,name='logout'),
    path('profile/',views.profile_view,name='profile'),
    ]

