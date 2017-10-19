from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import ugettext as _
from django.views.generic import DetailView, UpdateView
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.edit import DeleteView
from actstream.signals import action as actstream_action
from collab.mixins import ManagerRequiredMixin
from pinax.blog.parsers.markdown_parser import parse as md_parse
from .forms import ProfileForm, PasswordForm
from .models import Profile

class GetOrCreateProfileMixin(TemplateResponseMixin):

    def dispatch(self, request, *args, **kwargs):
        pk = kwargs.pop('user_pk',None)
        if pk is not None:
            try:
                pk = int(pk)
            except ValueError:
                pk = None
        if pk == None and request.user.is_authenticated():
            return redirect(reverse('collab_profile:detail', 
                    kwargs={'user_pk':request.user.pk})
            )
        self.user = get_object_or_404(get_user_model(), pk=pk)
        self.profile = self.object = Profile.objects.get_or_create(
            user=self.user
        )[0]
        return super(GetOrCreateProfileMixin,self).dispatch(
            request, 
            *args, 
            **kwargs
        )

    def get_object(self):
        return self.profile


class Detail(GetOrCreateProfileMixin, DetailView):
    template_name = "collab_profile/detail.html"
    model = Profile
    pk_url_kwarg = "user_pk"

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            raise PermissionDenied
        context = self.get_context_data(
            object=self.object, 
        )
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(Detail, self).get_context_data(**kwargs)
        context['body_class'] = 'collab_profile'
        parsed = ''
        if self.object.description:
            parsed = md_parse(self.object.description)
        context['parsed_description'] = parsed
        return context

class Edit(GetOrCreateProfileMixin, UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = "collab_profile/edit.html"
    pk_url_kwarg = "user_pk"

    def form_valid(self, form):
        user = self.object.user
        user.first_name = form.cleaned_data['first_name']
        user.last_name = form.cleaned_data['last_name']
        user.email = form.cleaned_data['email']
        user.save()
        super(Edit, self).form_valid(form)
        messages.success(self.request, _('Profile successfully updated.'))
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse('collab_profile:detail', kwargs={'user_pk':self.object.user.pk})

class PasswordEdit(UpdateView):
    model = get_user_model()
    form_class = PasswordForm
    pk_url_kwarg = "user_pk"
    template_name = "collab_profile/edit_password.html"

    def form_valid(self, form):
        messages.success(self.request, _('Password successfully changed.'))
        return super(PasswordEdit, self).form_valid(form)
    def get_success_url(self):
        return reverse('collab_profile:detail', kwargs={'user_pk':self.object.pk})

class PromoteToManager(ManagerRequiredMixin, DeleteView):
    """
    Promote a user to manager status.
    """
    model = get_user_model()
    success_message = _("User was promoted successfully.")
    pk_url_kwarg = "user_pk"
    template_name = "collab_profile/user_confirm_manager.html"

    def get_success_url(self):
        return reverse('collab_profile:detail', kwargs={'user_pk':self.object.pk})

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.collab.is_manager = True
        self.object.collab.save()
        messages.success(request, self.success_message)
        actstream_action.send(
                sender=request.user,
                verb=_("was promoted to manager status"),
                action_object=self.object
            )
        return redirect(success_url)

    # As a side effect of using DeleteView, context['user'], which normally 
    # contains request.user, gets overwritten with self.object.
    # Let's undo that.
    def get_context_data(self, **kwargs):
        context = super(PromoteToManager, self).get_context_data(**kwargs)
        context['user'] = self.request.user
        return context