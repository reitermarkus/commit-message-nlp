import re

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

stopwords = stopwords.words('english')

def reduce_list(a, b):
  a += b
  return a

def tokenize(commit_message):
  commit_message = commit_message.lower()

  # Normalize pull request number.
  commit_message = re.sub(r'#\d+', 'PULL_REQUEST_NUMBER', commit_message)

  # Normalize version numbers.
  commit_message = re.sub(r'\b\d+(\.\d+)+\b', 'VERSION_NUMBER', commit_message)

  # Normalize URLs.
  commit_message = re.sub(r'\(https?://[^)]+\)', '(URL)', commit_message)
  commit_message = re.sub(r'https?://[^\s]+', 'URL', commit_message)

  words = word_tokenize(commit_message)

  # Remove stopwords.
  words = [word for word in words if not word in stopwords]

  return words
