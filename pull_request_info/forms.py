from django import forms

from .models import GitUser


class GitHubUserForm(forms.ModelForm):
    class Meta:
        model = GitUser
        fields = ('GitHubUser',)
