from django.urls import path
from . import views
app_name = 'tracker'

urlpatterns = [
     path('', views.home, name='home'),
    path('add/', views.add_nutrition, name='add_nutrition'),
    path('food_group_distribution/', views.food_group_distribution, name='food_group_distribution'),
    path('login/', views.CustomLoginView.as_view(), name='account_login'),
    path('signup/', views.CustomSignupView.as_view(), name='account_signup'),
    path('logout/', views.CustomLogoutView.as_view(), name='account_logout'),
    path('ranking/', views.ranking_view, name='ranking'),
    path('generate_report/', views.generate_report, name='generate_report'),
    path('bmi_calculator/', views.bmi_calculator_view, name='bmi_calculator'),
]
