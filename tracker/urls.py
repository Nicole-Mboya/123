from django.urls import path
from .views import CustomLoginView, CustomSignupView, CustomLogoutView
from . import views
from .views import home, add_log, food_group_distribution, ranking_view, generate_report, bmi_calculator_view


urlpatterns = [
    path('', home, name='home'),
    path('add/', add_log, name='add_log'),
    path('distribution/<str:period>/', food_group_distribution, name='food_group_distribution'),
    path('login/', CustomLoginView.as_view(), name='account_login'),
    path('signup/', CustomSignupView.as_view(), name='account_signup'),
    path('logout/', CustomLogoutView.as_view(), name='account_logout'),
    path('ranking/', ranking_view, name='ranking'),
    path('generate_report/', generate_report, name='generate_report'),
    path('bmi_calculator/', bmi_calculator_view, name='bmi_calculator'),
    
   ]

