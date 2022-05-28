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
    except Exception as e:
        logging.error(e)
        return ''.join(traceback.format_exception(e)), 500

    return "done"


class FauxDataSetupException(Exception):
    pass
