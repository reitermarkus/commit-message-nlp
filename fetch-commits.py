#!/usr/bin/env python3

import os
import csv
from github import Github

token = os.environ['GITHUB_TOKEN']

g = Github(token)

languages = ['rust', 'python', 'ruby', 'c', 'haskell', 'c#', 'javascript']

repository_register = {}

for language in languages:
  repositories = g.search_repositories(query='stars:>10000 language:' + language).get_page(0)
  repository_register[language] = repositories[:5]

for l in languages:
  all_commits = []

  for repository in repository_register[l]:
    commits = [ (repository.name, repr(c.commit.message)) for c in repository.get_commits().get_page(0)[:20] ]
    all_commits.extend(commits)

  with open(f'results/{l}.csv', 'w+', encoding='utf-8') as out:
    csv_out = csv.writer(out, lineterminator='\n')
    csv_out.writerow(['repository','message'])
    for row in all_commits:
      csv_out.writerow(row)
