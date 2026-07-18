from pytigon_lib.schviews.viewtools import dict_to_json


import json


@dict_to_json
def form(request, **argv):
    """
    Echo received JSON POST data as a JSON response.

    Parses the request body as JSON, logs it to stdout, and returns it
    along with a greeting message and the ``f1`` field value echoed back
    into a form input element.
    """

    try:
        json_data = json.loads(request.body)
    except json.JSONDecodeError:
        json_data = {}
    print("-------------------------------------------------------")
    print(json_data)
    print("-------------------------------------------------------")
    return {
        ".result": "Hello world!<br/>" + str(json_data),
        "input.r1__value": json_data.get("f1", ""),
    }
