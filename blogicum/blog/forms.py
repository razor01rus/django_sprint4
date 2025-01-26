from django import forms # type: ignore
from django.core.mail import send_mail # type: ignore
from django.core.exceptions import ValidationError # type: ignore

from .models import Post, User, Comment

class PostForm(forms.ModelForm):
    
    class Meta:
        # Указываем модель, на основе которой должна строиться форма.
        model = Post
        exclude = ('author',)
        # Указываем, что надо отобразить все поля.
        fields = '__all__'

        widgets = {
            'post': forms.DateInput(attrs={'type': 'date'}),
            'pub_date': forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def clean_first_name(self):
        # Получаем значение имени из словаря очищенных данных.
        first_name = self.cleaned_data['first_name']
        # Разбиваем полученную строку по пробелам 
        # и возвращаем только первое имя.
        return first_name.split()[0]
    

class CommentForm(forms.ModelForm):
    
    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': forms.Textarea({'rows': '3'})
        }


class UserForm(forms.ModelForm):
    
    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'username',
            'email',
        ) 