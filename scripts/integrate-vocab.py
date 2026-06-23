#!/usr/bin/env python3
"""将新词库整合到词力系统的 vocab_data.json"""

import json

# 路径
VOCAB_FILE = r"D:\ai-hub\vocab-data\vocab_data.json"
WORD_BANK_DIR = r"D:\ai-hub\vocab-wordbank\wordbanks"
OUTPUT_FILE = r"D:\ai-hub\vocab-data\vocab_integrated.json"

# 加载现有词库
with open(VOCAB_FILE, "r", encoding="utf-8") as f:
    vocab = json.load(f)

# 找到最大槽位
max_slot = max(int(k) for k in vocab.keys()) if vocab else 0
print(f"当前最大槽位: #{max_slot}")

# 要添加的新词库
new_banks = [
    ("primary", "小学英语词汇（人教版同步）"),
    ("senior", "高中英语词汇"),
    ("cet4", "大学四级 CET-4"),
    ("cet6", "大学六级 CET-6"),
    ("postgraduate", "考研英语"),
    ("toefl", "托福 TOEFL"),
    ("sat", "SAT"),
    ("gaokao-3500", "高考核心 3500 词"),
    ("gaokao-24days", "24天突破高考词汇"),
    ("gaokao-core-20days", "20天背完高考核心词汇"),
    ("gaokao-michael", "Michael高考词群速记"),
]

integrated = dict(vocab)  # 复制现有

slot = max_slot + 1
for bank_id, bank_name in new_banks:
    bank_path = f"{WORD_BANK_DIR}/{bank_id}.json"
    try:
        with open(bank_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        words = data["words"]
        integrated[str(slot)] = words
        print(f"  #{slot} ({bank_name}): {len(words)} 词")
        slot += 1
    except Exception as e:
        print(f"  失败 {bank_id}: {e}")

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(integrated, f, ensure_ascii=False, indent=2)

total = sum(len(v) for v in integrated.values())
print(f"\n总计: {len(integrated)} 个槽位, {total:,} 个单词")
print(f"保存到: {OUTPUT_FILE}")
