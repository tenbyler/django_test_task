from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, User


class UserRegisterForm(UserCreationForm):
    ROLES = ((1, u"Creator"),
             (2, u"Completer"))

    email = forms.EmailField()
    role = forms.ChoiceField(choices=ROLES)

    class Meta:
        model = User
        fields = ['username', 'email', 'role', 'password1', 'password2']


class UserUpdateForm(forms.ModelForm):
    ROLES = ((1, u"Creator"),
             (2, u"Completer"))

    email = forms.EmailField()
    role = forms.ChoiceField(choices=ROLES)

    class Meta:
        model = User
        fields = ['username', 'email', 'role']


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image']

