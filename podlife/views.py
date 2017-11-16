from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.hashers import make_password
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.views.generic import TemplateView, ListView, CreateView, UpdateView

from podlife.forms import CommentsForm
from podlife.models import Comments, Podcasts, Topics, User

class Signup(CreateView):
	template_name = 'registration/signup.html'
	model = User
	fields = ['username', 'first_name', 'last_name', 'email', 'password']

	def get_success_url(self):
		return self.success_url

	def get_context_data(self, **kwargs):
		context = super(Signup, self).get_context_data(**kwargs)
		return context

	def form_valid(self, form):
		self.success_url = '/login/'
		form.instance.password = make_password(form.instance.password)
		return super(Signup, self).form_valid(form)

class Profile(LoginRequiredMixin, TemplateView):
	template_name = 'profile.html'

class LandingPage(TemplateView):
	template_name = 'landing.html'

class Statistics(LoginRequiredMixin, TemplateView):
	template_name = 'statistics.html'

class PodcastListView(ListView):
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
			context = Podcasts.objects.filter(tags__icontains=topic_filter)
		elif title_filter and not topic_filter:
			context = Podcasts.objects.filter(title__icontains=title_filter)
		elif topic_filter and not title_filter:
			context = Podcasts.objects.filter(tags__icontains=topic_filter)
		return context

	def get_context_data(self, **kwargs):
	 	podcasts = super(PodcastListView, self).get_context_data(**kwargs)
	 	podcasts['titlefilter'] = self.request.GET.get('titlefilter', '')
	 	podcasts['topics'] = Topics.objects.all()
	 	return podcasts

class PodcastView(TemplateView):
	template_name = 'view_podcast.html'

	def get_success_url(self):
		return self.success_url

	def get_context_data(self, **kwargs):
		podcast = Podcasts.objects.get(slugfield=kwargs['slugfield'])
		podcast.views += 1
		podcast.save()

		comments = Comments.objects.filter(podcast_id=podcast.id).order_by('-created')
		self.podcast_id = podcast.id
		podcast.tags = ', '.join(podcast.tags)

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

class PodcastsCreate(LoginRequiredMixin, CreateView):
	template_name = 'podcast_form.html'
	model = Podcasts
	fields = ['title', 'description', 'audio_file', 'file_type']

	def get_success_url(self):
		return self.success_url

	def get_context_data(self, **kwargs):
		context = super(PodcastsCreate, self).get_context_data(**kwargs)
		context['action'] = 'Create'
		context['topics'] = Topics.objects.all()
		return context

	def form_valid(self, form):
		form.instance.author = self.request.user
		slugfield = ''.join(w for w in form.instance.title.lower().replace(' ','_') if (w.isalnum() or w=='_'))
		form.instance.slugfield = slugfield
		self.success_url = '/podcast/' + slugfield
		return super(PodcastsCreate, self).form_valid(form)

class PodcastsUpdate(UpdateView):
	template_name = 'podcast_form.html'
	model = Podcasts
	action = 'Edit'
	fields = ['title', 'description', 'audio_file', 'file_type']
	slug_field = 'slugfield'
	slug_url_kwarg = 'slugfield'

	def get_success_url(self):
		return self.success_url

	def get_context_data(self, **kwargs):
		context = super(PodcastsUpdate, self).get_context_data(**kwargs)
		context['action'] = 'Edit'
		context['topics'] = Topics.objects.all()
		print(context['topics'])
		return context

	def form_valid(self, form):
		slugfield = ''.join(w for w in form.instance.title.lower().replace(' ','_') if (w.isalnum() or w=='_'))
		form.instance.updated = timezone.now()
		form.instance.slugfield = slugfield
		form.instance.views -= 1 # ignore view count increment on redirect
		self.success_url = '/podcast/' + slugfield
		return super(PodcastsUpdate, self).form_valid(form)
