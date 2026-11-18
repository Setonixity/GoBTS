if sys.platform == "darwin":
    exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name=APP_NAME,
              console=False, upx=False, strip=False)
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