# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[
        ('adb.exe', '.'),
        ('AdbWinApi.dll', '.'),
    ],
    datas=[
        ('img', 'img'),  # Copy img folder to _internal/img
    ],
    hiddenimports=[
        'PIL._tkinter_finder',
        'customtkinter',
        'cv2',
        'numpy',
        'ppadb',
        'ppadb.client',
        'ppadb.device',
        'psutil',
        'requests',
        'src.utils.version_checker',
        'src.utils.logger',
        'src.utils.notifications',
        'src.core.config',
        'src.core.device_manager',
        'src.core.image_recognition',
        'src.core.game_controller',
        'src.activities.daily_activities',
        'src.activities.arena_activities',
        'src.activities.guild_activities',
        'src.activities.bounty_activities',
        'src.activities.shop_activities',
        'src.activities.tower_activities',
        'src.activities.misc_activities',
        'src.activities.summon_activities',
        'src.activities.labyrinth_activities',
        'src.activities.campaign_activities',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'scipy',
        'pandas',
        'flask',
        'flask_socketio',
        'plyer',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='AutoAFK',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='img/auto.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AutoAFK',
)
