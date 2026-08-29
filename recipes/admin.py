from django.contrib import admin
from .models import Profile
from .models import Recipe, Like, Rating, Comment

admin.site.register(Profile)
admin.site.register(Recipe)
admin.site.register(Like)
admin.site.register(Rating)
admin.site.register(Comment)