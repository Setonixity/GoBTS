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

if sys.platform == "darwin":
    # macOS .app bundles should stay one-folder
    exe = EXE(
        pyz,
        a.scripts,
        [],
        exclude_binaries=True,
        name=APP_NAME,
        console=False,
        upx=False,
        strip=False,
    )
    coll = COLLECT(exe, a.binaries, a.datas, name=APP_NAME, upx=False, strip=False)
    app = BUNDLE(coll, name="GOBTS.app", bundle_identifier="setonixity.gobts")
else:
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.datas,
        [],
        name=APP_NAME,
        console=False,
        upx=False,
        strip=False,
        runtime_tmpdir=None,
    )