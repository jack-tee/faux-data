from datafaker.template import Template


## Google Cloud Function Entrypoint
def generate(request):
    """Entry point for the Google Cloud Function."""

    request_json = request.get_json()
    if not request.args:
        raise Exception("no request args")

    if "template" in request.args:
        # passing a template path
        # read file from cloud storage and initialise template
        t = Template.from_string("baa")

    elif "template_str" in request.args:
        t = Template.from_base64_string(request.args["template_str"])

    t.generate()
    return t.result()