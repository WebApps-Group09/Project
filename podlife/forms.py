from django.forms import ModelForm

from podlife.models import Comments

class CommentsForm(ModelForm):
  class Meta:
    model = Comments
    fields = ['comment']
