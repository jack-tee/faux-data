import logging
import sys
import time
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

            prev_elem = elem
            continue
        else:
            if prev_elem:
                params[prev_elem.strip("-")] = elem
                prev_elem = None
            else:
                print(f"don't know waht to do with {elem}")
    if elem.startswith("--"):
        params[elem.strip("-")] = True
    
    return  params


def show_help():
    print("help")

def cmd(args: List[str]):
    try:
        cmd = args[1]
    except IndexError as e:
        show_help()
        sys.exit(1)

    match cmd:
        case 'run':
            # run the template
            filename = args[2]
            params = parse_params(args[3:])
            set_debug(params)
            t = Template.from_file(filename, params)
            t.generate()
            print(t)

        case 'render':
            # render the template
            filename = args[2]
            params = parse_params(args[3:])
            set_debug(params)
            t = Template.render_from_file(filename, params)
            show_template(filename, params, t)

        case 'sample':
            # generate data and show a sample
            filename = args[2]
            params = parse_params(args[3:])
            set_debug(params)

        case _:
            raise Exception(f"Unrecognised command {cmd}")

def show_template(filename, params, t):
    s = f"""
Filename: {filename}
Input params: {params}
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