from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import Comment, Post

User = get_user_model()


class PostForm(forms.ModelForm):
    pub_date = forms.DateTimeField(
        label="Дата публикации",
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"
        ),
        input_formats=("%Y-%m-%dT%H:%M",),
    )

    class Meta:
        model = Post
        fields = ("title", "text", "pub_date", "category", "location", "image")


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("text",)
        widgets = {"text": forms.Textarea(attrs={"rows": 3})}


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "username", "email")


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(label="Адрес электронной почты")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email",)

    def save(self, commit: bool = True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user
