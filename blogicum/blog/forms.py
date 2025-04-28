from django import forms

# Импортируем класс модели Birthday.
from .models import Post

class PostForm(forms.ModelForm):
    class Meta:
        # Указываем модель, на основе которой должна строиться форма.
        model = Post
        # Указываем, что надо отобразить все поля.
        fields = ['title','text','pub_date','location','category','is_published']
        widgets = {
            'pub_date': forms.DateTimeInput(attrs={
                'type': 'datetime-local',  # HTML5 input type
                'class': 'form-control'   # Дополнительные классы, если нужно
            })
        }