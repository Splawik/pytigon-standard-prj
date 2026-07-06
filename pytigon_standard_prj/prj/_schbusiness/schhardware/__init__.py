from django.utils.translation import gettext_lazy as _

ModuleName = "config"
ModuleTitle = _("Config")
Name = "schhardware"
Title = _("Hardware")
Perms = True
Index = ""
Urls = (
    (
        "../schelements/view_elements_of_type/I-DEV-C/-/?view_in=desktop",
        _("Computer"),
        None,
        """client://devices/computer.png""",
    ),
    (
        "../schelements/view_elements_of_type/I-DEV-P/-/?view_in=desktop",
        _("Printer"),
        "-",
        """client://devices/printer.png""",
    ),
    (
        "../schelements/view_elements_of_type/I-DEV-H/-/?view_in=desktop",
        _("Phone"),
        None,
        """client://devices/audio-input-microphone.png""",
    ),
    (
        "../schelements/view_elements_of_type/I-DEV-O/-/?view_in=desktop",
        _("Other device"),
        None,
        """client://categories/applications-system.png""",
    ),
    (
        "../schelements/view_elements_of_type/I-DEV-M/-/?view_in=desktop",
        _("Monitor"),
        None,
        """client://devices/video-display.png""",
    ),
)
UserParam = {}
