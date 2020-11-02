# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['src\\main\\main_viewer.py'],
             pathex=['C:\\Users\\DEV-C2-2\\PythonProject\\XuRequest'],
             binaries=[],
             datas=[('src\\main\\icons', 'icons'), ('src\\main\\stylesheet', 'stylesheet'), ('src\\main\\html', 'html')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='JSON XuViewer',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False , icon='src\\main\\icons\\json.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='JSON XuViewer')
