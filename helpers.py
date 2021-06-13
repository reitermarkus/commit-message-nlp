import re
from time import sleep, perf_counter

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, accuracy_score

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

  # Normalize email addresses.
  commit_message = re.sub(r'[\w_.-]+[@][\w_.-]+\.\w+', 'EMAIL_ADDRESS', commit_message)

  return word_tokenize(commit_message)

def test(item):
  i, ((training_index, test_index), source_data, target_data) = item

  start = perf_counter()

  source_training_data, source_test_data = source_data[training_index], source_data[test_index]
  target_training_data, target_test_data = target_data[training_index], target_data[test_index]

  log_reg = LogisticRegression(solver='newton-cg')
  log_reg.fit(source_training_data, target_training_data)

  target_prediction_data = [round(value) for value in log_reg.predict(source_test_data)]

  accuracy = accuracy_score(target_test_data, target_prediction_data)
  f1_micro = f1_score(target_test_data, target_prediction_data, average='micro')
  f1_macro = f1_score(target_test_data, target_prediction_data, average='macro')

  stop = perf_counter()
  print(f'Fold {i} took {stop - start:0.3f} seconds.')
  print("  Accuracy:", accuracy)
  print("  F1 micro:", f1_micro)
  print("  F1 macro:", f1_macro)

  return [accuracy, f1_micro, f1_macro]
