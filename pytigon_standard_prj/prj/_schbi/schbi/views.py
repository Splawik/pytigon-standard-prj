from django.http import HttpResponse
from django.template import Template
from django.template import RequestContext


from . import models


import json
from django.http import Http404
from django.http import JsonResponse
from pytigon_lib.schdjangoext.fastform import form_from_str
from pytigon_lib.schdjangoext.django_ihtml import ihtml_to_html
from pytigon_lib.schdjangoext.import_from_db import run_code_from_db_field, ModuleStruct


models.refresh_data("begin")


def project_view(request, prj_name):

    try:
        prj = models.Project.objects.get(name=prj_name)
    except:
        raise Http404

    models.refresh_data("before")

    session_key = "bi_" + prj_name
    if session_key not in request.session:
        request.session[session_key] = {}

    if prj.form:
        form_class = form_from_str(prj.form, init_data={"prj": prj, "models": models})
        if request.method == "POST":
            json_data = json.loads(request.body)
            modified = False
            for key, value in json_data.items():
                if key in ("name", "new_value"):
                    continue
                key2 = prj_name + "/" + key
                if not (
                    key2 in request.session[session_key]
                    and request.session[session_key][key2] == value
                ):
                    request.session[session_key][key2] = value
                    modified = True
            request.session.modified = modified
            return JsonResponse({"send_event": {"refresh_bi_project": prj.name}})
        else:
            data = {}
            for key, value in request.session[session_key].items():
                if key.startswith(prj_name + "/"):
                    key = key.split("/")[-1]
                    data[key] = value
            form = form_class(initial=data)
    else:
        form = None

    if prj.template:
        t = Template(ihtml_to_html(None, prj.template))
    else:
        template = '% extends "schbi/base_project.html"\n'
        t = Template(ihtml_to_html(None, template))

    data = {}
    if prj.view:
        data = run_code_from_db_field(
            f"bi_prj_{prj.name}_view.py",
            prj,
            "view",
            "view",
            request=request,
            module=ModuleStruct(globals(), locals()),
            prj=prj,
        )

    c = RequestContext(
        request,
        {"form": form, "bi_prj": prj, "data": data | request.session[session_key]},
    )
    return HttpResponse(t.render(c))


def page_view(request, page_id):

    try:
        page = models.Page.objects.get(pk=page_id)
    except:
        raise Http404

    models.refresh_data("before")

    session_key = "bi_" + page.parent.name
    if session_key not in request.session:
        request.session[session_key] = {}

    if page.form:
        form_class = form_from_str(page.form)

        if request.method == "POST":
            json_data = json.loads(request.body)
            modified = False
            for key, value in json_data.items():
                if key in ("name", "new_value"):
                    continue
                key2 = page.name + "/" + page.parent.name + "/" + key
                if not (
                    key2 in request.session[session_key]
                    and request.session[session_key][key2] == value
                ):
                    request.session[session_key][key2] = value
                    modified = True
            request.session.modified = modified
            return JsonResponse({"send_event": {"refresh_bi_page": page.name}})
        else:
            data = {}
            for key, value in request.session[session_key].items():
                if key.startswith(page.name + "/" + page.parent.name + "/"):
                    key = key.split("/")[-1]
                    data[key] = value
            form = form_class(initial=data)
    else:
        form = None

    if page.template:
        t = Template(ihtml_to_html(None, page.template))
    else:
        template = '% extends "schbi/base_page.html"\n'
        t = Template(ihtml_to_html(None, template))

    data = {}
    if page.view:
        data = run_code_from_db_field(
            f"bi_prj_{page.parent.name}_page_{page.name}_view.py",
            page,
            "view",
            "view",
            request=request,
            module=ModuleStruct(globals(), locals()),
            page=page,
        )

    c = RequestContext(
        request,
        {"form": form, "page": page, "data": data | request.session[session_key]},
    )
    return HttpResponse(t.render(c))


def chart_view(request, chart_id):

    try:
        chart = models.Chart.objects.get(pk=chart_id)
    except:
        raise Http404

    models.refresh_data("before")

    session_key = "bi_" + chart.parent.parent.name
    if session_key not in request.session:
        request.session[session_key] = {}

    if chart.form:
        form_class = form_from_str(chart.form)

        if request.method == "POST":
            json_data = json.loads(request.body)
            modified = False
            for key, value in json_data.items():
                if key in ("name", "new_value"):
                    continue
                key2 = (
                    chart.name
                    + "/"
                    + chart.parent.name
                    + "/"
                    + chart.parent.parent.name
                    + "/"
                    + key
                )
                if not (
                    key2 in request.session[session_key]
                    and request.session[session_key][key2] == value
                ):
                    request.session[session_key][key2] = value
                    modified = True
            request.session.modified = modified
            return JsonResponse({"send_event": {"refresh_bi_chart": chart.name}})
        else:
            data = {}
            for key, value in request.session[session_key].items():
                if key.startswith(
                    chart.name
                    + "/"
                    + chart.parent.name
                    + "/"
                    + chart.parent.parent.name
                    + "/"
                ):
                    key = key.split("/")[-1]
                    data[key] = value
            form = form_class(initial=data)
    else:
        form = None

    if chart.template:
        t = Template(ihtml_to_html(None, chart.template))
    else:
        template = '% extends "schbi/base_chart.html"\n'
        t = Template(ihtml_to_html(None, template))

    data = {}
    if chart.view:
        data = run_code_from_db_field(
            f"bi_prj_{chart.parent.parent.name}_chart_{chart.name}_view.py",
            chart,
            "view",
            "view",
            request=request,
            module=ModuleStruct(globals(), locals()),
            chart=chart,
        )
    c = RequestContext(
        request,
        {"form": form, "chart": chart, "data": data | request.session[session_key]},
    )
    return HttpResponse(t.render(c))
