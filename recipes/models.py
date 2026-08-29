from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
class Recipe(models.Model):
    CATEGORY_CHOICES = [
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('snacks', 'Snacks & Quick Bites'),
    ]

    COST_CHOICES = [
        ('under_50', 'Under ₹50'),
        ('50_100', '₹50 – ₹100'),
        ('100_200', '₹100 – ₹200'),
        ('above_200', 'Above ₹200'),
    ]

    title=models.CharField(max_length=200)
    description=models.TextField()
    ingredients=models.TextField()
    steps=models.TextField()
    image=models.ImageField(upload_to='recipes/',blank=True,null=True)
    category=models.CharField(max_length=20,choices=CATEGORY_CHOICES,default='dinner')
    created_by=models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True,related_name='recipes')
    prep_time=models.PositiveIntegerField(blank=True,null=True,help_text='Minutes')
    servings=models.PositiveIntegerField(blank=True,null=True)
    cost_estimate=models.CharField(max_length=20,choices=COST_CHOICES,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    def __str__(self):
     return self.title 

    def like_count(self):
        return self.likes.count()

    def avg_rating(self):
        ratings = self.ratings.all()
        if not ratings:
            return 0
        return round(sum(r.stars for r in ratings) / ratings.count(), 1)

    def rating_count(self):
        return self.ratings.count()


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='liked_recipes')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'recipe')

    def __str__(self):
        return f"{self.user.username} likes {self.recipe.title}"


class Rating(models.Model):
    STAR_CHOICES = [(i, str(i)) for i in range(1, 6)]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings_given')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ratings')
    stars = models.PositiveSmallIntegerField(choices=STAR_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'recipe')

    def __str__(self):
        return f"{self.user.username} rated {self.recipe.title}: {self.stars}★"


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} on {self.recipe.title}"

class Profile(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    profile_pic=models.ImageField(upload_to='profile/',blank=True,null=True)
    bio=models.TextField(blank=True)
    def __str__(self):
      return self.user.username

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
