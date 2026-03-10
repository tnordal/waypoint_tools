# -*- mode: python ; coding: utf-8 -*-

"""
PyInstaller spec file for DJI Waypoint Tools.
Build with: pyinstaller waypoint_tools.spec
"""

import sys
from pathlib import Path

block_cipher = None

# Application info
app_name = "DJI Waypoint Tools"
app_version = "1.0.0"

# Determine paths
src_path = Path("src").absolute()
icon_path = None  # TODO: Add icon file

a = Analysis(
    ["src/waypoint_tools/__main__.py"],
    pathex=[str(src_path)],
    binaries=[],
    datas=[],
    hiddenimports=[
        "win32com.client",
        "win32com.shell.shell",
        "win32com.shell.shellcon",
        "PyQt6.QtCore",
        "PyQt6.QtGui",
        "PyQt6.QtWidgets",
        "lxml.etree",
        "lxml._elementpath",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "matplotlib",
        "numpy",
        "pandas",
        "PIL",
        "tkinter",
        "test",
        "unittest",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher,
)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="DJI Waypoint Tools",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Windows GUI app (no console)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_path,
    version="version_info.txt" if Path("version_info.txt").exists() else None,
)
