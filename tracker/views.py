from django.db.models import Count
from .models import NutritionLog, FoodGroup, UserProfile
from .forms import NutritionLogForm
from datetime import datetime, timedelta
from django.views.decorators.csrf import csrf_exempt
from django import forms
from django.utils import timezone
from django.contrib import messages
from .forms import NutritionLogForm
from .utils import check_balanced_diet
from django.contrib import messages
import io
import matplotlib.pyplot as plt
import pandas as pd
from django.http import FileResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from .forms import BMICalculatorForm
from allauth.account.views import LoginView, LogoutView, SignupView
from django.shortcuts import render
from io import BytesIO
import tempfile
import os
from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger








@csrf_exempt
def home(request):
    return render(request, 'tracker/home.html',  {'messages': messages.get_messages(request)})
class CustomLoginView(LoginView):
    def get_success_url(self):
        # Handle `next` redirection after login
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return '/'  # Redirect to home page (or your desired URL)

class CustomSignupView(SignupView):
    def get_success_url(self):
        # Handle `next` redirection after signup
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return '/'  # Redirect to home page (or your desired URL)

class CustomLogoutView(LogoutView):
    def get(self, request, *args, **kwargs):
        # Handle custom logout logic
        return redirect('/')  # Redirect to home page (or your desired URL)


class NutritionLogForm(forms.ModelForm):
    food_groups = forms.ModelMultipleChoiceField(
        queryset=FoodGroup.objects.all(),
        widget=forms.CheckboxSelectMultiple,  # Use checkboxes for selection
        required=True
    )

    class Meta:
        model = NutritionLog
        fields = ['food_item', 'quantity', 'notes', 'food_groups'] 



@csrf_exempt
def add_log(request):
    if request.method == 'POST':
        form = NutritionLogForm(request.POST)
        if form.is_valid():
            nutrition_log = form.save(commit=False)
            nutrition_log.user = request.user  # Assuming you have user authentication
            nutrition_log.save()
            form.save_m2m()  # Save many-to-many relationships

            # Check for balanced diet
            balanced_days = check_balanced_diet(request.user)
            if balanced_days > 1:
                messages.warning(request, "You haven't eaten a balanced diet for more than one day. Please include all food groups!")

            # Update balanced diet count
            update_balanced_diet_count(request.user)

            return redirect('success_url')  # Redirect to a success page
        else:
            # If the form is invalid, re-render the form with error messages
            return render(request, 'tracker/add_log.html', {'form': form})
    else:
        form = NutritionLogForm()
        return render(request, 'tracker/add_log.html', {'form': form})



@csrf_exempt
def food_group_distribution(request, period):
    if request.user.is_authenticated:
        if period == '7days':
            start_date = datetime.now() - timedelta(days=7)
        elif period == 'month':
            start_date = datetime.now() - timedelta(days=30)
        else:
            start_date = None

        if start_date:
            logs = NutritionLog.objects.filter(user=request.user, date__gte=start_date)
        else:
            logs = NutritionLog.objects.filter(user=request.user)

        food_groups = FoodGroup.objects.all()
        distribution = {fg.name: logs.filter(food_groups=fg).count() for fg in food_groups}

        return render(request, 'tracker/food_group_distribution.html', {
            'distribution': distribution,
            'period': period
        })
    return redirect('home')



def ranking_view(request):
    # Get all users sorted by balanced_diet_count in descending order
    users = UserProfile.objects.all().order_by('-balanced_diet_count')
    
    # Add pagination to limit the number of users per page
    paginator = Paginator(users, 10)  # Show 10 users per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'tracker/ranking.html', {'page_obj': page_obj})



