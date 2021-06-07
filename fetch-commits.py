#!/usr/bin/env python3

import os
from datetime import datetime
from pathlib import Path
from time import sleep
import csv
from github import Github

g = Github(os.environ['GITHUB_TOKEN'], per_page=100)

# Top 10 most wanted languages (excluding SQL), from:
# https://insights.stackoverflow.com/survey/2020#technology-most-loved-dreaded-and-wanted-languages-loved
languages = [
  'python',
  'javascript',
  'go',
  'typescript',
  'rust',
  'kotlin',
  'java',
  'c++',
  'c#',
  'swift',
]

def check_rate_limit(resource, show=False):
  rate_limit = g.get_rate_limit()

  if resource == 'core':
    rate_limit = rate_limit.core

  if resource == 'search':
    rate_limit = rate_limit.search

  remaining = rate_limit.remaining
  limit = rate_limit.limit

  should_sleep = remaining / limit < 0.1

  if show or should_sleep:
    print(f'Rate limit ({resource}): {remaining}/{limit}')

  if not should_sleep:
    return

  current_time = datetime.utcnow()
  reset_time = rate_limit.reset

  reset_seconds = (reset_time - current_time).total_seconds()

  if reset_seconds < 0:
    return

  print(f'Rate limit resets in {reset_seconds} seconds, sleeping until then.')
  sleep(reset_seconds)

for language in languages:
  commit_count = 0
  check_rate_limit(resource='search', show=True)
  for repo in g.search_repositories(query=f'language:{language}', sort='stars', order='desc'):
    print(f'Fetching repo {repo.full_name}')
    path = Path('results')/'repo'/f'{repo.full_name}.csv'

    if path.exists():
      print(f'Already contained in cache.')
      continue

    all_commits = []

    check_rate_limit(resource='core', show=True)
    for c in repo.get_commits():
      commit = c.commit

      merge_commit = len(commit.parents) > 1
      if merge_commit:
        continue

      all_commits.append((repo.full_name, repr(c.commit.message)))
      print(f"\r{len(all_commits)}")
      if len(all_commits) >= 10000:
        break

      check_rate_limit(resource='core')

    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w+', encoding='utf-8') as out:
      csv_out = csv.writer(out, lineterminator='\n')
      csv_out.writerow(['repository', 'message'])
      for row in all_commits:
        csv_out.writerow(row)

    print(f'Fetched {len(all_commits)} commits.')
    commit_count += len(all_commits)
    if commit_count >= 100000:
      break

    check_rate_limit(resource='search', show=True)
