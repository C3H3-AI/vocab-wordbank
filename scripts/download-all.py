#!/usr/bin/env python3
"""
批量下载 lilinji/English 全部词库文件 (678 个 XLSX)
使用 requests 库，支持中文 URL
"""

import json, os, sys, time, subprocess
from pathlib import Path

INDEX_FILE = r"D:\ai-hub\vocab-data\lilinji_index.json"
SOURCE_DIR = r"D:\ai-hub\vocab-wordbank\sources\lilinji"
BUILD_SCRIPT = r"D:\ai-hub\vocab-wordbank\scripts\build-wordbank.py"
PYTHON = r"C:\Users\duola\.workbuddy\binaries\python\versions\3.13.12\python.exe"

def extract_files(index_data):
    """从索引 JSON 中提取所有文件信息"""
    files = []
    for category, subcats in index_data.items():
        if isinstance(subcats, dict):
            for subcat, info in subcats.items():
                if isinstance(info, dict) and 'files' in info:
                    for fi in info['files']:
                        files.append({
                            'name': fi['name'],
                            'size': fi['size'],
                            'url': fi['download_url'],
                            'category': f"{category}/{subcat}"
                        })
                elif isinstance(info, list):
                    for fi in info:
                        files.append({
                            'name': fi['name'],
                            'size': fi['size'],
                            'url': fi['download_url'],
                            'category': f"{category}/{subcat}"
                        })
        elif isinstance(subcats, list):
            for fi in subcats:
                files.append({
                    'name': fi['name'],
                    'size': fi['size'],
                    'url': fi['download_url'],
                    'category': category
                })
    return files

def main():
    os.makedirs(SOURCE_DIR, exist_ok=True)
    
    # 加载索引
    print("📖 加载索引...")
    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        index_data = json.load(f)
    
    all_files = extract_files(index_data)
    print(f"  共 {len(all_files)} 个文件\n")
    
    # 分类统计
    categories = {}
    for fi in all_files:
        cat = fi['category']
        if cat not in categories:
            categories[cat] = {'count': 0, 'size': 0}
        categories[cat]['count'] += 1
        categories[cat]['size'] += fi['size']
    
    print("📂 文件分布:")
    for cat, info in sorted(categories.items()):
        print(f"  {cat}: {info['count']} 个文件 ({info['size']/1024:.0f} KB)")
    print()
    
    # 检查已下载
    existing_xlsx = {f for f in os.listdir(SOURCE_DIR) if f.endswith('.xlsx') and not f.startswith('_')}
    to_download = [fi for fi in all_files if fi['name'] not in existing_xlsx]
    
    # 去掉已存在且大小匹配的
    still_needed = []
    for fi in to_download:
        dest_path = os.path.join(SOURCE_DIR, fi['name'])
        if os.path.exists(dest_path):
            actual_size = os.path.getsize(dest_path)
            if actual_size == fi['size']:
                continue  # 已存在且大小一致
        still_needed.append(fi)
    to_download = still_needed
    
    if not to_download:
        print("✅ 全部文件已下载完毕（已验证）")
    else:
        total_size_mb = sum(fi['size'] for fi in to_download) / 1024 / 1024
        print(f"⬇️ 还需下载 {len(to_download)} 个文件 (共 {total_size_mb:.1f} MB)")
        
        # 先生成批量下载清单，传给 curl
        url_list_file = os.path.join(SOURCE_DIR, '_download_list.txt')
        with open(url_list_file, 'w', encoding='utf-8') as f:
            for fi in to_download:
                dest_path = os.path.join(SOURCE_DIR, fi['name'])
                f.write(f"{fi['url']}\t{dest_path}\n")
        
        # 用 PowerShell 逐行下载（原生支持中文 URL）
        ps_script = os.path.join(SOURCE_DIR, '_download.ps1')
        with open(ps_script, 'w', encoding='utf-8') as f:
            f.write('$ProgressPreference = "SilentlyContinue"\n')
            f.write(f'$listFile = "{url_list_file}"\n')
            f.write('$lines = Get-Content $listFile -Encoding UTF8\n')
            f.write('$total = $lines.Count\n')
            f.write('$success = 0; $failed = 0; $i = 0\n')
            f.write('foreach ($line in $lines) {\n')
            f.write('    $parts = $line -split "`t", 2\n')
            f.write('    $url = $parts[0]\n')
            f.write('    $dest = $parts[1]\n')
            f.write('    $filename = [System.IO.Path]::GetFileName($dest)\n')
            f.write('    $i++\n')
            f.write('    if (Test-Path $dest) {\n')
            f.write('        $success++; continue\n')
            f.write('    }\n')
            f.write('    Write-Host "  [→] ($i/$total) $filename"\n')
            f.write('    try {\n')
            f.write('        Invoke-WebRequest -Uri $url -OutFile $dest -TimeoutSec 30 -ErrorAction Stop | Out-Null\n')
            f.write('        $success++\n')
            f.write('    } catch {\n')
            f.write('        Write-Host "    ✗ 失败: $filename - $_"\n')
            f.write('        $failed++\n')
            f.write('    }\n')
            f.write('    if ($i % 50 -eq 0 -or $i -eq $total) {\n')
            f.write('        $pct = [math]::Round($i / $total * 100)\n')
            f.write('        Write-Host "  进度: $i/$total ($pct%) | ✅ $success | ❌ $failed"\n')
            f.write('    }\n')
            f.write('    Start-Sleep -Milliseconds 100\n')
            f.write('}\n')
            f.write('Write-Host "`n" + "="*50\n')
            f.write('Write-Host "✅ 成功: $success"\n')
            f.write('Write-Host "❌ 失败: $failed"\n')
        
        print(f"\n🚀 使用 PowerShell 批量下载...")
        result = subprocess.run([
            'powershell.exe', '-ExecutionPolicy', 'Bypass', '-File', ps_script
        ], capture_output=False, text=True)
        
        # 清理临时文件
        for tmp in [url_list_file, ps_script]:
            try:
                os.remove(tmp)
            except:
                pass
    
    # 最终统计
    final_xlsx = [f for f in os.listdir(SOURCE_DIR) if f.endswith('.xlsx') and not f.startswith('_')]
    final_size = sum(os.path.getsize(os.path.join(SOURCE_DIR, f)) for f in final_xlsx)
    print(f"\n📊 最终: {len(final_xlsx)} 个 XLSX 文件, {final_size/1024/1024:.1f} MB")
    
    # 自动运行构建脚本
    print(f"\n🔨 自动运行构建脚本...")
    subprocess.run([PYTHON, BUILD_SCRIPT, '--all'])

if __name__ == '__main__':
    main()
