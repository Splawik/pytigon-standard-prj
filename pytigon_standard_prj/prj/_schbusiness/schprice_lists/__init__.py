from django.utils.translation import gettext_lazy as _

ModuleName = "config"
ModuleTitle = _("Config")
Name = "schprice_lists"
Title = _("Prace lists")
Perms = True
Index = ""
Urls = (
    ("table/RetailPrice/-/form/list/", _("Retail prices"), None, """fa://bank.png"""),
    ("table/Price/-/form/list/", _("Prices"), None, """fa://bank.png"""),
)
UserParam = {}
