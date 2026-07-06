from django.utils.translation import gettext_lazy as _

ModuleName = "epg"
ModuleTitle = _("epg")
Name = "epg"
Title = _("EPG")
Perms = True
Index = ""
Urls = (
    (
        "table/Epg/-/form/list/?view_in=desktop",
        _("EPG"),
        None,
        """png://mimetypes/image-x-generic.png""",
    ),
    (
        "table/BlockEpg/-/form/list/?view_in=desktop",
        _("Blocked elements"),
        None,
        """ART_ERROR""",
    ),
)
UserParam = {}
