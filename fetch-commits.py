#!/usr/bin/env python3

import bq_helper

# https://www.kaggle.com/poonaml/analyzing-3-million-github-repos-using-bigquery
github_repos = bq_helper.BigQueryHelper(
  active_project= "bigquery-public-data",
  dataset_name = "github_repos",
)

# print(github_repos.list_tables())
#
# print(github_repos.head('languages'))
#
# print(github_repos)

from google.cloud import bigquery
import pandas as pd

client = bigquery.Client()

QUERY = """
SELECT message
FROM `bigquery-public-data.github_repos.commits`
WHERE LENGTH(message) > 10 AND LENGTH(message) <= 80
LIMIT 10000
"""

query_job = client.query(QUERY)

iterator = query_job.result(timeout=30)
rows = list(iterator)

for v in rows:
  commit_message = list(v.values())[0]

  if commit_message.startswith('chore'):
    print(commit_message)

# commit_messages = pd.DataFrame(data=[list(x.values()) for x in rows], columns=list(rows[0].keys()))
#
# # Look at the first 10 headlines
# print(commit_messages.head(1000))

