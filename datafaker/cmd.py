import logging
import sys
from typing import List

from .template import Template
from .utils import get_parts


def parse_params(args):
    args = " ".join(args)
    parts = get_parts(args)

    #print(parts)
    args_iter = iter(parts)

    params = {}
    elem = ""
    prev_elem = None
    for elem in args_iter:
        if elem.startswith("--"):
            if prev_elem:
                params[prev_elem.strip("-")] = True

            if "=" in elem:
                params[elem.split("=")[0].strip("-")] = elem.split("=")[1]
                continue

        else:
            if prev_elem:
                params[prev_elem.strip("-")] = elem
                prev_elem = None
                continue
            else:
                print(f"don't know waht to do with {elem}")

        prev_elem = elem

    if prev_elem:
        params[prev_elem.strip("-")] = True
    
    return  params




def cmd(args: List[str]):
    """The main entry point to the cli."""

    try:
        cmd_args = args[1:]
    except IndexError as e:
        show_help()
        sys.exit(1)

    match cmd_args:
        case [] | ["--help"] | ["-h"]:
            show_help()

        case [cmd, filename, *objs]:
            params = parse_params(objs)
            set_debug(params)

            match cmd:
                case 'run':
                    t = Template.from_file(filename, params)
                    t.run()
                    print(t)

                case 'render':
                    t = Template.render_from_file(filename, params)
                    show_template(filename, params, t)

                case 'sample':
                    t = Template.from_file(filename, params)
                    t.generate()
                    print(t)

                case _:
                    Exception(f"Unrecognised command {cmd}")

        case _:
            print("Unrecognised args [{cmd_args}]")
            show_help()

def show_help():
    s = """\
datafaker - a fake data generator.

Usage:
  datafaker [command]

Available Commands:
  render filename.yaml [params]    render a template
  sample filename.yaml [params]    generate a sample dataset for a template
  run filename.yaml [params]       run a template loading data to the specified targets

Flags:
  --debug    enable debug logging

  extra flags are passed to the template to override variables
  e.g datafaker render templates/mytemplate.yaml --myvar=foo
"""
    print(s)

def show_template(filename, params, t):
    s = f"""\
Filename: {filename}
Input params: {params}
===================== Resolved Parameters ======================

====================== Rendered Template =======================
{t}
================================================================"""
    print(s)



def set_debug(params: dict) -> None:
    if params.get("debug"):
        logging.basicConfig(level="DEBUG")
        logging.debug(f"Parsed params {params} from args {sys.argv}")
    else:
        logging.basicConfig(level="INFO")
    

def main():
    cmd(sys.argv)

if __name__ == '__main__':
    cmd(sys.argv)
