#!/usr/bin/env python3

import os
from datetime import datetime
from pathlib import Path
from time import sleep, perf_counter
import csv
from github import Github
import git

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

start_time = perf_counter()

for language in languages:
  commit_count = 0
  language_time = perf_counter()
  check_rate_limit(resource='search', show=True)

  for repo in g.search_repositories(query=f'language:{language}', sort='stars', order='desc'):
    print(f'Fetching repo {repo.full_name}')
    path = Path('results')/'clones'/repo.full_name

    if not path.exists():
      os.makedirs(path, exist_ok=True)
      git.Git(path).clone(repo.git_url)

    cloned_repo = git.Repo(f'{path}/{repo.name}')

    commits = list(cloned_repo.iter_commits(no_merges=True))
    print(f'Repo {repo.name} has {len(commits)} commits.')

    commit_count += len(commits)

    csv_path = Path('results')/'repo'/f'{repo.name}.csv'
    csv_path.parent.mkdir(parents=True, exist_ok=True)

    with open(csv_path, 'w+', encoding='utf-8') as out:
      csv_out = csv.writer(out, lineterminator='\n')
      csv_out.writerow(['repository', 'message'])
      for c in commits:
        csv_out.writerow([ repo.name, repr(c.message) ])

    if commit_count >= 100000:
      stop_time = perf_counter()
      print(f"Gathered {commit_count} commits in {stop_time - language_time:0.4f} seconds")
      break

print("------------------------------------------------------")
stop_time = perf_counter()
print(f"Gathered data took {stop_time - start_time:0.4f} seconds")
