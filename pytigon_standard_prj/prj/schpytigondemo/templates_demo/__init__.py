from django.utils.translation import gettext_lazy as _

ModuleName = "templates"
ModuleTitle = _("templates")
Name = "templates_demo"
Title = _("Templates")
Perms = False
Index = ""
Urls = (
    (
        "example_template/",
        _("Example template"),
        None,
        """png://mimetypes/x-office-presentation.png""",
    ),
    (
        "excel/",
        _("Excel template"),
        None,
        """png://mimetypes/x-office-spreadsheet.png""",
    ),
    ("odf/", _("odf template"), None, """png://mimetypes/x-office-spreadsheet.png"""),
    (
        "target/",
        _("Using the target"),
        None,
        """png://actions/media-playback-stop.png""",
    ),
    ("region/", _("Using the region"), None, """png://places/start-here.png"""),
    ("min/", _("Minimal page example"), None, """png://actions/window-new.png"""),
    (
        "details/",
        _("Details window"),
        None,
        """png://apps/preferences-system-windows.png""",
    ),
)
UserParam = {}
