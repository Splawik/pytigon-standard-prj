from pytigon_lib.schviews.viewtools import dict_to_json


from . import models


from pytigon_lib.schtools.schjson import json_loads


from pytigon_lib.schdjangoext.import_from_db import run_code_from_db_field


@dict_to_json
def plot_service(request, **argv):

    request_param = {"argv": argv}
    request_param["GET"] = request.GET
    if "param" in request.GET:
        request_param["param"] = request.GET["param"]
    else:
        request_param["param"] = None

    param = json_loads(request.body.decode("utf-8"))

    request_param["body"] = param

    action = param["action"]
    name = param["name"]

    objs = models.Plot.objects.filter(name=name)
    if len(objs) == 1:
        obj = objs[0]
    else:
        obj = None

    if obj:
        if action == "get_config":
            if obj.get_config:
                config = run_code_from_db_field(
                    f"plot__get_config{obj.pk}.py",
                    obj,
                    "get_config",
                    "get_config",
                    obj=obj,
                    request_param=request_param,
                )
            else:
                config = {
                    "displayModeBar": False,
                    "showLink": False,
                    "displaylogo": False,
                    "scrollZoom": True,
                    "modeBarButtonsToRemove": ["sendDataToCloud"],
                }
            return config
        elif action == "get_data":
            if obj.get_data:
                data = run_code_from_db_field(
                    f"plot__get_data{obj.pk}.py",
                    obj,
                    "get_data",
                    "get_data",
                    obj=obj,
                    request_param=request_param,
                )
            else:
                data = {}
            return data
        elif action == "get_layout":
            if obj.get_layout:
                layout = run_code_from_db_field(
                    f"plot__get_layout{obj.pk}.py",
                    obj,
                    "get_layout",
                    "get_layout",
                    obj=obj,
                    request_param=request_param,
                )
            else:
                layout = {}
            return layout
        elif action == "on_event":
            if obj.on_event:
                ret = run_code_from_db_field(
                    f"plot__on_event{obj.pk}.py",
                    obj,
                    "on_event",
                    "on_event",
                    obj=obj,
                    data=param,
                    request_param=request_param,
                )
                return ret
            else:
                return {}
        else:
            return {"error": "Action not found"}

    return {"error": "Plot object not found"}
