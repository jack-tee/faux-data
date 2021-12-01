import re
import yaml
import chevron
from typing import List


def get_parts(val: str):
    """Splits a string into parts respecting double and single quotes
    
    Examples:
        >>> get_parts("mycol Random Timestamp \"2023-03-03 00:00:00\" '2026-12-12 23:59:59'")
        ["mycol", "Random", "Timestamp", "2023-03-03 00:00:00", "2026-12-12 23:59:59"]

    """
    groups = re.findall(r"[ ]?(?:(?!\"|')(\S+)|(?:\"|')(.+?)(?:\"|'))[ ]?",
                        val)

    # there are two matching groups for the two cases so get the first non empty val
    def first_non_empty(g):
        if g[0]:
            return g[0]
        else:
            return g[1]

    return [first_non_empty(group) for group in groups]


def render_template(template_str: str, builtin_vars: dict, runtime_vars: dict):

    vars_ = resolve_variables(template_str, builtin_vars, runtime_vars)

    rendered_template = chevron.render(template_str, vars_, warn=True)
    return rendered_template


def resolve_variables(template_str: str, builtin_vars: dict,
                      runtime_vars: dict):
    """Resolve the template variables using the builtin and runtime provided variables.
    Returns the final set of vars to be applied to the template"""

    variable_lines = extract_variable_lines(template_str)
    builtin_vars.update(runtime_vars)
    vars_ = builtin_vars.copy()

    if not variable_lines:
        # no vars in template so just return builtins plus runtime vars
        return vars_

    for variable_line in variable_lines:
        rendered_var_line = chevron.render(variable_line, vars_)
        var = yaml.safe_load(rendered_var_line)

        key = list(var)[0]  # get the key of the only element
        if key not in vars_:
            vars_.update(var)

    return vars_


def extract_variable_lines(template_str: str) -> List[str] | None:
    """Extracts the variables from a template as a list of strings"""
    print(template_str)
    pattern = r"(?:^variables:)(.*)(?:^tables:)"
    r = re.search(pattern, template_str, re.DOTALL | re.MULTILINE)

    if r:
        lines = r.group(1).splitlines()
        return [line.strip() for line in lines if line.strip() != ""]
    else:
        # no variables in this template
        return None