def generate_report(request):
    # Fetch user data
    user = request.user
    logs = NutritionLog.objects.filter(user=user).order_by('-date')[:30]  # Last 30 days

    # Prepare data for plotting
    if logs.exists():  # Check if there are actual logs
        data = {
            'date': [log.date.strftime('%Y-%m-%d') for log in logs],
            'balanced': [log.balanced for log in logs],  # Assuming balanced is a boolean field
            'food_groups': [log.food_groups for log in logs]  # Assuming food_groups is a list or a comma-separated string
        }
    else:  # Placeholder data if no logs exist
        data = {
            'date': ['No data'],
            'balanced': [0],
            'food_groups': ['']
        }

    df = pd.DataFrame(data)

    # Ensure food_groups is a list
    df['food_groups'] = df['food_groups'].apply(lambda x: x.split(',') if isinstance(x, str) else x)

    # Bar graph: Balanced diet per day
    plt.figure(figsize=(10, 5))
    balanced_per_day = df.groupby('date')['balanced'].sum()
    balanced_per_day.plot(kind='bar', color='#4CAF50')
    plt.title('Balanced Diet per Day')
    plt.xlabel('Date')
    plt.ylabel('Balanced Diet Count')
    bar_graph = BytesIO()
    plt.savefig(bar_graph, format='png')
    bar_graph.seek(0)
    plt.close()

    # Pie chart: Total percentage of balanced diet
    plt.figure(figsize=(5, 5))
    df['balanced'].value_counts().plot(kind='pie', autopct='%1.1f%%', colors=['#4CAF50', '#FF5722'])
    plt.title('Total Percentage of Balanced Diet')
    pie_chart = BytesIO()
    plt.savefig(pie_chart, format='png')
    pie_chart.seek(0)
    plt.close()

    # Table: Frequency of each food group
    food_group_freq = df['food_groups'].explode().value_counts()
    table_data = food_group_freq.reset_index().values.tolist()

    # Create PDF
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Set font for text
    p.setFont("Helvetica", 10)

    # Temporarily save the charts to disk to avoid the issue
    with tempfile.NamedTemporaryFile(delete=False) as bar_file, tempfile.NamedTemporaryFile(delete=False) as pie_file:
        bar_file_path = bar_file.name
        pie_file_path = pie_file.name

        bar_graph.seek(0)
        with open(bar_file_path, 'wb') as f:
            f.write(bar_graph.read())

        pie_chart.seek(0)
        with open(pie_file_path, 'wb') as f:
            f.write(pie_chart.read())

        # Add bar graph to PDF
        p.drawImage(bar_file_path, 50, height - 300, width=500, height=250)

        # Add pie chart to PDF
        p.drawImage(pie_file_path, 50, height - 600, width=250, height=250)

        # Add table data to PDF
        p.drawString(50, height - 650, "Frequency of Each Food Group (Last 30 Days)")
        x_offset = 50
        y_offset = height - 700
        for row in table_data:
            p.drawString(x_offset, y_offset, f"{row[0]}: {row[1]}")
            y_offset -= 20

        # Finalize the PDF
        p.showPage()
        p.save()

    # Delete the temporary files
    os.remove(bar_file_path)
    os.remove(pie_file_path)

    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='nutrition_report.pdf')


def bmi_calculator_view(request):
    user_profile = UserProfile.objects.get(user=request.user)
    gender = user_profile.gender

    if request.method == 'POST':
        form = BMICalculatorForm(request.POST)
        if form.is_valid():
            height = form.cleaned_data['height'] / 100  # Convert cm to meters
            weight = form.cleaned_data['weight']
            bmi = weight / (height**2)

            # Determine BMI category based on gender
            if bmi < 18.5:
                category = 'Underweight'
            elif 18.5 <= bmi < 24.9:
                category = 'Normal weight'
            elif 25 <= bmi < 29.9:
                category = 'Overweight'
            else:
                category = 'Obesity'

            return render(request, 'tracker/bmi_result.html', {
                'bmi': bmi,
                'category': category,
                'gender': gender
            })
    else:
        form = BMICalculatorForm()

    return render(request, 'tracker/bmi_calculator.html', {'form': form})


