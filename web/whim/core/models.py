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


class CategoryManager(models.Manager):
    '''
    Manager methods for Category model
    '''

    def get_or_create_from_name(self, name):
        return self.get_or_create(name=name.lower())


class Category(BaseModel):
    '''
    Category model
    '''

    name = models.CharField(blank=False, max_length=75)

    objects = CategoryManager()

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


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

    def pending(self):
        return self.filter(status=Event.STATUS_PENDING)

    def published(self):
        return self.filter(status=Event.STATUS_PUBLISHED)

    def pending_or_published(self):
        return self.filter(status__in=(Event.STATUS_PENDING,
                                       Event.STATUS_PUBLISHED, ))

    def forthcoming(self):
        tomorrow = datetime.now().date() + timedelta(1)
        tomorrow_start = datetime.combine(tomorrow, time())
        return self.published().filter(start_datetime__gte=tomorrow_start)

    def today(self):
        today = datetime.now().date()
        tomorrow = today + timedelta(1)
        today_start = datetime.combine(today, time())
        today_end = datetime.combine(tomorrow, time())
        return self.published().filter(
            start_datetime__lte=today_end, end_datetime__gte=today_start)

    def exists_for_source_name(self, source, name):
        return self.pending_or_published().exists(
            source=source, name__iexact=name)


class Event(BaseModel):
    '''
    Event model
    '''

    STATUS_PENDING = 0
    STATUS_PUBLISHED = 1
    STATUS_REMOVED = 2
    STATUS_NEEDS_REVIEW = 3

    STATUS_CHOICES = ((STATUS_PENDING, 'Pending'), (
        STATUS_PUBLISHED, 'Published'), (STATUS_REMOVED, 'Removed'),
                      (STATUS_NEEDS_REVIEW, 'Needs Review'), )

    source = models.ForeignKey(Source, related_name="events")
    category = models.ForeignKey(Category, related_name="events")
    name = models.CharField(blank=False, max_length=75)
    slug = models.SlugField(max_length=75)
    description = models.TextField(blank=False)
    start_datetime = models.DateTimeField(blank=False)
    end_datetime = models.DateTimeField(blank=True, null=True)
    link = models.URLField(blank=True)
    tags = ArrayField(models.CharField(max_length=50), blank=True)
    status = models.PositiveIntegerField(
        choices=STATUS_CHOICES, default=STATUS_PENDING)

    objects = EventManager()

    class Meta:
        ordering = ['-start_datetime']

    def __str__(self):
        return '{} ({}) - {}'.format(
            self.name, self.category,
            self.start_datetime.strftime("%d/%m/%y %H:%M"))

    def get_absolute_url(self):
        return reverse('public_event_detail', args=[self.slug])


#Signals
@receiver(models.signals.pre_save, sender=Event)
def create_user_profile(sender, instance=None, **kwargs):
    if not instance.id:
        instance.slug = Event.objects.create_slug(instance.name)
        instance.status = Event.STATUS_PENDING
