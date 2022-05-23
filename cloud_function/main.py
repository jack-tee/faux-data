from faux_data.template import Template

import logging

logging.basicConfig(level='DEBUG')


def generate(request):
    """Entry point for the Google Cloud Function."""

    request_json = request.get_json()
    # if not request.args:
    #     raise ValueError("no request args")

    logging.info(request_json)

    if "template" in request_json:
        t = Template.from_file(request_json["template"], params=request_json)

    elif "template_str" in request_json:
        t = Template.from_base64_string(request_json["template_str"])

    else:
        raise ValueError(
            "No template provided. Please provide a `template` or `template_str` parameter."
        )

    t.run()
    logging.info(t)
    return "done"