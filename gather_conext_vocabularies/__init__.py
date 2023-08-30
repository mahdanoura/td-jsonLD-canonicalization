import os
from pathlib import Path

cwd = Path(os.getcwd())
base = '.'
if cwd.name == 'gather_context_vocabularies':
    base = '..'
elif cwd.name == 'current':
    base = '../..'

ONTOLOGY_DIRECTORY = Path(base) / 'ontology'
