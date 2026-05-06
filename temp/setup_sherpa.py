#!/usr/bin/env python3
"""Set up ios_TTS with Sherpa-ONNX TTS
复制 xcframework、模型文件、Swift wrapper 到项目中
通过 base64 编码传输到 Mac 执行"""
import os
import shutil

BASE = "/Users/bytedance/Desktop/hehe/ioswork"
SRC = f"{BASE}/ios_TTS/sherpa-onnx-src"
PROJ = f"{BASE}/ios_TTS"

def w(path, content):
    full = os.path.join(PROJ, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, 'w') as f:
        f.write(content)

# Copy Swift API wrapper
shutil.copy2(f"{SRC}/swift-api-examples/SherpaOnnx.swift", f"{PROJ}/ios_TTS/SherpaOnnx.swift")

# Copy onnxruntime.xcframework
for item in os.listdir(f"{SRC}/build-ios/ios-onnxruntime"):
    if item.endswith('.xcframework'):
        dst = f"{PROJ}/{item}"
        if os.path.exists(dst): shutil.rmtree(dst)
        shutil.copytree(f"{SRC}/build-ios/ios-onnxruntime/{item}", dst)

# Copy sherpa-onnx.xcframework
dst = f"{PROJ}/sherpa-onnx.xcframework"
if os.path.exists(dst): shutil.rmtree(dst)
shutil.copytree(f"{SRC}/build-ios/sherpa-onnx.xcframework", dst)

# Copy model files (int8 for smaller size)
model_src = f"{PROJ}/vits-melo-tts-zh_en"
model_dst = f"{PROJ}/ios_TTS/model-files"
if os.path.exists(model_dst): shutil.rmtree(model_dst)
os.makedirs(model_dst, exist_ok=True)

for f in ['model.int8.onnx', 'model.onnx', 'tokens.txt', 'lexicon.txt', 'date.fst', 'number.fst', 'phone.fst', 'new_heteronym.fst']:
    src_f = f"{model_src}/{f}"
    if os.path.exists(src_f):
        shutil.copy2(src_f, f"{model_dst}/{f}")

dict_src = f"{model_src}/dict"
if os.path.exists(dict_src):
    shutil.copytree(dict_src, f"{model_dst}/dict")

print("Setup complete")
