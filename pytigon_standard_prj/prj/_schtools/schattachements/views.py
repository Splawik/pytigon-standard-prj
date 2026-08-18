import mimetypes
import os
from wsgiref.util import FileWrapper

from django.http import HttpResponse

from . import models


def download(request, pk):

    obj = models.Attachement.objects.get(id=pk)
    wrapper = FileWrapper(open(obj.file.path, "rb"))
    content_type = mimetypes.guess_type(obj.file.path)[0]
    response = HttpResponse(wrapper, content_type=content_type)
    response["Content-Length"] = os.path.getsize(obj.file.path)
    response["Content-Disposition"] = "attachment; filename=%s" % obj.file.name
    return response
