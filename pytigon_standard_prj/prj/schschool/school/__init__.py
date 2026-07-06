from django.utils.translation import gettext_lazy as _

ModuleName = "school"
ModuleTitle = _("School")
Name = "school"
Title = _("School")
Perms = True
Index = ""
Urls = (
    (
        "../schelements/view_elements_as_tree/-/O-COM/school__school/?view_in=desktop",
        _("Schools"),
        "school.list_schools",
        """fa://building-o.png""",
    ),
    (
        "../schelements/view_elements_as_tree/SCHOOL1-C/-/school__class/?view_in=desktop",
        _("Klasy"),
        None,
        """fa://group.png""",
    ),
    (
        "../schelements/table/Element/0/form/tree/?view_in=desktop",
        _("Structure"),
        None,
        """png://places/folder.png""",
    ),
    (
        "../schelements/view_elements/N/-/-/?view_in=desktop",
        _("Nauczyciele"),
        None,
        """png://emotes/face-smile.png""",
    ),
    (
        "table/SubjectType/-/form/list/?view_in=desktop",
        _("Typy przedmiotów"),
        None,
        """fa://app.png""",
    ),
    (
        "table/Subject/-/form/list/?view_in=desktop",
        _("Przedmioty"),
        None,
        """fa://app.png""",
    ),
    (
        "../schelements/table/DocHead/Lesson/form/docheadlist/?view_in=desktop",
        _("Lekcje"),
        None,
        """fa://list-alt.png""",
    ),
    (
        "email?view_in=desktop",
        _("email"),
        None,
        """png://actions/mail-reply-sender.png""",
    ),
    (
        "../schelements/table/DocHead/Lesson/form/docheadlist/?version=school__calendar&view_in=desktop",
        _("Lesson calendar - for admin"),
        None,
        """""",
    ),
    (
        "../schelements/table/DocHead/Lesson/school__calendar2/docheadlist/?version=school_calendar2&view_in=desktop",
        _("Lesson calendar - for student"),
        None,
        """""",
    ),
    (
        "../schelements/table/DocHead/Lesson/school__calendar3/docheadlist/?version=school__calendar3&view_in=desktop",
        _("Lesson calendar - for teacher"),
        None,
        """""",
    ),
    ("statistic_for_user/?view_in=desktop", _("statistic for user"), None, """"""),
    (
        "statistic_for_teacher/?view_in=desktop",
        _("statistic for teacher"),
        None,
        """""",
    ),
    ("../schelements/view_elements_as_tree/DEVICES/-/-/", _("Devices"), None, """"""),
    (
        "../schelements/view_elements_as_tree/-/0/school__all_devices/",
        _("All devices"),
        None,
        """png://actions/document-print.png""",
    ),
    (
        "../schelements/view_elements/CUSTOMERS/-/school__customers/",
        _("Customers"),
        None,
        """png://emotes/face-monkey.png""",
    ),
    (
        "table/Customer/-/form/list/",
        _("Consumers 2"),
        None,
        """png://emotes/face-devilish.png""",
    ),
)
UserParam = {}
