import os

import PyInstaller.__main__

request = [
    '--name=Xu Request',
    # '--onefile',
    '--noconsole',
    '--add-data=src\\main\\icons;icons',
    '--add-data=src\\main\\stylesheet;stylesheet',
    '--add-data=src\\main\\html;html',
    '--icon=src\\main\\icons\\it.ico',
    os.path.join("", 'src\\main\\main.py'),
]

json_viewer = [
    '--name=Xu JSON Viewer',
    # '--onefile',
    '--noconsole',
    '--add-data=src\\main\\icons;icons',
    '--add-data=src\\main\\stylesheet;stylesheet',
    '--add-data=src\\main\\html;html',
    '--icon=src\\main\\icons\\json.ico',
    os.path.join("", 'src\\main\\main_viewer.py'),
]

PyInstaller.__main__.run(json_viewer)
