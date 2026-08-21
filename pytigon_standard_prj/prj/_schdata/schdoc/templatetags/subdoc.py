from django import template
from django.template.loader import get_template
from pytigon_lib.schdjangoext.tools import make_href

register = template.Library()


def inclusion_tag(file_name):
    def dec(func):
        def func2(context, *argi, **argv):
            ret = func(context, *argi, **argv)
            t = get_template(file_name)
            return t.render(ret, context.request)

        return register.simple_tag(
            takes_context=True, name=getattr(func, "_decorated_function", func).__name__
        )(func2)

    return dec


@inclusion_tag("schdoc/subdoc.html")
def subdoc(context, name, type):
    doc = context["doc"]
    doc_def = context["doc_def"]
    url = make_href("/schdoc/edit_subdoc/%d/%s/%s/" % (doc.id, name, type))
    return {"href": url}


@inclusion_tag("schdoc/check.html")
def check(context, is_checked, title=""):
    return {"is_checked": is_checked, "title": title}
