from django.http import HttpResponse


from . import models


from wsgiref.util import FileWrapper
import mimetypes


def download(request, pk):

    obj = models.Attachment.objects.get(id=pk)
    wrapper = FileWrapper(obj.file.open("rb"))
    content_type = mimetypes.guess_type(obj.file.name)[0]
    response = HttpResponse(wrapper, content_type=content_type)
    response["Content-Length"] = obj.file.size
    response["Content-Disposition"] = "attachment; filename=%s" % obj.file.name
    return response
