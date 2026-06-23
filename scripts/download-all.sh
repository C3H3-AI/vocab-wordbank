#!/bin/bash
# 批量下载 lilinji/English 全部词库文件
# 使用 curl 直接下载，支持中文 URL

INDEX_FILE="D:/ai-hub/vocab-data/lilinji_index.json"
SOURCE_DIR="D:/ai-hub/vocab-wordbank/sources/lilinji"
BUILD_SCRIPT="D:/ai-hub/vocab-wordbank/scripts/build-wordbank.py"
PYTHON="/c/Users/duola/.workbuddy/binaries/python/versions/3.13.12/python.exe"

mkdir -p "$SOURCE_DIR"

# 从 lilinji_index.json 提取所有下载 URL（用 Python 生成 URL 列表）
"$PYTHON" -c "
import json
idx = json.load(open('$INDEX_FILE', 'r', encoding='utf-8'))
files = []
for cat, subcats in idx.items():
    if isinstance(subcats, dict):
        for subcat, info in subcats.items():
            if isinstance(info, dict) and 'files' in info:
                for fi in info['files']:
                    files.append(fi)
            elif isinstance(info, list):
                for fi in info:
                    files.append(fi)
    elif isinstance(subcats, list):
        for fi in subcats:
            files.append(fi)

# 输出为 JSON lines
for fi in files:
    print(json.dumps(fi, ensure_ascii=False))
" > /tmp/lilinji_files.jsonl 2>&1

TOTAL=$(wc -l < /tmp/lilinji_files.jsonl)
echo "📖 共 $TOTAL 个文件"

# 分批下载
SUCCESS=0
FAILED=0
COUNT=0

while IFS= read -r line; do
    NAME=$(echo "$line" | "$PYTHON" -c "import sys,json; print(json.load(sys.stdin)['name'])")
    URL=$(echo "$line" | "$PYTHON" -c "import sys,json; print(json.load(sys.stdin)['download_url'])")
    SIZE=$(echo "$line" | "$PYTHON" -c "import sys,json; print(json.load(sys.stdin)['size'])")
    
    COUNT=$((COUNT + 1))
    DEST="$SOURCE_DIR/$NAME"
    
    # 检查是否已存在
    if [ -f "$DEST" ]; then
        ACTUAL_SIZE=$(stat -c%s "$DEST" 2>/dev/null || echo "0")
        if [ "$ACTUAL_SIZE" = "$SIZE" ]; then
            SUCCESS=$((SUCCESS + 1))
            printf "\r  [✓] %3d/%d 已存在" $COUNT $TOTAL
            continue
        fi
    fi
    
    printf "\r  [→] %3d/%d %s" $COUNT $TOTAL "$NAME"
    
    # 用 curl 下载（支持中文 URL）
    if curl -sL --max-time 60 "$URL" -o "$DEST" 2>/dev/null; then
        SUCCESS=$((SUCCESS + 1))
    else
        FAILED=$((FAILED + 1))
        echo ""
        echo "    ✗ 失败: $NAME"
    fi
    
    sleep 0.2
    
    # 每 20 个文件显示进度详情
    if [ $((COUNT % 20)) -eq 0 ]; then
        PCT=$((COUNT * 100 / TOTAL))
        echo ""
        echo "  进度: $COUNT/$TOTAL ($PCT%) | ✅ $SUCCESS | ❌ $FAILED"
    fi
done < /tmp/lilinji_files.jsonl

echo ""
echo "=================================================="
echo "✅ 成功: $SUCCESS"
echo "❌ 失败: $FAILED"

# 最终统计
FINAL_COUNT=$(ls "$SOURCE_DIR"/*.xlsx 2>/dev/null | wc -l)
FINAL_SIZE=$(du -sm "$SOURCE_DIR" 2>/dev/null | cut -f1)
echo "📊 最终: $FINAL_COUNT 个 XLSX 文件, ${FINAL_SIZE:-0} MB"

# 自动运行构建
echo ""
echo "🔨 自动运行构建脚本..."
"$PYTHON" "$BUILD_SCRIPT" --all
