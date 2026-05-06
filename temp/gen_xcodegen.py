#!/usr/bin/env python3
"""生成 project.yml 和 BridgingHeader.h，用 xcodegen 生成 Xcode 项目"""

PROJ = "/Users/bytedance/Desktop/hehe/ioswork/ios_TTS"

yml = '''name: ios_TTS
options:
  bundleIdPrefix: com.example
  deploymentTarget:
    iOS: "16.0"

targets:
  ios_TTS:
    type: application
    platform: iOS
    sources:
      - path: ios_TTS
        excludes:
          - model-files/**
          - Info.plist
      - path: ios_TTS/model-files
        buildPhase: resources
        type: folder
    info:
      path: ios_TTS/Info.plist
      properties:
        CFBundleDisplayName: 网页朗读器
        NSAppTransportSecurity:
          NSAllowsArbitraryLoads: true
        UILaunchScreen: {}
    settings:
      base:
        PRODUCT_BUNDLE_IDENTIFIER: com.example.ios-TTS
        SWIFT_VERSION: "5.0"
        SWIFT_OBJC_BRIDGING_HEADER: ios_TTS/BridgingHeader.h
        OTHER_LDFLAGS:
          - -lc++
        CODE_SIGN_STYLE: Automatic
        TARGETED_DEVICE_FAMILY: "1,2"
    dependencies:
      - framework: sherpa-onnx.xcframework
        embed: false
      - framework: onnxruntime.xcframework
        embed: false
'''

with open(f"{PROJ}/project.yml", 'w') as f:
    f.write(yml)

bridging = '''#ifndef BridgingHeader_h
#define BridgingHeader_h
#include "sherpa-onnx/c-api/c-api.h"
#endif
'''
with open(f"{PROJ}/ios_TTS/BridgingHeader.h", 'w') as f:
    f.write(bridging)

print("Generated project.yml and BridgingHeader.h")
