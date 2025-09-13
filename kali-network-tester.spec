# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['route_stress_test.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('route-stress-test.nse', '.'),
        ('NSE_INSTALL.md', '.'),
        ('README.md', '.'),
    ],
    hiddenimports=[
        'ipaddress',
        'concurrent.futures',
        'json',
        'subprocess',
        'threading',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='kali-network-tester',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
