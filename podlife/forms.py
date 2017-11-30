from django.forms import ModelForm

from podlife.models import Comment


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['comment']
