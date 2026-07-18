import time
from pytigon_lib.schtasks.publish import publish


@publish("test")
def test(cproxy=None, **kwargs):

    if cproxy:
        cproxy.send_event(
            "<ul class='data'></ul><div name='task_end_info' style='display: none;'>Finish</div>"
        )
    for i in range(30):
        if cproxy:
            cproxy.send_event(f"<li>item {i}</li> ===>> .data")
        time.sleep(1)
    return "Hello world"
