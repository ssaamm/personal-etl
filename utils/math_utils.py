from __future__ import division

def rolling_average(lst, window):
    if window > len(lst):
        raise ValueError("Can't take rolling {m}-avg of {n} values".format(m=window, n=len(lst)))

    for i in range(window, len(lst) + 1):
        avg = sum(lst[j] for j in range(i - window, i)) / window
        yield avg
