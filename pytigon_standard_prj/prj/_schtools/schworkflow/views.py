from pytigon_lib.schviews import actions


from . import models


def accept(request, pk):

    obj = models.WorkflowItem.objects.get(pk=pk)
    obj.accept_workflow_item()
    return actions.refresh(request)


def reject(request, pk):

    obj = models.WorkflowItem.objects.get(pk=pk)
    obj.reject_workflow_item()
    return actions.refresh(request)
