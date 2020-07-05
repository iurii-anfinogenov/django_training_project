from django.forms import ModelForm
from .models import Post, Comment


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['group', 'text', 'image']
        labels = {
            'group': 'Группа',
            'text': 'Введите текст',
            
        }
        help_texts = {
            'text': 'Это поле обязательно для заполнения',
            'group': 'Выберите группу для записи',
        }


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['text',]        
