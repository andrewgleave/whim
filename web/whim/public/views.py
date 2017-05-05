from django.shortcuts import render, get_object_or_404
from whim.core.models import Event


def index(request):
    return render(request, 'index.html', {'events': Event.objects.today()})


def event_detail(request, event_slug):
    event = get_object_or_404(Event, slug=event_slug)
    return render(request, 'event_detail.html', {'event': event})
