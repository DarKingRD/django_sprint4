from django import forms
from django.contrib.auth.models import User
from .models import Post, Comment
from django.forms import DateTimeInput


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "text", "pub_date", "location", "category", "image"]
        widgets = {
            'pub_date': DateTimeInput(attrs={'type': 'datetime-local'}),
        }


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]


class CommentForm(forms.ModelForm):
    class Meta:
        text = forms.CharField(widget=forms.Textarea)
        model = Comment
        fields = ["text"]
