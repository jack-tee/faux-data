import sys

from .template import Template

def parse_params(args):
    args_iter = iter(args)

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

def main():
    try:
        cmd = sys.argv[1]
    except IndexError as e:
        show_help()
        sys.exit(1)

    match cmd:
        case 'run':
            filename = sys.argv[2]
            params = parse_params(sys.argv[3:])
            print(params)
            t = Template.from_file(filename)
            t.generate()
            print(t.tables[0].df.head(5))

        case _:
            raise Exception(f"Unrecognised command {cmd}")
