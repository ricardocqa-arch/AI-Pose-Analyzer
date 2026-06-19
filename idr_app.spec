# -*- mode: python ; coding: utf-8 -*-
import os
import mediapipe
import gradio
from PyInstaller.utils.hooks import collect_data_files

# Encontrar o caminho real onde o Gradio e media pipe
mp_path = os.path.dirname(mediapipe.__file__)
gradio_path = os.path.dirname(gradio.__file__)
block_cipher = None

added_files = [
    ('exoskeletons.db', '.'),
    # LINHAS DOS LOGÓTIPOS REMOVIDAS DAQUI PARA EVITAR ERROS DE COMPILAÇÃO
    ('video abertura.mp4', '.'),
    ('video final.mp4', '.'),
    ('arial.ttf', '.'),
    (mp_path, 'mediapipe'),
    (gradio_path, 'gradio'),
]


libs = ['safehttpx', 'groovy', 'gradio_client', 'fastapi', 'uvicorn', 'starlette']
for lib in libs:
    try:
        added_files += collect_data_files(lib)
    except:
        pass

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=[
        'mediapipe',
        'cv2',
        'pandas',
        'gradio',
        'safehttpx',
        'groovy',
        'fastapi',
        'uvicorn',
        'starlette',
        'mediapipe.python.solutions.pose',
        'mediapipe.python.solutions.drawing_utils',
        'mediapipe.python.solutions.drawing_styles'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='AI_Pose_Analyzer', # Nome atualizado para o teu portefólio pessoal
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AI_Pose_Analyzer', # Alinhado com o novo nome da pasta de distribuição
)