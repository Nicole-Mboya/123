from datetime import timedelta
from django.utils import timezone
from .models import Nutrition, UserProfile, FoodGroup



def check_balanced_diet(user):
    today = timezone.now().date()
    # Get logs for the last few days
    logs = NutritionLog.objects.filter(date_logged__gte=today - timedelta(days=7), user=user)

    # Check if each food group is represented
    food_groups = FoodGroup.objects.all()
    balanced_days = 0

    for day in range(7):
        day_logs = logs.filter(date_logged=today - timedelta(days=day))
        logged_groups = set()

        for log in day_logs:
            logged_groups.update(log.food_groups.all())

        if all(group in logged_groups for group in food_groups):
            balanced_days += 1

    return balanced_days
