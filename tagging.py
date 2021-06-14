import re

GITMOJI_MAPPINGS = {
  ':memo:':             'docs',        # Documentation
  ':zap:':              'perf',        # Performance
  ':fire:':             'remove',      # Removal
  ':sparkles:':         'feat',        # Feature
  ':bug:':              'fix',         # Bug Fix
  ':lipstick:':         'ui',          # UI
  ':wrench:':           'config',      # Configuration
  ':hammer:':           'development', # Development Scripts
  ':art:':              'refactor',    # Improve Code Structure/Format
  ':white_check_mark:': 'test',        # Tests
  ':chore:':            'chore',       # Chore
  ':up:':               'update',      # Update
  ':arrow_up:':         'deps',        # Dependency Update
  ':arrow_down:':       'deps',        # Dependency Downgrade
  ':bulb:':             'docs',        # Update Source Code Comments
  ':rocket:':           'deploy',      # Deployment
  ':pencil2:':          'typo',        # Fix Typo
  ':green_heart:':      'ci',          # Fix CI
  ':construction:':     'wip',         # Work In Progress
  ':recycle:':          'refactor',    # Refactor Code
}

TAG_MAPPINGS = {
  'bug':           'fix',
  'bugfix':        'fix',
  'testing':       'test',
  'tests':         'test',
  'tst':           'test',
  'documentation': 'docs',
  'doc':           'docs',
  'changelog':     'docs',
  'feature':       'feat',
  'gui':           'ui',
}

def message_to_tag(message):
  message = message.lower()

  # Extract “Conventional Commits”.
  match = re.match(r'^([^(\s:]+)(?:\([^)]+\))?!?:\s*(.*)$', message)
  if match:
    tag = match[1]
    message = match[2]
    return (message, TAG_MAPPINGS.get(tag) or tag)

  # Extract “Gitmoji Commits”.
  match = re.match(r'^(:[a-z0-9_]+:)\s*(.*)$', message)
  if match:
    tag = match[1]
    message = match[2]
    return (message, GITMOJI_MAPPINGS.get(tag) or tag)

  return (message, None)

KNOWN_TAGS = set([
  'build',
  'chore',
  'ci',
  'deps',
  'docs',
  'feat',
  'fix',
  'perf',
  'refactor',
  'style',
  'test',
  'examples',
])

def message_to_known_tag(message):
  message, tag = message_to_tag(message)
  return (message, tag) if tag in KNOWN_TAGS else (message, None)
