from functools import reduce
from glob import glob
from pathlib import Path
from time import sleep, perf_counter

import pandas as pd

def read_csv(path):
  csv = pd.read_csv(path)

  # Ensure commit message is a string.
  csv['message'] = csv['message'].astype(str)

  return csv

def load_commits():
  start = perf_counter()

  commits_per_language = dict(map(lambda path: (Path(path).stem, read_csv(path)), glob('results/csv/*.csv')))
  all_commits = reduce(lambda a, b: pd.concat([a, b], ignore_index=True), commits_per_language.values())

  stop = perf_counter()
  print(f'Loading commits took {stop - start:0.3f} seconds.')

  return all_commits
