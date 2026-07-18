from django.http import HttpResponse

from pytigon_lib.schviews.viewtools import dict_to_template


from django_q.tasks import async_task
import asyncio
from django.contrib import messages


@dict_to_template("tasks_demo/v_test_task.html")
def test_task(request, **argv):
    """
    Enqueue an async test task via Django-Q and return its task ID.

    Schedules ``tasks_demo.tasks.test_task`` with parameter 123 under
    the publish ID ``test1`` and passes the task ID and demo identifier
    to the template for progress polling.
    """

    task_id_val = async_task(
        "tasks_demo.tasks.test_task", task_publish_id="test1", param=123
    )
    return {"task_id": task_id_val, "id": "demo__test1"}


@dict_to_template("tasks_demo/v_test_task2.html")
def test_task2(request, **argv):
    """
    Enqueue a second async test task via Django-Q and return its task ID.

    Schedules ``tasks_demo.tasks.test_task2`` asynchronously and returns
    the task identifier for client-side progress tracking.
    """

    task_id = async_task("tasks_demo.tasks.test_task2")
    return {"ret": task_id}


async def test_messages(request, **argv):
    """
    Demonstrate async streaming of batched Django messages.

    An async view that adds messages at multiple severity levels
    (ERROR, INFO, SUCCESS, WARNING, DEBUG) to the request with 5-second
    delays between batches, illustrating server-sent streaming updates.
    """

    response = HttpResponse("Hello, async Django!")

    message_batches = [
        (messages.ERROR, "Hello world 1"),
        (messages.INFO, "Hello world 1.1"),
        (messages.SUCCESS, "Hello world 2"),
        (messages.WARNING, "Hello world 3"),
        (messages.DEBUG, "Hello world 4"),
        (messages.INFO, "Hello world 5"),
        (messages.SUCCESS, "Hello world 6"),
    ]

    for level, text in message_batches:
        messages.add_message(request, level, text)
        request._messages.update(response)
        await asyncio.sleep(5)

    return response
