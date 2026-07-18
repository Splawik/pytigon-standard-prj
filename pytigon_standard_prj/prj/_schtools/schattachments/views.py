from django.http import HttpResponse


from . import models
import os


from wsgiref.util import FileWrapper
import mimetypes


def download(request, pk):

    obj = models.Attachment.objects.get(id=pk)
    wrapper = FileWrapper(open(obj.file.path, "rb"))
    content_type = mimetypes.guess_type(obj.file.path)[0]
    response = HttpResponse(wrapper, content_type=content_type)
    response["Content-Length"] = os.path.getsize(obj.file.path)
    response["Content-Disposition"] = "attachment; filename=%s" % obj.file.name
    return response
