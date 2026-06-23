#!/usr/bin/env python3
"""
词库全量构建脚本 — Build Wordbank

将 KyleBing TXT 和 lilinji XLSX 源文件批量转换为词力(Lexi)系统兼容的 JSON 格式。
输出文件按词库级别分类，可直接被词汇教练系统加载。

使用方法:
  python3 build-wordbank.py --all              # 构建所有词库
  python3 build-wordbank.py --list             # 列出可构建的词库
  python3 build-wordbank.py --source kylebing  # 仅构建 KyleBing 词库
  python3 build-wordbank.py --source lilinji   # 仅构建 lilinji 词库

输出格式:
  wordbanks/
    index.json          # 词库索引（描述所有可用词库）
    01-primary.json     # 小学
    02-junior.json      # 初中
    03-senior.json      # 高中 / 高考高频
    04-cet4.json        # 大学四级
    05-cet6.json        # 大学六级
    06-postgraduate.json # 考研英语
    07-ielts.json       # 雅思
    08-toefl.json       # 托福
    09-sat.json         # SAT
    10-gaokao-3500.json # 高考核心 3500 词
    ...

JSON 格式 (每个词库文件):
  {
    "meta": {
      "id": "senior",
      "name": "高中英语词汇",
      "level": "高中",
      "total": 6008,
      "source": "KyleBing",
      "description": "高中英语词汇，共 6008 词"
    },
    "words": [
      ["word", "[ˈfəʊnətɪk]", "v./n.", "释义"],
      ...
    ]
  }
"""

import json, os, sys, re, argparse
from pathlib import Path

# ============================================================
# 路径定义
# ============================================================
REPO_ROOT = Path(__file__).resolve().parent.parent
SOURCES_DIR = REPO_ROOT / 'sources'
KYLEBING_DIR = SOURCES_DIR / 'kylebing'
LILINJI_DIR = SOURCES_DIR / 'lilinji'
OUTPUT_DIR = REPO_ROOT / 'wordbanks'

# ============================================================
# 释义解析
# ============================================================
POS_PATTERN = re.compile(r'^([a-zA-Z,;/\s]+)\.\s*(.*)')

def parse_translation(text):
    """解析释义文本，返回 (pos, meaning)"""
    if not text:
        return ('', text or '')
    text = text.strip()
    m = POS_PATTERN.match(text)
    if m:
        pos = m.group(1).strip()
        meaning = m.group(2).strip()
        return (pos, meaning)
    return ('', text)

# ============================================================
# KyleBing TXT 解析
# ============================================================
def parse_kylebing_txt(filepath):
    """解析 KyleBing TXT 行: word\tn. 释义"""
    words = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split('\t', 1)
            if len(parts) < 2:
                continue
            word = parts[0].strip()
            trans_text = parts[1].strip()
            pos, meaning = parse_translation(trans_text)
            words.append([word, '', pos, meaning])
    return words

# ============================================================
# lilinji XLSX 解析
# ============================================================
def parse_xlsx(filepath):
    """解析 lilinji XLSX 格式: 列1=单词, 列2=英音, 列3=美音, 列4=释义"""
    import openpyxl
    wb = openpyxl.load_workbook(filepath, read_only=True)
    ws = wb.active
    
    words = []
    for row in ws.iter_rows(values_only=True):
        if not row or not row[0]:
            continue
        word = str(row[0]).strip()
        if not word:
            continue
        # 音标: 优先英音，其次美音
        phonetic = ''
        if len(row) > 1 and row[1]:
            phonetic = str(row[1]).strip()
        elif len(row) > 2 and row[2]:
            phonetic = str(row[2]).strip()
        # 释义
        trans_text = ''
        if len(row) > 3 and row[3]:
            trans_text = str(row[3]).strip()
        pos, meaning = parse_translation(trans_text)
        words.append([word, phonetic, pos, meaning])
    
    wb.close()
    return words

