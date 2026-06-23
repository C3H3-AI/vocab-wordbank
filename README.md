# 📚 英语词汇词库大全 — Vocab WordBank

一站式英语词汇词库仓库，覆盖从小学到留学的全阶段考试词汇。
专为 **词力 (Lexi)** 智能词汇教练系统设计，可直接加载使用。

## 🎯 包含词库

| 级别 | 词库ID | 词数 | 来源 |
|------|--------|------|------|
| 📘 小学 | `primary` | 7,028 | 人教版同步 (lilinji) |
| 📗 初中 | `junior` | 1,987 | KyleBing |
| 📙 高考核心 3500 | `gaokao-3500` | 3,866 | 100个句子记完3500个高考单词 |
| 📙 24天突破高考词汇 | `gaokao-24days` | 2,528 | 高考大纲词汇 3500 |
| 📙 20天背完高考核心 | `gaokao-core-20days` | 2,411 | 高考核心词汇 |
| 📙 Michael高考词群 | `gaokao-michael` | 4,378 | 词群速记 |
| 📙 高中英语 | `senior` | 3,743 | KyleBing |
| 📕 大学四级 CET-4 | `cet4` | 4,543 | KyleBing |
| 📕 大学六级 CET-6 | `cet6` | 3,991 | KyleBing |
| 📕 考研英语 | `postgraduate` | 5,047 | KyleBing |
| 📕 TOEFL 托福 | `toefl` | 10,367 | KyleBing |
| 📕 SAT | `sat` | 4,464 | KyleBing |
| **合计** | **12 个词库** | **54,353** | |

## 📁 仓库结构

```
vocab-wordbank/
├── wordbanks/          # ✅ 构建好的词库 JSON 文件（可直接使用）
│   ├── index.json      # 词库索引
│   ├── primary.json    # 小学词汇
│   ├── junior.json     # 初中词汇
│   ├── senior.json     # 高中词汇
│   ├── gaokao-3500.json  # 高考核心 3500
│   ├── ...
│   ├── cet4.json       # 大学四级
│   ├── cet6.json       # 大学六级
│   ├── postgraduate.json # 考研英语
│   ├── toefl.json      # 托福
│   └── sat.json        # SAT
├── sources/            # 📦 原始词库文件
│   ├── kylebing/       # KyleBing TXT 格式
│   └── lilinji/        # lilinji XLSX 格式
├── scripts/            # 🔧 构建工具
│   └── build-wordbank.py # 全量构建脚本
└── README.md
```

## 🔧 如何使用

### 1. 直接在词力系统中使用

将 `wordbanks/` 目录下任意 JSON 文件的内容，复制到词力系统的 `vocab_data.json` 中作为新槽位。

### 2. 格式说明

每个词库 JSON 的格式：

```json
{
  "meta": {
    "id": "senior",
    "name": "高中英语词汇",
    "level": "高中",
    "total": 3743,
    "source": "KyleBing",
    "description": "高中英语词汇，覆盖高考大纲"
  },
  "words": [
    ["abandon", "[əˈbændən]", "v.", "放弃；遗弃；抛弃"],
    ["ability", "[əˈbɪləti]", "n.", "能力；才能；能耐"]
  ]
}
```

每条词汇：
| 位置 | 字段 | 说明 |
|------|------|------|
| [0] | `word` | 英文单词 |
| [1] | `phonetic` | 音标（可能为空） |
| [2] | `pos` | 词性（n./v./adj./adv.等） |
| [3] | `meaning` | 中文释义 |

### 3. 自行构建

```bash
# 安装依赖
pip install openpyxl

# 构建所有词库
python scripts/build-wordbank.py --all

# 仅构建 KyleBing 词库
python scripts/build-wordbank.py --source kylebing

# 仅构建 lilinji 词库（需要先下载 XLSX 文件到 sources/lilinji/）
python scripts/build-wordbank.py --source lilinji

# 列出可构建的源文件
python scripts/build-wordbank.py --list
```

## 📚 数据来源

- [KyleBing 英语词汇库](https://github.com/KyleBing/english-vocabulary) — 7 个分级 TXT 词库
- [lilinji/English](https://github.com/lilinji/English) — 320+ 个教材同步 XLSX 词库

## 🧠 配合词力 (Lexi) 使用

本仓库专为 **词力 (Lexi)** 词汇教练系统配套设计：

- **间隔重复**：基于艾宾浩斯遗忘曲线（1/2/4/7/15/30 天复习）
- **三种练习模式**：跟打、复习、默写
- **错词管理**：自动记录错词，强化复习
- **进度追踪**：每日学习统计，预估完成时间

## 📄 许可

MIT License — 数据源自公开开源项目，仅供学习使用。
