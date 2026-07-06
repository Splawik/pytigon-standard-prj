from django.utils.translation import gettext_lazy as _

ModuleName = "config"
ModuleTitle = _("Config")
Name = "schmasterdata"
Title = _("Master data")
Perms = True
Index = ""
Urls = (
    (
        "../schelements/view_elements_of_type/O-COM/-/",
        _("Companies"),
        None,
        """fa://institution.png""",
    ),
    (
        "../schelements/view_elements_of_type/O-CUS/-/",
        _("Customers"),
        None,
        """png://emotes/face-smile.png""",
    ),
    (
        "../schelements/view_elements_of_type/O-SUP/-/",
        _("Suppliers"),
        None,
        """png://emotes/face-devilish.png""",
    ),
    (
        "../schelements/view_elements_of_type/I-PRD/-/",
        _("Products"),
        None,
        """png://mimetypes/application-x-executable.png""",
    ),
    (
        "../schelements/view_elements_of_type/I-MER/-/",
        _("Merchandises"),
        None,
        """png://actions/edit-redo.png""",
    ),
    (
        "../schelements/view_elements_of_type/I-UNT/-/",
        _("Standard units of measure"),
        None,
        """png://actions/format-indent-more.png""",
    ),
    (
        "../schelements/view_elements_of_type/O-EMP/-/",
        _("Employes"),
        None,
        """png://categories/applications-development.png""",
    ),
    (
        "../schelements/view_elements_of_type/O-PER/-/",
        _("Persons"),
        None,
        """png://apps/system-users.png""",
    ),
    (
        "../schelements/view_elements_of_type/O-LOC/-/",
        _("Locations"),
        None,
        """png://apps/preferences-system-session.png""",
    ),
)
UserParam = {}
