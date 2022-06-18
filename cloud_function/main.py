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

import logging
import traceback

from faux_data.template import Template

logging.basicConfig(level='DEBUG')


def generate(request):
    """Entry point for the Google Cloud Function."""

    request_json = request.get_json()

    logging.info(request_json)

    try:
        if "template" in request_json:
            t = Template.from_file(request_json["template"],
                                   params=request_json)

        elif "template_str" in request_json:
            t = Template.from_base64_string(request_json["template_str"])

        else:
            raise FauxDataSetupException(
                "No template provided. Please provide a `template` or `template_str` parameter."
            )

        t.run()
        logging.info(t)
        return f"Completed {t.template_path}"

    except Exception as e:
        logging.error(e)
        return ''.join(traceback.format_exception(e)), 500


class FauxDataSetupException(Exception):
    pass
