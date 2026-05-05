#!/bin/bash
# Mac 端 - 轮询执行脚本
# 用法: bash mac_agent.sh <WINDOWS_IP> [端口] [轮询间隔秒]
# 示例: bash mac_agent.sh 192.168.1.100 8900 3

SERVER="${1:?用法: bash mac_agent.sh <WINDOWS_IP> [端口] [间隔秒]}"
PORT="${2:-8900}"
INTERVAL="${3:-3}"
URL="http://${SERVER}:${PORT}"

echo "Polling ${URL} every ${INTERVAL}s ..."

while true; do
    resp=$(curl -s --connect-timeout 5 "${URL}/cmd" 2>/dev/null)
    cmd=$(echo "$resp" | python3 -c "import sys,json; print(json.load(sys.stdin).get('cmd',''))" 2>/dev/null)

    if [ -n "$cmd" ]; then
        echo "[RUN] $cmd"
        stdout_file=$(mktemp)
        stderr_file=$(mktemp)
        bash -c "$cmd" >"$stdout_file" 2>"$stderr_file"
        code=$?
        stdout_val=$(cat "$stdout_file")
        stderr_val=$(cat "$stderr_file")
        rm -f "$stdout_file" "$stderr_file"

        payload=$(python3 -c "
import json,sys
print(json.dumps({
    'cmd': sys.argv[1],
    'stdout': sys.argv[2],
    'stderr': sys.argv[3],
    'code': int(sys.argv[4])
}))" "$cmd" "$stdout_val" "$stderr_val" "$code")

        curl -s --connect-timeout 5 -X POST \
            -H "Content-Type: application/json" \
            -d "$payload" \
            "${URL}/result" >/dev/null 2>&1
    fi

    sleep "$INTERVAL"
done
