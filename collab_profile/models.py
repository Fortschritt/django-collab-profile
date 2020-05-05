import time
from django.conf import settings
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.db import models
from django.utils.translation import ugettext_lazy as _
from private_media.storages import PrivateMediaStorage

def file_upload_path(instance, filename):
    time_string = time.strftime('%Y/%m/%d')
    return 'collab_profile/%s/%s' % (time_string, filename)

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    picture = models.FileField(upload_to=file_upload_path, storage=PrivateMediaStorage(), null=True, blank=True)
    organization = models.CharField(max_length=256, blank=True, default='')
    link = models.CharField(max_length=256, blank=True, default='')
    description = models.TextField(blank=True, default='', verbose_name=_("self description"))

    @property
    def avatar(self):
        if self.picture:
            return self.picture.url
        else:
            return static('img/default_avatar.png')