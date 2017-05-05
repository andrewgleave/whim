from django.conf.urls import url
from django.views.generic import TemplateView

from whim.public import views

urlpatterns = [
    # Dashboard
    url(r'^$', views.index, name='public_index'),
    url(
        r'^event/(?P<event_slug>[\w-]+)/$',
        views.event_detail,
        name='public_event_detail'),
]
