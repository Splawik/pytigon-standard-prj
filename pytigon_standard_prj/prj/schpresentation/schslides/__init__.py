from django.utils.translation import gettext_lazy as _

ModuleName = "main"
ModuleTitle = _("main")
Name = "schslides"
Title = _("Slides")
Perms = True
Index = ""
Urls = (
    (
        "table/Show/-/form/list/?view_in=desktop",
        _("Slideshow"),
        None,
        """png://mimetypes/x-office-presentation-template.png""",
    ),
)
UserParam = {}
