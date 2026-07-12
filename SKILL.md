---
name: qwen-vl
description: |
  图片/PDF 视觉识别 — 通过阿里云百炼 Qwen-VL 多模态 API 分析图片内容，将结果返回给主模型处理。
  解决 DeepSeek 等纯文本模型无法直接"看图"的问题。
  支持单图分析、批量截图、PDF页面截图和 OCR 文字提取。
  Use when: 需要分析论文截图、PDF 报告、GUI 界面、训练曲线图、架构图、
  或者任何主模型无法直接查看的图片/图表内容。
---

# Qwen-VL 视觉识别 Skill

你通过阿里云百炼平台的 Qwen-VL 多模态模型来"看图"，然后将文字描述交给主模型处理。

## 工具脚本

```
qwen_vl.py
```

## 配置 API Key

使用前需要在环境变量中配置阿里云百炼 DashScope API key：

```bash
export DASHSCOPE_API_KEY="your_api_key_here"
```

Windows PowerShell:

```powershell
$env:DASHSCOPE_API_KEY = "your_api_key_here"
```
## 使用方式

### 1. 单张图片分析（默认）

```bash
python qwen_vl.py "图片路径"
```

默认 prompt 会要求模型描述图片的布局、文字、图表、数据等所有可见信息。

### 2. 带自定义提问

```bash
python qwen_vl.py "图片路径" -p "这张图里的训练曲线说明了什么？"
```

### 3. OCR 文字提取

适合扫描件、PDF 截图中的文字识别：

```bash
python qwen_vl.py "图片路径" --ocr
```

### 4. 多图批量分析

```bash
python qwen_vl.py img1.png img2.png img3.png
```

### 5. 结果保存到文件

```bash
python qwen_vl.py "图片路径" -o result.txt
```

### 6. 切换模型

| 模型 | 参数 | 适用场景 |
|------|------|---------|
| `qwen3-vl-flash` | 默认 | 日常快速分析，便宜 |
| `qwen3-vl-plus` | `-m qwen3-vl-plus` | 复杂图表、需要深度理解 |
| `qwen-vl-ocr-latest` | `--ocr` | 纯文字识别 |

## 你的工作流

收到看图请求时：

1. **确认图片路径** — 如果用户提到了图片但没给路径，先让用户确认文件位置
2. **选择合适的模型和 prompt** — 根据任务类型选：
   - 描述图表 → 默认 prompt + `qwen3-vl-flash`
   - 识别文字 → `--ocr`
   - 理解复杂架构图 → `-m qwen3-vl-plus`
3. **执行脚本** — 用 Bash 工具运行，读回结果
4. **基于结果处理** — 你拿到 Qwen-VL 的文字描述后，结合上下文完成用户的实际任务

## 典型场景

- **论文图题核查**：OCR 提取论文截图中的图号和图题，判断正文是否引用
- **AIGC 检测报告**：识别 PDF 截图中的段落高亮、标注和检测概率
- **GUI 界面校验**：看系统截图确认界面布局是否与设计一致
- **训练曲线分析**：读 loss/accuracy 曲线图，用文字描述趋势
- **架构图理解**：分析系统架构框图，转换为文字描述

## 注意事项

- 支持的图片格式：PNG、JPG、GIF、WebP、BMP
- 图片大小建议不超过 10MB
- 一次调用可以传多张图片（最多 5 张）
- API key 从环境变量 `DASHSCOPE_API_KEY` 读取，不要把密钥写入脚本或提交到 GitHub