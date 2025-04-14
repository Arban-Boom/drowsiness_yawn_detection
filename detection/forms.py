from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, DriverProfile


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    license_number = forms.CharField(
        max_length=20, required=True, help_text="Enter your vehicle's license plate.")
    phone_number = forms.CharField(
        max_length=15, required=True, help_text="Enter your phone number.")

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('email', 'password1', 'password2',
                  'license_number', 'phone_number')

    def save(self, commit=True):
        user = super().save(commit=False)
        # Set the username to the email
        user.username = self.cleaned_data['email']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            DriverProfile.objects.create(
                user=user,
                license_number=self.cleaned_data['license_number'],
                phone_number=self.cleaned_data['phone_number']
            )
        return user
