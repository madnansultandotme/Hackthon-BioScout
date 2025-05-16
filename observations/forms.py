from django import forms
from django.utils import timezone
from .models import Observation

class ObservationForm(forms.ModelForm):
    class Meta:
        model = Observation
        fields = ['species_name', 'date_observed', 'location', 'image', 'notes']
        widgets = {
            'date_observed': forms.DateInput(attrs={
                'type': 'date',
                'max': timezone.now().date(),
                'class': 'form-control'
            }),
            'notes': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Add any additional notes about your observation'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter location in Islamabad or Margalla Hills'
            }),
            'species_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter species name'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }

    def clean_date_observed(self):
        date = self.cleaned_data.get('date_observed')
        if date and date > timezone.now().date():
            raise forms.ValidationError('Observation date cannot be in the future')
        return date or timezone.now().date()

    def clean_location(self):
        location = self.cleaned_data.get('location', '').strip()
        if not location:
            raise forms.ValidationError('Location is required')
        return location

    def clean_species_name(self):
        species = self.cleaned_data.get('species_name', '').strip()
        if not species:
            raise forms.ValidationError('Species name is required')
        return species

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            if image.size > 5 * 1024 * 1024:  # 5MB limit
                raise forms.ValidationError('Image size must be less than 5MB')
            if not image.content_type.startswith('image/'):
                raise forms.ValidationError('File must be an image')
        return image 