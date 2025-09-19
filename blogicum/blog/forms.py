from django import forms
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = (
            'title', 'text', 'pub_date', 'location', 'category', 'image'
        )
        widgets = {
            'pub_date': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pub_date_field = self.fields['pub_date']
        pub_date_field.input_formats = ['%Y-%m-%dT%H:%M']

        if self.data:
            return

        if self.instance.pk and self.instance.pub_date:
            value = self.instance.pub_date
        else:
            value = timezone.now()

        if timezone.is_aware(value):
            value = timezone.localtime(value)

        self.initial.setdefault(
            'pub_date',
            value.replace(second=0, microsecond=0)
        )


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)


User = get_user_model()


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')
