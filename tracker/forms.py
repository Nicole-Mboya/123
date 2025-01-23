from django import forms
from .models import NutritionLog

class NutritionLogForm(forms.ModelForm):
    class Meta:
        model = NutritionLog
        fields = ['food_item', 'quantity', 'notes', 'food_group']

class BMICalculatorForm(forms.Form):
    height = forms.FloatField(label='Height (cm)')
    weight = forms.FloatField(label='Weight (kg)')        