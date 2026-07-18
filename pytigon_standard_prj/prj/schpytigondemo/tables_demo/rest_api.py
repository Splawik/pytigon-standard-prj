"""Auto-generated REST API endpoints for the tables_demo module.

Registers REST API routes for all models defined in the tables_demo module
using pytigon_lib's automatic API generation utility.
"""
from pytigon_lib.schdjangoext.rest_tools import create_api_for_models
from . import models

urlpatterns = []
create_api_for_models(models, urlpatterns)
