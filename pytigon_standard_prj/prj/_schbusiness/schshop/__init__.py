from django.utils.translation import gettext_lazy as _

ModuleName = "config"
ModuleTitle = _("Config")
Name = "schshop"
Title = _("Shop")
Perms = True
Index = ""
Urls = (
    ("table/ShopGood/-/form__shopping/list/", _("Shopping"), None, """fa://usd.png"""),
    (
        "table/ShoppingCart/-/form/list/",
        _("Shopping cart"),
        None,
        """fa://shopping-cart.png""",
    ),
    (
        "table/ShopGood/-/form/list/",
        _("Shop goods"),
        None,
        """png://status/folder-open.png""",
    ),
)
UserParam = {}
