# mac-r

HTTP 轮询方式远程控制 Mac，适用于 Mac 无公网 IP 的场景。

## 工作原理

```
┌─────────────────┐         HTTP 短轮询          ┌─────────────────┐
│   Windows       │◄─────────────────────────────│      Mac        │
│   (有公网 IP)    │                              │   (无公网 IP)    │
│                 │  1. GET /cmd  (每3秒)         │                 │
│  server.py      │─────────────────────────────►│  mac_agent.sh   │
│  端口 8900      │  返回: {"cmd":"ls ~"}         │                 │
│                 │                              │  2. bash -c 执行 │
│                 │  3. POST /result             │                 │
│                 │◄─────────────────────────────│  回传 stdout/err│
└─────────────────┘                              └─────────────────┘
```

**核心流程：**

1. Windows 运行 HTTP 服务器（server.py），提供 Web 终端界面和 REST API
2. Mac 运行轮询脚本（mac_agent.sh），每隔几秒向 Windows 发 GET 请求拿命令
3. 拿到命令后 `bash -c` 执行，将 stdout、stderr、exit code 以 JSON POST 回服务器
4. 浏览器页面自动刷新显示结果；也可通过 API 程序化调用（如 Claude Code）

**为什么用短轮询：** Mac 没有公网 IP，无法接受入站连接。由 Mac 主动出站请求 Windows，每次都是独立的 HTTP 请求-响应，连完即断。断网不影响，恢复后继续轮询。

## Server（Windows）

```bash
python server.py [端口]
```

默认端口 8900，启动后浏览器打开 `http://localhost:8900` 即可输入命令、查看结果。

### API

| 接口 | 方法 | 说明 |
|------|------|------|
| `/` | GET | Web 终端界面 |
| `/cmd` | GET | Mac 轮询取命令 |
| `/cmd` | POST | 发送命令 `{"cmd": "ls ~"}` |
| `/result` | POST | Mac 回传执行结果 |
| `/results` | GET | 获取所有历史结果 |

## Client（Mac）

```bash
bash mac_agent.sh <Windows_IP> [端口] [轮询间隔秒]
```

示例：

```bash
bash mac_agent.sh 192.168.1.100 8900 3
```

## 实际应用：远程创建 iOS 项目

利用 mac-r，从 Windows 上的 Claude Code 远程控制 Mac 完成了以下工作：

### 1. 创建 ios_TTS 项目

通过 base64 编码传输 Python 脚本到 Mac 执行（避免 JSON 转义问题），自动生成完整的 Xcode 项目结构。

### 2. 集成 Sherpa-ONNX 离线 TTS

```
Mac 端执行的步骤（全部通过 mac-r 远程完成）：
├── brew install cmake          # 安装构建工具
├── git clone sherpa-onnx       # 拉取源码
├── bash build-ios.sh           # 编译 iOS xcframework
├── 下载 vits-melo-tts-zh_en 模型  # 中文神经网络 TTS 模型
├── brew install xcodegen       # 安装项目生成工具
├── xcodegen generate           # 生成 .xcodeproj
└── xcodebuild build            # 编译验证
```

### 3. ios_TTS 功能

App 包含两个 Tab：

**Tab 1 — 网页朗读**
- 输入 URL，抓取网页内容，去除 HTML 标签提取纯文字
- 使用 Sherpa-ONNX + MeloTTS 神经网络模型离线合成语音
- 可调语速（0.5x ~ 2.0x）
- TTS 完全离线，不需要网络

**Tab 2 — 论文翻译朗读**
- 输入任意论文 PDF 链接（如 `https://arxiv.org/pdf/2509.20021`）
- PDFKit 提取 PDF 全文文字
- Google Translate API 自动翻译成中文（分段翻译，无需 API Key）
- 翻译结果保存到本地（Documents 目录）
- Sherpa-ONNX 离线语音朗读翻译后的中文内容

### 4. 关键技术点

- **文件传输**：将脚本 base64 编码后通过命令 `echo 'BASE64' | base64 --decode | python3` 传输执行
- **项目生成**：使用 xcodegen 从 `project.yml` 生成 Xcode 项目，避免手写 pbxproj
- **模型打包**：model-files 目录作为 folder reference 打包进 app bundle
- **TTS 引擎**：Sherpa-ONNX (k2-fsa) + VITS MeloTTS 中英文模型，纯离线推理
- **PDF 解析**：iOS 原生 PDFKit 提取文字，无需第三方库
- **论文翻译**：Google Translate 免费 API 分段翻译，自动拼接结果

## 依赖

- Python 3（Windows/Mac 均自带或易装）
- curl（Mac 自带）
