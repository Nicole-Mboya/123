from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')], default='Male',  # Set a default value
        null=True, 
        blank=True)
    balanced_diet_count = models.IntegerField(default=0)  # Count of days with a balanced diet

    def __str__(self):
        return self.user.username

class FoodGroup(models.Model):
       name = models.CharField(max_length=100)

       def __str__(self):
           return self.name

class NutritionLog(models.Model):
       user = models.ForeignKey(User, on_delete=models.CASCADE)
       date = models.DateField(auto_now_add=True)
       food_item = models.CharField(max_length=100)
       quantity = models.CharField(max_length=50)
       notes = models.TextField(blank=True)
       food_group = models.ForeignKey(FoodGroup, on_delete=models.CASCADE)

       def __str__(self):
           return f"{self.food_item} - {self.date}"