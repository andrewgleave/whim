from django.shortcuts import _get_queryset


def get_object_or_none(klass, *args, **kwargs):
    '''
    A clone of get_object_or_404 which instead of
    throwing a 404 on not finding the object returns None
    '''

    queryset = _get_queryset(klass)
    try:
        return queryset.get(*args, **kwargs)
    except queryset.model.DoesNotExist:
        return None