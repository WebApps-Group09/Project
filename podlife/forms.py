from django.forms import ModelForm

from podlife.models import Comments, Podcasts

class CommentsForm(ModelForm):
  class Meta:
    model = Comments
    fields = ['comment']
    