# 百炼平台微调工具包

本工具包帮助你将 MedQA 医学选择题数据集转换为阿里云百炼平台所需的格式，并提供便捷的上传和微调功能。

## 📁 文件说明

| 文件 | 说明 |
|------|------|
| `convert_to_bailian_format.py` | 单文件转换脚本，支持命令行参数 |
| `batch_convert.py` | 批量转换所有 MedQA 数据集 |
| `quick_start.py` | 交互式快速开始脚本（推荐新手使用）|
| `百炼微调使用指南.md` | 详细的使用文档和最佳实践 |

## 🚀 快速开始

### 方式一：交互式脚本（推荐）

```bash
python quick_start.py
```

脚本会引导你完成：
1. ✅ 数据格式转换
2. ✅ API Key 配置
3. ✅ 文件上传
4. ✅ 创建微调任务

### 方式二：手动执行

#### 1. 安装依赖

```bash
pip install dashscope
```

#### 2. 转换数据

**批量转换所有数据集：**
```bash
python batch_convert.py
```

**单个文件转换：**
```bash
python convert_to_bailian_format.py datasets/MedQA/questions/Mainland/4_options/train.jsonl datasets/MedQA_BaiLian/train.jsonl
```

#### 3. 配置 API Key

```bash
# Windows PowerShell
$env:DASHSCOPE_API_KEY="your-api-key-here"

# Windows CMD
set DASHSCOPE_API_KEY=your-api-key-here

# Linux/Mac
export DASHSCOPE_API_KEY="your-api-key-here"
```

#### 4. 上传文件

```bash
dashscope files.upload -f "datasets/MedQA_BaiLian/mainland_4opt_train.jsonl" -p fine_tune -d "训练集"
dashscope files.upload -f "datasets/MedQA_BaiLian/mainland_4opt_dev.jsonl" -p fine_tune -d "验证集"
```

记录返回的 `file_id`。

#### 5. 创建微调任务

**推荐配置（LoRA 高效训练）：**
```bash
dashscope fine_tunes.call \
  -m qwen2.5-7b-instruct \
  -t '<训练集file_id>' \
  -v '<验证集file_id>' \
  --mode efficient_sft \
  -b 16 \
  -e 3 \
  -l 1e-4 \
  --hyper_parameters "lora_rank=64 target_modules=ALL max_length=2048"
```

#### 6. 查看训练状态

```bash
# 查看特定任务
dashscope fine_tunes.get -j '<job_id>'

# 查看所有任务
dashscope fine_tunes.list

# 或访问控制台
# https://bailian.console.aliyun.com/
```

## 📊 数据格式

### 原始格式 (MedQA)

```json
{
    "question": "卧位腰椎穿刺，脑脊液压力正常值是（　　）。",
    "options": {
        "A": "80～180mmH2O（0.78～1.76kPa）",
        "B": "50～70mmH2O（0.49～0.69kPa）",
        "C": "230～250mmH2O（2.25～2.45kPa）",
        "D": "260～280mmH2O（2.55～2.74kPa）"
    },
    "answer": "80～180mmH2O（0.78～1.76kPa）",
    "answer_idx": "A"
}
```

### 百炼 SFT 格式

```json
{
    "messages": [
        {
            "role": "system",
            "content": "你是一个专业的医学助手，擅长回答医学选择题。请根据题目和选项，给出正确答案。"
        },
        {
            "role": "user",
            "content": "卧位腰椎穿刺，脑脊液压力正常值是（　　）。\n\n选项：\nA. 80～180mmH2O（0.78～1.76kPa）\nB. 50～70mmH2O（0.49～0.69kPa）\nC. 230～250mmH2O（2.25～2.45kPa）\nD. 260～280mmH2O（2.55～2.74kPa）"
        },
        {
            "role": "assistant",
            "content": "答案是 A. 80～180mmH2O（0.78～1.76kPa）"
        }
    ]
}
```

## 🎯 可用数据集

转换后的数据集会保存在 `datasets/MedQA_BaiLian/` 目录：

