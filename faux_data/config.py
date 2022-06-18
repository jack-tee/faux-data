#    Copyright 2022 @jack-tee
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
"""
Module for environment level config.
"""
import logging
import os
from pathlib import Path

from dynaconf import Dynaconf, Validator

log = logging.getLogger(__name__)

settings = Dynaconf(
    envvar_prefix="FAUXDATA",
    settings_files=[
        Path.home() / '.fauxdata/config.toml',
    ],
)


def default_gcp_project_id(settings, validator):
    if settings.get("gcp_project_id"):
        return
    if os.environ.get("GOOGLE_PROJECT_ID"):
        return os.environ.get("GOOGLE_PROJECT_ID")
    else:
        return "NOTSET"


settings.validators.register(Validator("DEPLOYMENT_MODE", default="local"))
settings.validators.register(
    Validator("GCP_PROJECT_ID", default=default_gcp_project_id))

settings.validators.validate_all()


def log_config():
    params = ["deployment_mode", "gcp_project_id"]
    return [f"{param} is set to: [{settings.get(param)}]" for param in params]