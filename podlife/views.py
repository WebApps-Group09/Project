from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse
from django.utils import timezone
from django.views.generic import TemplateView, ListView, CreateView, UpdateView

from podlife.forms import CommentsForm
from podlife.models import Comments, Podcasts, Topics

## Admin Pages

class ManageTopics(ListView):
  template_name = 'manage_topics.html'
  model = Topics
  context_object_name = 'topics'

class CreateTopic(CreateView):
  template_name = 'create_topic.html'
  model = Topics
  slug_field = 'topic'
  success_url = '/control/topic/'
  fields = ['topic', 'description']

## Main Pages

class HomePage(TemplateView):
  template_name = 'home.html'

class PodcastList(ListView):
  template_name = 'list_podcasts.html'
  model = Podcasts
  context_object_name = 'podcasts'

  def get_queryset(self):
    title_filter = self.request.GET.get('titlefilter', '')
    topic_filter = self.request.GET.get('topicfilter', '')
    if not title_filter and not topic_filter:
      context = Podcasts.objects.order_by('-created')
    elif title_filter and topic_filter:
      context = Podcasts.objects.filter(title__icontains=title_filter)
      context = Podcasts.objects.filter(topic__icontains=topic_filter)
    elif title_filter and not topic_filter:
      context = Podcasts.objects.filter(title__icontains=title_filter)
    elif topic_filter and not title_filter:
      context = Podcasts.objects.filter(topic__icontains=topic_filter)
    return context

  def get_context_data(self, **kwargs):
    podcasts = super(PodcastList, self).get_context_data(**kwargs)
    podcasts['titlefilter'] = self.request.GET.get('titlefilter', '')
    podcasts['topics'] = Topics.objects.all()
    return podcasts

# Redirect to a random podcast
def random(request):
  podcast = Podcasts.objects.random()
  if podcast:
    return HttpResponseRedirect('/podcast/'+podcast.slugfield)
  else:
    return HttpResponseRedirect('/list/')

class PodcastView(TemplateView):
  template_name = 'view_podcast.html'

  def get_success_url(self):
    return self.success_url

  def get_context_data(self, **kwargs):
    podcast = Podcasts.objects.get(slugfield=kwargs['slugfield'])
    podcast.views += 1
    podcast.save()
    comments = Comments.objects.filter(podcast_id=podcast.id).order_by('-created')
    context = {}
    context['podcast'] = podcast
    context['comments'] = comments
    return context

  def post(self, request, *args, **kwargs):
    if request.method == 'POST':
      form = CommentsForm(request.POST)
      if form.is_valid():
        podcast = Podcasts.objects.get(slugfield=kwargs['slugfield'])
        podcast.num_comments += 1
        podcast.views -= 1 # ignore view count increment on redirect
        podcast.save()

        comment = form.save(commit=False)
        comment.podcast = podcast
        comment.author = self.request.user
        comment.save()
      return HttpResponseRedirect('/podcast/' + kwargs['slugfield'] + '/')

## Dashboard

class Dashboard(LoginRequiredMixin, TemplateView):
  template_name = 'dashboard.html'

class Statistics(LoginRequiredMixin, TemplateView):
  template_name = 'statistics.html'

class UserSettings(LoginRequiredMixin, UpdateView):
  template_name = 'settings.html'
  model = User
  fields = ['first_name', 'last_name', 'email']
  success_url = '/dashboard/settings/'

  def get_object(self, queryset=None):
    return self.request.user

  def get_context_data(self, **kwargs):
    context = super(UserSettings, self).get_context_data(**kwargs)
    return context

class PodcastManage(LoginRequiredMixin, ListView):
  template_name = 'manage_podcasts.html'
  model = Podcasts
  context_object_name = 'podcasts'

  def get_queryset(self):
    context = Podcasts.objects.filter(author__id=self.request.user.id)
    return context

class PodcastUpload(LoginRequiredMixin, CreateView):
  template_name = 'podcast_form.html'
  model = Podcasts
  fields = ['title', 'description', 'audio_file', 'file_type']

  def get_success_url(self):
    return self.success_url

  def get_context_data(self, **kwargs):
    context = super(PodcastUpload, self).get_context_data(**kwargs)
    context['title'] = 'Upload a Podcast'
    context['topics'] = Topics.objects.all()
    return context

  def form_valid(self, form):
    topic_id = self.request.POST['topics']
    form.instance.topic = Topics.objects.get(id=topic_id)
    form.instance.author = self.request.user
    slugfield = ''.join(w for w in form.instance.title.lower().replace(' ','_') if (w.isalnum() or w=='_'))
    form.instance.slugfield = slugfield
    self.success_url = '/podcast/' + slugfield
    
    return super(PodcastUpload, self).form_valid(form)

  def form_invalid(self, form):
    print(form.errors)
    return HttpResponse("invalid")

class PodcastUpdate(LoginRequiredMixin, UpdateView):
  template_name = 'podcast_form.html'
  model = Podcasts
  fields = ['title', 'description', 'audio_file', 'file_type']
  slug_field = 'slugfield'
  slug_url_kwarg = 'slugfield'

  def get_success_url(self):
    return self.success_url

  def get_context_data(self, **kwargs):
    context = super(PodcastUpdate, self).get_context_data(**kwargs)
    context['title'] = 'Edit Podcast'
    context['topics'] = Topics.objects.all()
    print(context['topics'])
    return context

  def form_valid(self, form):
    slugfield = ''.join(w for w in form.instance.title.lower().replace(' ','_') if (w.isalnum() or w=='_'))
    form.instance.updated = timezone.now()
    form.instance.slugfield = slugfield
    form.instance.views -= 1 # ignore view count increment on redirect
    self.success_url = '/podcast/' + slugfield
    return super(PodcastUpdate, self).form_valid(form)
