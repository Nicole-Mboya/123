from django import forms
from .models import Nutrition, FoodGroup, Category

class NutritionWithFoodGroupForm(forms.ModelForm):
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Categories"
    )
    food_group_name = forms.CharField(max_length=100, required=False, label="New Food Group (Optional)")

    class Meta:
        model = Nutrition
        fields = ['food_item', 'food_group', 'categories', 'notes']

    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        widget=forms.CheckboxSelectMultiple,  # or forms.SelectMultiple for a dropdown
        required=True    
    )
    def clean(self):
        cleaned_data = super().clean()
        food_group_name = cleaned_data.get('food_group_name')

        # If the user provides a new food group name, create it
        if food_group_name:
            food_group, created = FoodGroup.objects.get_or_create(name=food_group_name)
            cleaned_data['food_group'] = food_group

        return cleaned_data



class BMICalculatorForm(forms.Form):
    height = forms.FloatField(label='Height (cm)')
    weight = forms.FloatField(label='Weight (kg)')        