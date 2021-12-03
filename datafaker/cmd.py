import sys
from typing import List

from .template import Template
from .utils import get_parts


def parse_params(args):
    args = " ".join(args)
    parts = get_parts(args)

    args_iter = iter(parts)

    params = {}
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
            filename = args[2]
            params = parse_params(args[3:])
            print(params)
            t = Template.from_file(filename)
            t.generate()
            print(t.tables[0].df.head(5))

        case _:
            raise Exception(f"Unrecognised command {cmd}")


def main():
    cmd(sys.argv)