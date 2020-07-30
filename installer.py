import os

import PyInstaller.__main__

PyInstaller.__main__.run([
    '--name=XuRequest',
    # '--onefile',
    '--noconsole',
    '--add-data=src\\main\\icons;icons',
    '--add-data=src\\main\\stylesheet;stylesheet',
    '--add-data=src\\main\\html;html',
    '--icon=src\\main\\icons\\main_window_icon.ico',
    os.path.join("", 'src\\main\\main.py'),
])
