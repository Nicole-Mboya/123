from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now



class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')], default='Male',  # Set a default value
        null=True, 
        blank=True)
    balanced_diet_count = models.IntegerField(default=0)  # Count of days with a balanced diet

    def __str__(self):
        return self.user.username

class FoodGroup(models.Model):
    CATEGORY_CHOICES = [
        ('Protein', 'Protein'),
        ('Carbohydrate', 'Carbohydrate'),
        ('Vitamin', 'Vitamin'),
    ]

    name = models.CharField(max_length=100, unique=True)
    categories = models.ManyToManyField('Category', related_name='food_groups')

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=20, choices=FoodGroup.CATEGORY_CHOICES, unique=True)

    def __str__(self):
        return self.name


class Nutrition(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    food_item = models.CharField(max_length=200)
    food_group = models.ForeignKey(FoodGroup, on_delete=models.SET_NULL, null=True)
    categories = models.ManyToManyField(Category, related_name='nutritions')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(default=now, editable=False) 

    def __str__(self):
        return f"{self.food_item} by {self.user.username}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()