| 文件 | 来源 | 说明 |
|------|------|------|
| `mainland_4opt_train.jsonl` | Mainland/4_options/train.jsonl | 中国大陆训练集 |
| `mainland_4opt_dev.jsonl` | Mainland/4_options/dev.jsonl | 中国大陆验证集 |
| `mainland_4opt_test.jsonl` | Mainland/4_options/test.jsonl | 中国大陆测试集 |
| `taiwan_train.jsonl` | Taiwan/train.jsonl | 台湾训练集 |
| `taiwan_dev.jsonl` | Taiwan/dev.jsonl | 台湾验证集 |
| `taiwan_test.jsonl` | Taiwan/test.jsonl | 台湾测试集 |
| `us_4opt_train.jsonl` | US/4_options/... | 美国训练集 |
| `us_4opt_dev.jsonl` | US/4_options/... | 美国验证集 |
| `us_4opt_test.jsonl` | US/4_options/... | 美国测试集 |

## ⚙️ 推荐配置

### 模型选择

| 模型 | 代码 | 适用场景 |
|------|------|----------|
| 通义千问 2.5-7B | `qwen2.5-7b-instruct` | ⭐ 平衡性能和成本（推荐）|
| 通义千问 2.5-14B | `qwen2.5-14b-instruct` | 更好的效果 |
| 通义千问 2.5-32B | `qwen2.5-32b-instruct` | 最佳效果（成本较高）|

### 训练类型

| 类型 | 代码 | 特点 |
|------|------|------|
| LoRA 高效训练 | `efficient_sft` | ⭐ 推荐：快速、低成本、效果好 |
| 全参数训练 | `sft` | 大数据量时使用 |

### 超参数（LoRA）

```json
{
    "n_epochs": 3,
    "batch_size": 16,
    "learning_rate": "1e-4",
    "lora_rank": 64,
    "target_modules": "ALL",
    "max_length": 2048
}
```

## 💰 成本估算

以 10,000 条训练数据为例：

```
训练数据: 10,000 条
平均每条: 200 tokens
循环次数: 3
总 tokens: 10,000 × 200 × 3 = 6,000,000
预估费用: ~12 元（按 0.002 元/千token 计算）
```

**注意：** 实际费用以平台显示为准，部署费用另计。

## 📖 常用命令

```bash
# 文件管理
dashscope files.list              # 列出所有文件
dashscope files.get -f <file_id>  # 查看文件详情
dashscope files.delete -f <file_id>  # 删除文件

# 微调任务
dashscope fine_tunes.list         # 列出所有任务
dashscope fine_tunes.get -j <job_id>  # 查看任务详情
dashscope fine_tunes.cancel -j <job_id>  # 取消任务

# 模型部署（在控制台完成）
# https://bailian.console.aliyun.com/
```

## ❓ 常见问题

### Q: 文件超过 300MB 怎么办？

A: 百炼平台限制单文件 300MB。可以：
1. 分割数据为多个文件
2. 上传时指定多个 `training_file_ids`

```bash
# 上传多个文件
dashscope files.upload -f "train_part1.jsonl" -p fine_tune
dashscope files.upload -f "train_part2.jsonl" -p fine_tune

# 创建任务时使用多个文件
dashscope fine_tunes.call -m qwen2.5-7b-instruct -t '<file_id1>' '<file_id2>' --mode efficient_sft
```

### Q: 应该用多少数据？

A: 推荐：
- 最少：1,000 条
- 适中：5,000-10,000 条
- 大规模：10,000+ 条（考虑减少循环次数）

### Q: 如何评估模型效果？

A: 
1. 查看训练曲线（loss、accuracy）
2. 使用验证集/测试集评估
3. 人工评测实际输出质量

### Q: 训练需要多长时间？

A: 取决于：
- 数据量
- 模型大小
- 循环次数
- 训练类型（LoRA 更快）

一般：1,000 条数据，LoRA 训练约 10-30 分钟。

## 📚 更多资料

- [详细使用指南](./百炼微调使用指南.md)
- [百炼平台官方文档](https://help.aliyun.com/zh/model-studio/)
- [模型微调 API 文档](https://help.aliyun.com/zh/model-studio/developer-reference/fine-tune-api)

## 🔧 技术支持

如遇到问题：
1. 查看 `百炼微调使用指南.md` 获取详细说明
2. 检查百炼平台控制台的错误日志
3. 访问阿里云工单系统
4. 查阅官方文档

---

**祝你训练顺利！** 🎉

