from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse
from django.utils import timezone
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView

from podlife.forms import CommentForm
from podlife.models import Comment, Podcast, Topic, CreatorSubscription
# from podlife.models import CreatorSubscription, TopicSubscription


# Main Pages
# Landing page for initial user interaction with the website
class HomePage(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super(HomePage, self).get_context_data(**kwargs)
        context['topics'] = Topic.objects.all().order_by('topic')
        return context


# Main page for trending podcasts and allow filtering by pods
class MainPage(ListView):
    template_name = 'main_page.html'
    model = Podcast
    context_object_name = 'podcasts'

    def get_queryset(self):
        title_filter = self.request.GET.get('titlefilter', '')
        if title_filter:
            podcasts = Podcast.objects.filter(title__icontains=title_filter)
        else:
            podcasts = Podcast.objects.all()
        return podcasts.order_by('-views')

    def get_context_data(self, **kwargs):
        context = super(MainPage, self).get_context_data(**kwargs)
        context['titlefilter'] = self.request.GET.get('titlefilter', '')
        context['topics'] = Topic.objects.all().order_by('topic')
        return context

#upvote and downvote functions to update the podcasts vote total
def upvote(request, podcast_id, origin=None):
    podcast = Podcast.objects.get(id=podcast_id)
    podcast.num_upvotes += 1
    podcast.save()
    print(origin)
    if origin:
        return HttpResponseRedirect('/user/' + origin)
    else:
        return HttpResponseRedirect('/podcast')

def downvote(request, podcast_id, origin=None):
    podcast = Podcast.objects.get(id=podcast_id)
    podcast.num_upvotes -= 1
    podcast.save()
    if origin:
        return HttpResponseRedirect('/user/' + origin)
    else:
        return HttpResponseRedirect('/podcast')

# Function called on /random/ to redirect to a random podcast
def random(request):
    podcast = Podcast.objects.random()
    if podcast:
        return HttpResponseRedirect('/podcast/' + podcast.slugfield)
    else:
        return HttpResponseRedirect('/list/')


# View an individual podcast - comments, voting, playback of audio, subscriptions
class PodcastView(TemplateView):
    template_name = 'view_podcast.html'

    def get_success_url(self):
        return self.success_url

    def get_context_data(self, **kwargs):
        podcast = Podcast.objects.get(slugfield=kwargs['slugfield'])
        podcast.views += 1
        podcast.save()
        comments = Comment.objects.filter(podcast_id=podcast.id).order_by('-created')
        context = {}
        context['podcast'] = podcast
        context['comments'] = comments
        context['topics'] = Topic.objects.all().order_by('topic')
        return context

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            form = CommentForm(request.POST)
            if form.is_valid():
                podcast = Podcast.objects.get(slugfield=kwargs['slugfield'])
                podcast.num_comments += 1
                podcast.views -= 1  # ignore view count increment on redirect
                podcast.save()

                comment = form.save(commit=False)
                comment.podcast = podcast
                comment.author = self.request.user
                comment.save()
            return HttpResponseRedirect('/podcast/' + kwargs['slugfield'] + '/')


# List all users
class ListUsers(ListView):
    template_name = 'list_users.html'
    model = User
    context_object_name = 'users'

    def get_context_data(self, **kwargs):
        context = super(ListUsers, self).get_context_data(**kwargs)
        context['topics'] = Topic.objects.all().order_by('topic')
        return context


# View a specific user's uploaded podcasts
class UserView(ListView):
    template_name = 'view_user.html'
    model = Podcast
    context_object_name = 'podcasts'

    def get_success_url(self):
        return self.success_url

    def get_queryset(self):
        user = self.kwargs['username']
        user_id = User.objects.get(username=user).id
        podcasts = Podcast.objects.filter(author__id=user_id)
        return podcasts

    def get_context_data(self, **kwargs):
        context = super(UserView, self).get_context_data(**kwargs)
        context['titlefilter'] = self.request.GET.get('titlefilter', '')
        context['topics'] = Topic.objects.all().order_by('topic')
        context['username'] = self.kwargs['username']
        #check if they are subscribed
        creator = User.objects.get(username=self.kwargs['username'])
        if CreatorSubscription.objects.filter(creator=creator, user=self.request.user).exists():
            context['subscribed'] = True
        else:
            context['subscribed'] = False
        return context

def user_subscribe(request, creator_username, user_id):
    entry = CreatorSubscription(creator=User.objects.get(username=creator_username), user=User.objects.get(id=user_id))
    entry.save()
    return HttpResponseRedirect('/user/' + creator_username)

def user_unsubscribe(request, creator_username, user_id):
    CreatorSubscription.objects.filter(creator=User.objects.get(username=creator_username), user=User.objects.get(id=user_id)).delete()
    return HttpResponseRedirect('/user/' + creator_username)


# View list of podcasts from a specific pod
class TopicView(ListView):
    template_name = 'view_topic.html'
    model = Podcast
    context_object_name = 'podcasts'

    def get_queryset(self):
        topic = Topic.objects.get(topic=self.kwargs['topic'])
        podcasts = topic.podcast_set.all()
        return podcasts

    def get_context_data(self, **kwargs):
        context = super(TopicView, self).get_context_data(**kwargs)
        context['topic'] = Topic.objects.get(topic=self.kwargs['topic'])
        context['topic'].topic = context['topic'].topic.title()
        context['topics'] = Topic.objects.all().order_by('topic')
        return context


# Dashboard for users/content creators
# Main page with statistics recent subscriptions
class Dashboard(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super(Dashboard, self).get_context_data(**kwargs)
        context['topics'] = Topic.objects.all().order_by('topic')
        return context


# View a list of subscriptions and updates
class ManageSubscriptions(LoginRequiredMixin, TemplateView):
    template_name = 'manage_subscriptions.html'

    def get_context_data(self, **kwargs):
        context = super(ManageSubscriptions, self).get_context_data(**kwargs)
        context['topics'] = Topic.objects.all().order_by('topic')
        return context


# Set the user profile and other user settings
class UserSettings(LoginRequiredMixin, UpdateView):
    template_name = 'settings.html'
    model = User
    fields = ['first_name', 'last_name', 'email']
    success_url = '/dashboard/settings/'

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super(UserSettings, self).get_context_data(**kwargs)
        context['topics'] = Topic.objects.all().order_by('topic')
        return context


# Manage podcasts uploaded onto the site - delete/option to edit
class ManagePodcasts(LoginRequiredMixin, ListView):
    template_name = 'manage_podcasts.html'
    model = Podcast
    context_object_name = 'podcasts'
    slug_field = 'slugfield'
    slug_url_kwarg = 'slugfield'

    def get_queryset(self):
        context = Podcast.objects.filter(author__id=self.request.user.id)
        return context

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            slug = self.request.POST['slugfield']
            podcast = Podcast.objects.get(slugfield=slug)
            podcast.delete()
            return HttpResponseRedirect('/dashboard/manage/podcast/')

    def get_context_data(self, **kwargs):
        context = super(ManagePodcasts, self).get_context_data(**kwargs)
        context['topics'] = Topic.objects.all().order_by('topic')
        return context


# Upload a new podcast onto the site
class UploadPodcast(LoginRequiredMixin, CreateView):
    template_name = 'podcast_form.html'
    model = Podcast
    fields = ['title', 'description', 'audio_file', 'file_type']
    success_url = '/dashboard/manage/podcast/'

    def get_context_data(self, **kwargs):
        context = super(UploadPodcast, self).get_context_data(**kwargs)
        context['function'] = 'Upload'
        context['topics'] = Topic.objects.all().order_by('topic')
        return context

    def form_valid(self, form):
        topic_id = self.request.POST['topics']
        topic = Topic.objects.get(id=topic_id)
        topic.num_podcasts += 1
        topic.save()

        form.instance.topic = topic
        form.instance.author = self.request.user
        slugfield = ''.join(w for w in form.instance.title.lower(
        ).replace(' ', '_') if (w.isalnum() or w == '_'))
        form.instance.slugfield = slugfield
        return super(UploadPodcast, self).form_valid(form)

    def form_invalid(self, form):
        print(form.errors)
        return HttpResponse("invalid")


# Update an uploaded podcast - only the original creator can update
class UpdatePodcast(LoginRequiredMixin, UpdateView):
    template_name = 'podcast_form.html'
    model = Podcast
    fields = ['title', 'description']
    slug_field = 'slugfield'
    slug_url_kwarg = 'slugfield'

    def get_success_url(self):
        return self.success_url

    def get_context_data(self, **kwargs):
        context = super(UpdatePodcast, self).get_context_data(**kwargs)
        context['function'] = 'Edit'
        context['topics'] = Topic.objects.all().order_by('topic')
        return context

    def form_valid(self, form):
        slugfield = ''.join(w for w in form.instance.title.lower(
        ).replace(' ', '_') if (w.isalnum() or w == '_'))
        form.instance.updated = timezone.now()
        form.instance.slugfield = slugfield
        form.instance.views -= 1  # ignore view count increment on redirect
        self.success_url = '/podcast/' + slugfield
        return super(UpdatePodcast, self).form_valid(form)


# Manage all topics - allows for editing/deletion
class ManageTopics(ListView):
    template_name = 'manage_topics.html'
    model = Topic
    context_object_name = 'topics'

    def get_context_data(self, **kwargs):
        context = super(ManageTopics, self).get_context_data(**kwargs)
        context['topics'] = Topic.objects.all().order_by('topic')
        return context


# Create a new topic
class CreateTopic(CreateView):
    template_name = 'create_topic.html'
    model = Topic
    slug_field = 'topic'
    success_url = '/dashboard/'
    fields = ['topic', 'description']

    def get_context_data(self, **kwargs):
        context = super(CreateTopic, self).get_context_data(**kwargs)
        context['topics'] = Topic.objects.all().order_by('topic')
        return context
