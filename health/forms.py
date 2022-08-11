from django import forms
from .models import Weight
from django.utils import timezone


class HealthSerchForm(forms.Form):
    start_year = 2022
    end_year = timezone.now().year + 1
    years = [(year, f'{year}年')
             for year in reversed(range(start_year, end_year + 1))]
    years.insert(0, (0, ''))
    YEAR_CHOICES = tuple(years)

    months = [(month, f'{month}月') for month in range(1, 13)]
    months.insert(0, (0, ''))
    MONTH_CHOICES = tuple(months)

    year = forms.ChoiceField(
        label='年での絞り込み',
        required=False,
        choices=YEAR_CHOICES,
        widget=forms.Select(attrs={'class': 'form'})
    )

    month = forms.ChoiceField(
        label='月での絞り込み',
        required=False,
        choices=MONTH_CHOICES,
        widget=forms.Select(attrs={'class': 'form'})
    )

class WeightCreateForm(forms.ModelForm):
    class Meta:
        model = Weight
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['body_fat'].widget = forms.HiddenInput()
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form'
            field.widget.attrs['placeholder'] = field.label
            field.widget.attrs['autocomplete'] = 'off'