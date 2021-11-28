import re
import numpy as np
import pandas as pd


def empty_df(rows: int = 5) -> pd.DataFrame:
    return pd.DataFrame({"rowId": np.arange(rows)})


def strip_lborder(template_str):
    lines = template_str.splitlines()
    spaces = len(lines[1]) - len(lines[1].lstrip())
    output = []
    for line in lines:
        pattern = "^ {%d}" % spaces
        output.append(re.sub(pattern, "", line))

    return '\n'.join(output)