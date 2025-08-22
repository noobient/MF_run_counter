# -*- mode: python ; coding: utf-8 -*-
import PyInstaller.config
import os
PyInstaller.config.CONF['distpath'] = './dict_release'

block_cipher = None
path = os.getcwd()


a = Analysis(['..\\main.py'],
             pathex=[path + '\\..\\MF_run_counter'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
a.datas += [('d2icon.png', path+'\\..\\MF_run_counter\\media\\d2icon.png', 'DATA')]
a.datas += [('run_sound.wav', path+'\\..\\MF_run_counter\\media\\run_sound.wav', 'DATA')]
a.datas += [('icon.ico', path+'\\..\\MF_run_counter\\media\\icon.ico', 'DATA')]
a.datas += [('item_library.csv', path+'\\..\\MF_run_counter\\media\\item_library.csv', 'DATA')]
a.datas += [('stat_map.csv', path+'\\..\\MF_run_counter\\media\\stat_map.csv', 'DATA')]
a.datas += [('caret-down.png', path+'\\..\\MF_run_counter\\media\\caret-down.png', 'DATA')]
a.datas += [('caret-up.png', path+'\\..\\MF_run_counter\\media\\caret-up.png', 'DATA')]
a.datas += [('about_icon.png', path+'\\..\\MF_run_counter\\media\\about_icon.png', 'DATA')]
a.datas += [('default_eth_grail_data.json', path+'\\..\\MF_run_counter\\utils\\default_eth_grail_data.json', 'DATA')]
a.datas += [('default_grail_data.json', path+'\\..\\MF_run_counter\\utils\\default_grail_data.json', 'DATA')]
pyz = PYZ(a.pure, a.zipped_data,
          cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='mf_timer',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False , icon=path+'\\media\\icon.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='mf_timer')
