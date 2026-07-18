from pytigon_lib.schtasks.publish import publish


from pytigon_lib.schfs.tasks import filesystemcmd


@publish("vfs_action")
def vfs_action(cproxy=None, **kwargs):

    return filesystemcmd(cproxy, **kwargs)
