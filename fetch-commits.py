#!/usr/bin/env python3

import os
from github import Github

token = os.environ['GITHUB_TOKEN']

g = Github(token)

languages = ['rust', 'python', 'ruby', 'c', 'haskell', 'c#', 'javascript']

repository_register = {}

for language in languages:
  repositories = g.search_repositories(query='stars:>10000 language:' + language).get_page(0)
  repository_register[language] = repositories[:5]

