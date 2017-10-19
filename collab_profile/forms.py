from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import SetPasswordForm
from django.utils.translation import ugettext as _
from markdown_ckeditor.ckeditor import CKEditorWidget
from .models import Profile

class PictureWidget(forms.widgets.FileInput):

    def render(self, name, value, attrs=None):
        if value and hasattr(value, 'url'):
            id = ''.join([attrs['id'], '_current'])
            current = '<div style="background:url(%s);" id="%s"></div><br>' % (value.url, id)
        else:
            current = ''
        field =  super(PictureWidget, self).render(name, None, attrs=attrs)
        return current + field


class ProfileForm(forms.ModelForm):

    # additional fields for changing AUTH_USER_MODEL attributes
    first_name = forms.CharField(required=False, label=_('first name'))
    last_name = forms.CharField(required=False, label=_('last name'))
    email = forms.EmailField(required=False)
    
    class Meta:
        model = Profile
        fields = ('picture', 'first_name', 'last_name', 'email', 'organization', 'link', 'description')
        widgets = {
            'picture': PictureWidget(),
            'description': CKEditorWidget(),
        }
        labels = {
            'picture': _('image'),
        }

    class Media:
        js = ("collab_profile/js/collab_profile.js",
        )


    def clean_link(self):
        link = self.cleaned_data['link']
        if link and not link.lower().startswith('http'):
            link = ''.join(['http://',link])
        return link

    def __init__(self, *args, **kwargs):
        user = kwargs['instance'].user
        initial = kwargs['initial']
        initial['first_name'] = user.first_name
        initial['last_name'] = user.last_name
        initial['email'] = user.email
        super(ProfileForm, self).__init__(*args, **kwargs)


class PasswordForm(SetPasswordForm):

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('instance')
        super(PasswordForm, self).__init__(self.user, *args, **kwargs)

