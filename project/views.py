from django.views.generic import CreateView
from django.contrib.auth.models import User

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