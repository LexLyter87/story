from django import forms
from .models import Story, Comment, UserProfile
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from slugify import slugify
from ckeditor.widgets import CKEditorWidget


class StoryForm(forms.ModelForm):
    content = forms.CharField(label='Текст рассказа', widget=CKEditorWidget(attrs={'class': 'form-control'}))
    class Meta:
        model = Story
        fields = ['title', 'content', 'excerpt', 'category', 'cover_image', 'status']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'excerpt': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Краткое описание для превью...'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'cover_image': forms.FileInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def clean_title(self):
        title = self.cleaned_data['title']
        if not slugify(title):
            raise forms.ValidationError("Заголовок должен содержать хотя бы одну букву или цифру.")
        return title


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Оставьте свой комментарий...'}),
        }
        labels = {
            'content': '',
        }


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Ваш Email'}) 
    )

    class Meta:
        model = User
        fields = ["username", "email"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Имя пользователя'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Придумайте пароль'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Повторите пароль'})


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Пользователь с таким именем уже существует.")
        return username
    
    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Пользователь с таким email уже существует.")
        return email


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['avatar', 'bio']
        widgets = {
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
