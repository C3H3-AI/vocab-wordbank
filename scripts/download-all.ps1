# 批量下载 lilinji/English 全部词库文件
param(
    [string]$IndexFile = "D:\ai-hub\vocab-data\lilinji_index.json",
    [string]$SourceDir = "D:\ai-hub\vocab-wordbank\sources\lilinji",
    [string]$BuildScript = "D:\ai-hub\vocab-wordbank\scripts\build-wordbank.py"
)

$ProgressPreference = 'SilentlyContinue'

# 读取索引
Write-Host "📖 加载索引..." -ForegroundColor Cyan
$index = Get-Content $IndexFile -Encoding UTF8 | ConvertFrom-Json

# 提取所有文件
$allFiles = @()
$index.PSObject.Properties | ForEach-Object {
    $category = $_.Name
    $value = $_.Value
    
    if ($value -is [System.Management.Automation.PSCustomObject]) {
        $value.PSObject.Properties | ForEach-Object {
            $subcat = $_.Name
            $subval = $_.Value
            if ($subval.files) {
                $subval.files | ForEach-Object {
                    $allFiles += [PSCustomObject]@{
                        Name = $_.name
                        Url = $_.download_url
                        Size = $_.size
                        Category = "$category/$subcat"
                    }
                }
            } elseif ($subval -is [System.Array]) {
                $subval | ForEach-Object {
                    $allFiles += [PSCustomObject]@{
                        Name = $_.name
                        Url = $_.download_url
                        Size = $_.size
                        Category = "$category/$subcat"
                    }
                }
            }
        }
    } elseif ($value -is [System.Array]) {
        $value | ForEach-Object {
            $allFiles += [PSCustomObject]@{
                Name = $_.name
                Url = $_.download_url
                Size = $_.size
                Category = $category
            }
        }
    }
}

Write-Host "  共 $($allFiles.Count) 个文件" -ForegroundColor Cyan

# 分类统计
$categories = $allFiles | Group-Object Category | Sort-Object Name
Write-Host "`n📂 文件分布:" -ForegroundColor Yellow
$categories | ForEach-Object { 
    $sizeKB = [math]::Round(($_.Group | Measure-Object Size -Sum).Sum / 1KB)
    Write-Host "  $($_.Name): $($_.Count) 个文件 ($sizeKB KB)"
}

# 检查已下载
if (-not (Test-Path $SourceDir)) { New-Item -ItemType Directory -Path $SourceDir -Force | Out-Null }
$existing = @(Get-ChildItem $SourceDir -Filter *.xlsx | ForEach-Object { $_.Name })
$toDownload = $allFiles | Where-Object { $_.Name -notin $existing }

if ($toDownload.Count -eq 0) {
    Write-Host "`n✅ 全部文件已下载完毕" -ForegroundColor Green
} else {
    $totalSizeMB = [math]::Round(($toDownload | Measure-Object Size -Sum).Sum / 1MB, 1)
    Write-Host "`n⬇️ 还需下载 $($toDownload.Count) 个文件 (共 $totalSizeMB MB)" -ForegroundColor Yellow
    
    $success = 0
    $failed = 0
    $batchSize = 10
    $total = $toDownload.Count
    $batches = [math]::Ceiling($total / $batchSize)
    
    $i = 0
    foreach ($fi in $toDownload) {
        $i++
        $dest = Join-Path $SourceDir $fi.Name
        
        # 检查是否已存在且大小匹配
        if ((Test-Path $dest) -and ((Get-Item $dest).Length -eq $fi.Size)) {
            Write-Host "  [✓] ($i/$total) $($fi.Name) (已存在)" -ForegroundColor DarkGray
            $success++
            continue
        }
        
        $sizeKB = [math]::Round($fi.Size / 1KB)
        Write-Host "  [→] ($i/$total) $($fi.Name) ($sizeKB KB)" -ForegroundColor Gray
        
        try {
            Invoke-WebRequest -Uri $fi.Url -OutFile $dest -TimeoutSec 60 -ErrorAction Stop
            $success++
        } catch {
            Write-Host "    ✗ 失败: $_" -ForegroundColor Red
            $failed++
            # 写失败标记
            "$($fi.Url)" | Out-File "$dest.failed" -Encoding UTF8
        }
        
        # 每批后显示进度
        if ($i % $batchSize -eq 0 -or $i -eq $total) {
            $pct = [math]::Round($i / $total * 100)
            Write-Host "  进度: $i/$total ($pct%) | ✅ $success | ❌ $failed" -ForegroundColor Cyan
        }
        
        Start-Sleep -Milliseconds 200
    }
    
    Write-Host "`n" + "=" * 50 -ForegroundColor Cyan
    Write-Host "✅ 成功: $success" -ForegroundColor Green
    Write-Host "❌ 失败: $failed" -ForegroundColor Red
}

# 最终统计
$finalXlsx = @(Get-ChildItem $SourceDir -Filter *.xlsx)
$finalSize = ($finalXlsx | Measure-Object Length -Sum).Sum
Write-Host "`n📊 最终: $($finalXlsx.Count) 个 XLSX 文件, $([math]::Round($finalSize/1MB, 1)) MB" -ForegroundColor Cyan

# 自动运行构建脚本
Write-Host "`n🔨 自动运行构建脚本..." -ForegroundColor Green
$python = "C:\Users\duola\.workbuddy\binaries\python\versions\3.13.12\python.exe"
& $python $BuildScript --all
