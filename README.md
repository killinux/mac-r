# mac-r

HTTP 轮询方式远程控制 Mac，适用于 Mac 无公网 IP 的场景。

## Server（Windows）

```bash
python server.py [端口]
```

默认端口 8900，启动后浏览器打开 `http://localhost:8900` 即可输入命令、查看结果。

## Client（Mac）

```bash
bash mac_agent.sh <Windows_IP> [端口] [轮询间隔秒]
```

示例：

```bash
bash mac_agent.sh 192.168.1.100 8900 3
```

Mac 每隔几秒轮询一次，拿到命令就执行，结果自动回传。

## 依赖

- Python 3（Windows/Mac 均自带或易装）
- curl（Mac 自带）
