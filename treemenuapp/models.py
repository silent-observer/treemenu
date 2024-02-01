from django.urls import reverse
from django.utils.translation import gettext as _
from django.db import models

class MenuNode(models.Model):

    name = models.CharField(_("Name"), max_length=255)
    named_url = models.CharField(_("Named URL"), max_length=200, blank=True, null=True)
    url = models.CharField(_("Direct URL"), max_length=200, blank=True, null=True)
    parent = models.ForeignKey("self", verbose_name=_("Parent"), on_delete=models.CASCADE, null=True, blank=True, related_name="children")
    priority = models.IntegerField(_("Priority"), default=0)
    menu = models.ForeignKey("Menu", verbose_name=_("Menu"), on_delete=models.CASCADE, related_name="nodes")

    class Meta:
        verbose_name = _("menu node")
        verbose_name_plural = _("menu nodes")

    def get_url(self):
        """
        Gets the direct URL for the node.
        Named URL take priority over direct ones.
        Arguments for the named URLs can be specified delimeted by a space.
        """
        if self.named_url:
            parts = self.named_url.split(' ')
            if len(parts) > 1:
                url = reverse(parts[0], args=parts[1:])
            else:
                url = reverse(parts[0])
        elif self.url:
            url = self.url
        else:
            url = '/'
        
        if url is None:
            return '/'
        else:
            return url

    def __str__(self):
        return self.name

class Menu(models.Model):
    slug = models.SlugField(_("Slug"), max_length=255, unique=True, db_index=True)

    class Meta:
        verbose_name = _("menu")
        verbose_name_plural = _("menus")

    def __str__(self):
        return self.slug
