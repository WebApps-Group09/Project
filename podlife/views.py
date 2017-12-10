from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse
from django.utils import timezone
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView

from podlife.forms import CommentForm
from podlife.models import Comment, Podcast, Topic, CreatorSubscription, TopicSubscription
from itertools import chain


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
        # filter based off of search bar
        title_filter = self.request.GET.get('titlefilter', '')
        if title_filter:
            podcasts = Podcast.objects.filter(title__icontains=title_filter)
        else:
            podcasts = Podcast.objects.all()

        # filter based off of sorttype
        if self.request.GET.get('sorttype') == None:
            return podcasts
        elif self.request.GET.get('sorttype') == 'title':
            return podcasts.order_by('title')
        elif self.request.GET.get('sorttype') == 'views':
            return podcasts.order_by('-views')
        elif self.request.GET.get('sorttype') == 'upvotes':
            return podcasts.order_by('-num_upvotes')
        elif self.request.GET.get('sorttype') == 'new':
            return podcasts.order_by('-created')
        return podcasts

    def get_context_data(self, **kwargs):
        context = super(MainPage, self).get_context_data(**kwargs)
        context['titlefilter'] = self.request.GET.get('titlefilter', '')
        context['topics'] = Topic.objects.all().order_by('topic')
        return context


# Upvote function to update the podcasts vote total
def upvote(request, podcast_id, origin=None):
    podcast = Podcast.objects.get(id=podcast_id)
    podcast.num_upvotes += 1
    podcast.save()
    print(origin)
    if origin:
        return HttpResponseRedirect('/user/' + origin)
    else:
        return HttpResponseRedirect('/podcast')

#downvote function to update the podcasts vote total
def downvote(request, podcast_id, origin=None):
    podcast = Podcast.objects.get(id=podcast_id)
    podcast.num_upvotes -= 1
    podcast.save()
    if origin: #if the origin is set, it is coming from the user page and needs to be sent back there
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
        comments = Comment.objects.filter(
            podcast_id=podcast.id).order_by('-created')
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
        # check if it's themselves
        if (str(self.request.user) == self.kwargs['username']):
            context['is_self'] = True
        else:
            context['is_self'] = False
        # check if they are subscribed
        creator = User.objects.get(username=self.kwargs['username'])
        if CreatorSubscription.objects.filter(creator=creator, user=self.request.user).exists():
            context['subscribed'] = True
        else:
            context['subscribed'] = False

        user_id = User.objects.get(username=self.kwargs['username']).id
        context['usersubs'] = CreatorSubscription.objects.filter(user=user_id)
        context['topicsubs'] = TopicSubscription.objects.filter(user=user_id)
        return context

#subscribes a user to another user
def user_subscribe(request, creator_username, user_id):
    entry = CreatorSubscription(creator=User.objects.get(
        username=creator_username), user=User.objects.get(id=user_id))
    entry.save()
    return HttpResponseRedirect('/user/' + creator_username)

#unsubscribes a user from a user
def user_unsubscribe(request, creator_username, user_id):
    CreatorSubscription.objects.filter(creator=User.objects.get(
        username=creator_username), user=User.objects.get(id=user_id)).delete()
    return HttpResponseRedirect('/user/' + creator_username)

#unsubscribes a user from another user from the dashboard page
def dashboard_user_unsubscribe(request, creator_username, user_id):
    CreatorSubscription.objects.filter(creator=User.objects.get(
        username=creator_username), user=User.objects.get(id=user_id)).delete()
    return HttpResponseRedirect('/dashboard/manage/subs')

#unsubscrbies a user from a topic from the dashboard page
def dashboard_topic_unsubscribe(request, topic, user_id):
    TopicSubscription.objects.filter(pod=Topic.objects.get(
        topic=topic.lower()), user=User.objects.get(id=user_id)).delete()
    #updates the number of subscribers a topic has
    topic_to_update = Topic.objects.get(topic=topic.lower())
    topic_to_update.num_subscribers -= 1
    topic_to_update.save()
    return HttpResponseRedirect('/dashboard/manage/subs')

#subscribes a user to a topic
def topic_subscribe(request, topic, user_id):
    # create the subscription in the table
    entry = TopicSubscription(pod=Topic.objects.get(
        topic=topic.lower()), user=User.objects.get(id=user_id))
    entry.save()

    # update topic number of subs
    topic_to_update = Topic.objects.get(topic=topic.lower())
    topic_to_update.num_subscribers += 1
    topic_to_update.save()

    return HttpResponseRedirect('/topic/' + topic.lower())

#unsubscribes a user from a topic
def topic_unsubscribe(request, topic, user_id):
    # delete the sub in the table
    TopicSubscription.objects.filter(pod=Topic.objects.get(
        topic=topic.lower()), user=User.objects.get(id=user_id)).delete()

    # decrement number of subscribers
    topic_to_update = Topic.objects.get(topic=topic.lower())
    topic_to_update.num_subscribers -= 1
    topic_to_update.save()

    return HttpResponseRedirect('/topic/' + topic.lower())


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
        # checking if the topic is already subscribed
        if TopicSubscription.objects.filter(pod=context['topic'], user=self.request.user).exists():
            context['subscribed'] = True
        else:
            context['subscribed'] = False
        context['topic'].topic = context['topic'].topic.title()
        context['topics'] = Topic.objects.all().order_by('topic')
        return context


# Dashboard for users/content creators
# Main page with statistics recent subscriptions
class Dashboard(LoginRequiredMixin, ListView):
    template_name = 'dashboard.html'
    context_object_name = 'updates'

    def get_queryset(self):
        curr_user = User.objects.get(username=self.request.user)
        usersubs = CreatorSubscription.objects.values_list('creator', flat=True).filter(user=curr_user)
        topicsubs = TopicSubscription.objects.values_list('pod', flat=True).filter(user=curr_user)
        if usersubs or topicsubs:
            # initial query
            sql = 'SELECT * FROM podlife_podcast WHERE'
            # add user subs
            if usersubs:
                sql += ' author_id=%s' % usersubs[0]
                for sub in usersubs[1:]:
                    sql += ' OR author_id=%s' % sub
            # add topic subs
            if topicsubs:
                if usersubs:  # build off the previously constructed query string
                    sql += ' OR'
                sql += ' topic_id=%s' % topicsubs[0]
                for sub in topicsubs[1:]:
                    sql += ' OR topic_id=%s' % sub
            # order by the most recently updated, then alphabetically by title
            sql += ' ORDER BY updated DESC, title ASC'
            # print(sql)
            return Podcast.objects.raw(sql)
        return []  # no subscriptions

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

        curr_user = User.objects.get(username=self.request.user)
        context['usersubs'] = CreatorSubscription.objects.filter(user=curr_user)
        context['topicsubs'] = TopicSubscription.objects.filter(user=curr_user)
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
