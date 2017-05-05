from datetime import datetime, time, timedelta

from django.db import models
from django.dispatch import receiver
from django.contrib.postgres.fields import ArrayField
from django.utils.text import slugify
from django.urls import reverse


class BaseModel(models.Model):
    '''
    Custom model base class providing creation/mod timestamps
    '''

    creation_date = models.DateTimeField(auto_now_add=True)
    last_modified_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Source(BaseModel):
    '''
    Source model
    '''

    name = models.CharField(blank=False, max_length=75)
    scraper_name = models.CharField(blank=False, max_length=75)
    last_run_date = models.DateTimeField(blank=True, null=True)
    active = models.BooleanField(default=False)

    def __str__(self):
        return '{} - {}'.format(self.name, self.scraper_name)


class EventManager(models.Manager):
    '''
    Manager methods for Event model
    '''

    def create_slug(self, name):
        slug = slugify(name)
        count = 1
        while self.filter(slug=slug).exists():
            count += 1
            slug = '{}_{:d}'.format(slug, count)
        return slug

    def forthcoming(self):
        tomorrow = datetime.now().date() + timedelta(1)
        tomorrow_start = datetime.combine(tomorrow, time())
        return self.filter(start_datetime__gte=tomorrow_start)

    def today(self):
        today = datetime.now().date()
        tomorrow = today + timedelta(1)
        today_start = datetime.combine(today, time())
        today_end = datetime.combine(tomorrow, time())
        return self.filter(
            start_datetime__lte=today_end, end_datetime__gte=today_start)


class Event(BaseModel):
    '''
    Event model
    '''

    source = models.ForeignKey(Source, related_name="events")
    name = models.CharField(blank=False, max_length=75)
    slug = models.SlugField(max_length=75)
    description = models.TextField(blank=False)
    start_datetime = models.DateTimeField(blank=False)
    end_datetime = models.DateTimeField(blank=True, null=True)
    link = models.URLField(blank=True)
    tags = ArrayField(models.CharField(max_length=50), blank=True)

    objects = EventManager()

    class Meta:
        ordering = ['-start_datetime']

    def __str__(self):
        return '{} - {}'.format(self.name,
                                self.start_datetime.strftime("%d/%m/%y %H:%M"))

    def get_absolute_url(self):
        return reverse('public_event_detail', args=[self.slug])


#Signals
@receiver(models.signals.pre_save, sender=Event)
def create_user_profile(sender, instance=None, **kwargs):
    instance.slug = Event.objects.create_slug(instance.name)