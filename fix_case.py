"""
The windows file system is case insensitive but git is case sensitive.
This means that if you change the capitalisation of the file git will not notice.
The only way I have found is to delete the files with wrong capitalisation, commit their removal and readd them again.
"""

import os
import glob
import zipfile
zip_path = r"C:\Users\james_000\Downloads\PyMCTranslate-dev.zip"

if os.path.isfile(zip_path) and os.path.isdir('PyMCTranslate/json'):
    git = set()
    with zipfile.ZipFile(zip_path) as zip:
        for p in zip.namelist():
            p: str
            if 'PyMCTranslate/json/' in p and p.endswith('.json'):
                i = p.index('PyMCTranslate/json/') + len('PyMCTranslate/json/')
                git.add(p[i:])
    local = [os.path.relpath(p, 'PyMCTranslate/json').replace('\\', '/') for p in glob.iglob('PyMCTranslate/json/**/*.json', recursive=True)]
    for p in local:
        if p not in git:
            os.remove(os.path.join('PyMCTranslate/json', p))

else:
    print('could not find json folder to compare with')
