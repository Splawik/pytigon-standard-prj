from django.utils.translation import gettext_lazy as _

ModuleName = "config"
ModuleTitle = _("Config")
Name = "schattachments"
Title = _("Attachments")
Perms = True
Index = ""
Urls = (
    (
        "table/Attachment/-/form/list/?view_in=desktop",
        _("Attachments"),
        "schattachments.admin_attachment",
        """client://status/mail-attachment.png""",
    ),
)
UserParam = {}
