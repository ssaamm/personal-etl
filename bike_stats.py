from __future__ import print_function
import sys

import pandas as pd

from workouts import get_raw_rows, SEP

if __name__ == '__main__':
    sep = SEP
    try:
        if sys.argv[1] == '-s':
            sep = sys.argv[2]
    except IndexError:
        pass

    cycling = pd.DataFrame([e._asdict() for e in get_raw_rows() if e.exercise.lower() == 'cycling']).set_index('timestamp')
    monthly_mileage = (
        cycling.groupby(pd.TimeGrouper('1M'))
        ['distance'].sum().to_frame()
    )
    monthly_mileage.to_csv(sys.stdout, sep=sep)
