from django.conf import settings

def in_frame(request):
    if hasattr(settings, "IN_FRAME"):
        return {"IN_FRAME": settings.IN_FRAME}
    else:
        return {"IN_FRAME": False}