# ============================================================
# 词库定义
# ============================================================
# KyleBing 词库配置
KYLEBING_BOOKS = [
    {
        'id': 'primary',
        'name': '小学英语词汇',
        'level': '小学',
        'source_file': None,  # 由 lilinji 补充
    },
    {
        'id': 'junior',
        'name': '初中英语词汇',
        'level': '初中',
        'source_file': '1-初中.txt',
        'description': '初中英语词汇，覆盖中考大纲',
    },
    {
        'id': 'senior',
        'name': '高中英语词汇',
        'level': '高中',
        'source_file': '2-高中.txt',
        'description': '高中英语词汇，覆盖高考大纲',
    },
    {
        'id': 'cet4',
        'name': '大学英语四级词汇 (CET-4)',
        'level': '大学四级',
        'source_file': '3-四级.txt',
        'description': '大学英语四级考试大纲词汇',
    },
    {
        'id': 'cet6',
        'name': '大学英语六级词汇 (CET-6)',
        'level': '大学六级',
        'source_file': '4-六级.txt',
        'description': '大学英语六级考试大纲词汇',
    },
    {
        'id': 'postgraduate',
        'name': '考研英语词汇',
        'level': '考研',
        'source_file': '5-考研.txt',
        'description': '全国硕士研究生入学考试英语词汇',
    },
    {
        'id': 'toefl',
        'name': 'TOEFL 托福词汇',
        'level': '托福',
        'source_file': '6-托福.txt',
        'description': '托福考试核心词汇',
    },
    {
        'id': 'sat',
        'name': 'SAT 词汇',
        'level': 'SAT',
        'source_file': '7-SAT.txt',
        'description': '美国高考 SAT 考试词汇',
    },
]

# lilinji 词库映射（文件名模式 → 词库 ID）
LILINJI_BOOKS = [
    {
        'id': 'gaokao-3500',
        'name': '高考核心 3500 词',
        'level': '高考',
        'pattern': '100个句子记完3500个高考单词',
        'description': '100个句子记忆高考核心 3500 词',
    },
    {
        'id': 'gaokao-24days',
        'name': '24天突破高考大纲词汇 3500',
        'level': '高考',
        'pattern': '24天突破高考大纲词汇3500 主词',
        'description': '24天突破高考大纲词汇 3500（主词）',
    },
    {
        'id': 'gaokao-core-20days',
        'name': '20天背完高考核心词汇',
        'level': '高考',
        'pattern': '20天背完高考核心词汇',
        'description': '20天背完高考核心词汇',
    },
    {
        'id': 'gaokao-michael',
        'name': 'Michael老师高考词汇（词群速记）',
        'level': '高考',
        'pattern': 'Michael老师高考词汇',
        'description': 'Michael老师高考词群速记词汇',
    },
]

# 小学人教版文件列表（自动发现）
PRIMARY_PUBLISHERS = ['人教版']

# ============================================================
# 主逻辑
# ============================================================
def build_kylebing_books():
    """构建所有 KyleBing 词库"""
    results = []
    for book in KYLEBING_BOOKS:
        if not book.get('source_file'):
            continue
        filepath = KYLEBING_DIR / book['source_file']
        if not filepath.exists():
            print(f"  ⚠ 文件不存在: {filepath}")
            continue
        
        words = parse_kylebing_txt(filepath)
        if not words:
            print(f"  ⚠ 空词库: {book['name']}")
            continue
        
        # 去重（保留首次出现）
        seen = set()
        deduped = []
        for w in words:
            key = w[0].lower()
            if key not in seen:
                seen.add(key)
                deduped.append(w)
        
        result = {
            'meta': {
                'id': book['id'],
                'name': book['name'],
                'level': book['level'],
                'total': len(deduped),
                'source': 'KyleBing',
                'description': book.get('description', ''),
            },
            'words': deduped
        }
        
        output_name = f"{book['id']}.json"
        filepath_out = OUTPUT_DIR / output_name
        
        with open(filepath_out, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"  ✓ {book['name']}: {len(deduped)} 词 → {output_name}")
        results.append(result)
    
    return results

