#!/usr/bin/env python3

import os
from pathlib import Path
import csv
from github import Github

g = Github(os.environ['GITHUB_TOKEN'])

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

repository_register = {}

for language in languages:
  commit_count = 0
  repo_page = 0

  while commit_count < 100000:
    repositories = g.search_repositories(query=f'language:{language}', sort='stars', order='desc').get_page(repo_page)

    if not repositories:
      break

    for repo in repositories:
      print(f'Fetching repo {repo.full_name}')
      path = Path('results')/'repo'/f'{repo.full_name}.csv'

      if path.exists():
        print(f'Already contained in cache.')
        continue

      commit_page = 0
      all_commits = []

      while len(all_commits) < 10000:
        commits = repo.get_commits().get_page(commit_page)

        if not commits:
          break

        for c in commits:
          commit = c.commit

          merge_commit = len(commit.parents) > 1
          if merge_commit:
            continue

          all_commits.append((repo.full_name, repr(c.commit.message)))

        commit_page += 1

      path.parent.mkdir(parents=True, exist_ok=True)
      with open(path, 'w+', encoding='utf-8') as out:
        csv_out = csv.writer(out, lineterminator='\n')
        csv_out.writerow(['repository', 'message'])
        for row in all_commits:
          csv_out.writerow(row)

      print(f'Fetched {len(all_commits)} commits.')
      commit_count += len(all_commits)

    repo_page += 1
