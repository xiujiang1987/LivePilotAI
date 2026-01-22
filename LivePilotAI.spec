# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

mp_datas, mp_binaries, mp_hiddenimports = collect_all('mediapipe')


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=mp_binaries,
    datas=[('src', 'src'), ('models', 'models'), ('config', 'config')] + mp_datas,
    hiddenimports=[
        'cv2', 
        'PIL', 
        'numpy', 
        'speech_recognition', 
        'pyaudio'
    ] + mp_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tensorflow', 'torch', 'torchvision', 'scipy', 'pandas', 'matplotlib', 'notebook'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='LivePilotAI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
