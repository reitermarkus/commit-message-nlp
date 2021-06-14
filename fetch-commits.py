#!/usr/bin/env python3

import shutil
import os
from datetime import datetime
from pathlib import Path
from time import sleep, perf_counter
import itertools
import csv
from github import Github
import git
import re

result_cache_dir = Path(os.environ.get('RESULT_CACHE_DIR') or 'results/clones')
g = Github(os.environ['GITHUB_TOKEN'], per_page=100)

# Top 10 most wanted languages (excluding SQL), from:
# https://insights.stackoverflow.com/survey/2020#technology-most-loved-dreaded-and-wanted-languages-loved
LANGUAGES = [
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

MAX_COMMITS_PER_LANGUAGE = 100000
MAX_COMMITS_PER_REPO = 10000
MAX_COMMITS_PER_AUTHOR = 100

exceptions = []

with open("exceptions.txt") as ex:
  exceptions = ex.readlines()

def is_excluded(commit_message):
  for exception in exceptions:
    match = re.match(exception, commit_message)

    if match:
      return True

  return False

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

authors = {}

for language in LANGUAGES:
  language_commit_count = 0
  language_time = perf_counter()
  check_rate_limit(resource='search', show=True)
  all_commits = []

  for repo in g.search_repositories(query=f'language:{language}', sort='stars', order='desc'):
    repo_commit_count = 0

    print(f'Fetching repo {repo.full_name}')
    path = result_cache_dir/repo.full_name

    if not path.exists():
      path.mkdir(parents=True, exist_ok=True)
      try:
        git.Git(path).clone(repo.git_url)
      except KeyboardInterrupt as e:
        shutil.rmtree(path)
        raise e

    print(f'Inspecting repo {repo.full_name}')
    cloned_repo = git.Repo(f'{path}/{repo.name}')

    commits = cloned_repo.iter_commits(no_merges=True)

    done = False
    for commit in commits:
      if is_excluded(commit.message):
        continue

      author = commit.author.email
      if author not in authors:
        authors[author] = 1
      else:
        authors[author] += 1

      if authors[author] > MAX_COMMITS_PER_AUTHOR:
        continue

      all_commits.append([repo.full_name, language, author, commit.message])

      language_commit_count += 1
      repo_commit_count += 1
      if language_commit_count >= MAX_COMMITS_PER_LANGUAGE:
        done = True
        break
      elif repo_commit_count >= MAX_COMMITS_PER_REPO:
        break

    print(f'Gathered {repo_commit_count} commits for repo {repo.full_name}. ({language_commit_count}/{MAX_COMMITS_PER_LANGUAGE})')

    if done:
      stop_time = perf_counter()
      print(f'Gathered {MAX_COMMITS_PER_LANGUAGE} commits in {stop_time - language_time:0.4f} seconds.')
      break

  csv_path = Path('results')/'csv'/f'{language}.csv'
  csv_path.parent.mkdir(parents=True, exist_ok=True)

  with open(csv_path, 'w+', encoding='utf-8') as out:
    csv_out = csv.writer(out, lineterminator='\n')
    csv_out.writerow(['repository', 'language', 'author', 'message'])
    for c in all_commits:
      csv_out.writerow(c)

print("------------------------------------------------------")
stop_time = perf_counter()
print(f"Gathered data took {stop_time - start_time:0.4f} seconds")