def build_lilinji_books():
    """构建所有 lilinji 词库（小学 + 高考）"""
    results = []
    
    # 处理小学词库：扫描 lilinji 目录下的人教版文件
    primary_files = sorted(LILINJI_DIR.glob('*小学*年级*.xlsx'))
    if not primary_files:
        primary_files = sorted(LILINJI_DIR.glob('*.xlsx'))
    
    if primary_files:
        all_primary_words = []
        primary_sources = []
        
        for f in primary_files:
            try:
                words = parse_xlsx(f)
                if words:
                    all_primary_words.extend(words)
                    primary_sources.append(f.name)
                    print(f"  ✓ {f.name}: {len(words)} 词")
            except Exception as e:
                print(f"  ⚠ {f.name}: 解析失败 - {e}")
        
        if all_primary_words:
            # 去重
            seen = set()
            deduped = []
            for w in all_primary_words:
                key = w[0].lower()
                if key not in seen:
                    seen.add(key)
                    deduped.append(w)
            
            result = {
                'meta': {
                    'id': 'primary',
                    'name': '小学英语词汇（人教版同步）',
                    'level': '小学',
                    'total': len(deduped),
                    'source': 'lilinji',
                    'sources': primary_sources,
                    'description': f'人教版小学英语同步词汇，合并去重后共 {len(deduped)} 词',
                },
                'words': deduped
            }
            
            output_name = 'primary.json'
            with open(OUTPUT_DIR / output_name, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            print(f"\n  ✓ 小学词汇总计: {len(deduped)} 词 → {output_name}")
            results.append(result)
    
    # 处理高考词库：按文件名模式匹配
    gaokao_files = sorted(LILINJI_DIR.glob('*.xlsx'))
    
    for book in LILINJI_BOOKS:
        pattern = book['pattern']
        matched = [f for f in gaokao_files if pattern in f.stem]
        
        if not matched:
            # 尝试模糊匹配
            keywords = pattern.split(' ')[0]
            matched = [f for f in gaokao_files if keywords in f.stem]
        
        if not matched:
            print(f"  ⚠ 未找到匹配文件: {book['name']} (pattern: {pattern})")
            continue
        
        all_words = []
        sources = []
        for f in matched:
            try:
                words = parse_xlsx(f)
                if words:
                    all_words.extend(words)
                    sources.append(f.name)
                    print(f"  ✓ {f.name}: {len(words)} 词")
            except Exception as e:
                print(f"  ⚠ {f.name}: 解析失败 - {e}")
        
        if all_words:
            # 去重
            seen = set()
            deduped = []
            for w in all_words:
                key = w[0].lower()
                if key not in seen:
                    seen.add(key)
                    deduped.append(w)
            
            result = {
                'meta': {
                    'id': book['id'],
                    'name': book['name'],
                    'level': book['level'],
                    'total': len(deduped),
                    'source': 'lilinji',
                    'sources': sources,
                    'description': book['description'],
                },
                'words': deduped
            }
            
            clean_id = book['id']
            output_name = f"{clean_id}.json"
            with open(OUTPUT_DIR / output_name, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            print(f"  ✓ {book['name']}: {len(deduped)} 词 → {output_name}")
            results.append(result)
    
    return results

def build_index(results):
    """构建词库索引文件"""
    index = {
        'version': '2.0',
        'last_updated': '',
        'total_books': len(results),
        'total_words': sum(r['meta']['total'] for r in results),
        'books': sorted([r['meta'] for r in results], key=lambda x: x['id'])
    }
    
    with open(OUTPUT_DIR / 'index.json', 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*60}")
    print(f"📊 词库索引已生成: wordbanks/index.json")
    print(f"   词库数量: {index['total_books']}")
    print(f"   总词数:   {index['total_words']:,}")
    print(f"{'='*60}")
    
    print(f"\n{'词库ID':<20} {'名称':<30} {'词数':<8}")
    print(f"{'-'*60}")
    for book in index['books']:
        print(f"{book['id']:<20} {book['name']:<30} {book['total']:<8}")
    
    return index

def list_available():
    """列出可用的源文件"""
    print("=" * 60)
    print("📂 KyleBing 源文件:")
    for f in sorted(KYLEBING_DIR.glob('*.txt')):
        size = f.stat().st_size
        print(f"   {f.name} ({size/1024:.0f} KB)")
    
    print(f"\n📂 lilinji 源文件:")
    for f in sorted(LILINJI_DIR.glob('*.xlsx')):
        size = f.stat().st_size
        print(f"   {f.name} ({size/1024:.0f} KB)")
    
    print(f"\n📂 当前词库输出:")
    for f in sorted(OUTPUT_DIR.glob('*.json')):
        data = json.load(open(f, 'r', encoding='utf-8'))
        if 'meta' in data:
            print(f"   {f.name}: {data['meta']['name']} ({data['meta']['total']} 词)")

def main():
    parser = argparse.ArgumentParser(description='词库全量构建脚本')
    parser.add_argument('--all', action='store_true', help='构建所有词库')
    parser.add_argument('--list', action='store_true', help='列出可构建的词库')
    parser.add_argument('--source', choices=['kylebing', 'lilinji'], help='仅构建指定来源')
    args = parser.parse_args()
    
    if args.list:
        list_available()
        return
    
    print("🚀 开始构建词汇词库...\n")
    
    all_results = []
    
    # 构建 KyleBing 词库
    if args.all or args.source == 'kylebing':
        print("📗 KyleBing 词库:")
        results = build_kylebing_books()
        all_results.extend(results)
    
    # 构建 lilinji 词库
    if args.all or args.source == 'lilinji':
        print("\n📕 lilinji 词库:")
        results = build_lilinji_books()
        all_results.extend(results)
    
    # 构建索引
    if all_results:
        print("\n📊 生成词库索引...")
        index = build_index(all_results)
    else:
        print("⚠ 没有词库被构建")
    
    print("\n✅ 完成!")

if __name__ == '__main__':
    main()
