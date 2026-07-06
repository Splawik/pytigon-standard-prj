from django.utils.translation import gettext_lazy as _

ModuleName = "shop"
ModuleTitle = _("Shop")
Name = "shop"
Title = _("Shop")
Perms = True
Index = ""
Urls = (
    ("test/", _("test"), None, """png://actions/folder-new.png"""),
    (
        "../pl/account/",
        _("Your account"),
        None,
        """png://apps/preferences-system-session.png""",
    ),
    ("../pl/checkout/", _("Your basket"), None, """fa://shopping-cart.png"""),
)
UserParam = {}
