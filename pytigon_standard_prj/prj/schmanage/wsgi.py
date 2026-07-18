import os
import sys

_lp = os.path.dirname(os.path.abspath(__file__))

if "PYTIGON_ROOT_PATH" in os.environ:
    _rp = os.environ["PYTIGON_ROOT_PATH"]
else:
    _rp = os.path.abspath(os.path.join(_lp, "..", "..", ".."))

if _lp not in sys.path:
    sys.path.insert(0, _lp)
if _rp not in sys.path:
    sys.path.insert(0, _rp)

from pytigon_lib import init_paths  # noqa: E402

init_paths()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings_app")

import django  # noqa: E402
from django.core.wsgi import get_wsgi_application  # noqa: E402

django.setup()

application = get_wsgi_application()
