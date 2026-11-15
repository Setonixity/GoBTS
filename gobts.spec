import sys

APP_NAME = "gobts"
DATA_FOLDERS = ["fonts", "images", "sounds", "themes"] 

a = Analysis(
    ["src/gobts/__main__.py"],
    pathex=["src"],
    binaries=[],
    datas=[(f"data/gobts/{folder}", f"data/gobts/{folder}") for folder in DATA_FOLDERS], 
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True, 
    name=APP_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False, 
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name=APP_NAME,
)

if sys.platform == "darwin":
    app = BUNDLE(
        coll,
        name="GOBTS.app",
        bundle_identifier="setonixity.gobts", 
    )