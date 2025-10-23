# 🎯 阿里云百炼模型微调 - 完整指南

## 📦 项目结构

```
LoRAT1/
├── .env                          # 配置文件（已更新）
├── requirements.txt              # Python 依赖
├── datasets/
│   ├── MedQA/                   # 原始数据集
│   └── MedQA_BaiLian/           # 转换后的数据集
├── 数据处理/
│   ├── batch_convert.py         # 批量转换脚本
│   ├── convert_to_bailian_format.py  # 单文件转换脚本
│   └── fine_tune_automation.py  # 微调自动化脚本 ⭐
└── doc/
    ├── 快速开始-微调流程.md      # 快速开始指南 ⭐
    └── 百炼微调使用指南.md       # 详细使用指南
```

## 🚀 快速开始（3步完成微调）

### Step 1: 安装依赖

```bash
pip install -r requirements.txt
```

### Step 2: 转换数据格式（如果还没转换）

```bash
cd 数据处理
python batch_convert.py
```

### Step 3: 运行自动化微调

```bash
python fine_tune_automation.py --auto
```

就这么简单！脚本会自动完成：
- ✅ 上传文件
- ✅ 创建微调任务
- ✅ 监控训练进度
- ✅ 更新配置文件

## 📋 .env 配置说明

### 当前已配置项

```bash
# ✅ 已配置
DASHSCOPE_API_KEY="sk-1c720921b5694dd5ad1ec8258d121039"
DASHSCOPE_MODEL_NAME=qwen-plus

# ✅ 已添加（默认值）
FINE_TUNE_BASE_MODEL=qwen2.5-7b-instruct
TRAINING_TYPE=efficient_sft
N_EPOCHS=3
BATCH_SIZE=16
LEARNING_RATE=1e-4
LORA_RANK=64
TARGET_MODULES=ALL
MAX_LENGTH=2048
```

### 需要运行时填写（自动化脚本会自动填写）

```bash
# ⏳ 运行时自动填写
TRAIN_FILE_ID=          # 上传训练文件后获得
VALIDATION_FILE_ID=     # 上传验证文件后获得
FINE_TUNE_JOB_ID=       # 创建微调任务后获得
FINE_TUNED_MODEL_ID=    # 训练完成后获得
```

## 🎨 微调流程图

```
┌─────────────────────────────────────────────────────────────┐
│  1. 数据准备                                                 │
│  ├─ batch_convert.py                                        │
│  └─ 输出: datasets/MedQA_BaiLian/*.jsonl                    │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  2. 上传文件到百炼平台                                       │
│  ├─ fine_tune_automation.py --upload                        │
│  └─ 获得: TRAIN_FILE_ID, VALIDATION_FILE_ID                 │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  3. 创建微调任务                                             │
│  ├─ fine_tune_automation.py --create                        │
│  └─ 获得: FINE_TUNE_JOB_ID                                  │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  4. 监控训练进度                                             │
│  ├─ fine_tune_automation.py --monitor <job_id>              │
│  └─ 状态: PENDING → RUNNING → SUCCEEDED                     │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  5. 部署模型（在控制台）                                     │
│  ├─ https://bailian.console.aliyun.com/                     │
│  └─ 获得: FINE_TUNED_MODEL_ID                               │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  6. 测试和使用                                               │
│  ├─ fine_tune_automation.py --test <model_id>               │
│  └─ 在应用中调用微调后的模型                                │
└─────────────────────────────────────────────────────────────┘
```

## 🛠️ 使用示例

### 示例 1: 自动化完整流程（推荐）

```bash
cd 数据处理

# 一键完成所有步骤
python fine_tune_automation.py --auto
```

### 示例 2: 分步骤执行

```bash
cd 数据处理

# 步骤 1: 上传文件
python fine_tune_automation.py --upload
# 选择: 1 (mainland_4opt_train.jsonl)
# 选择: 2 (mainland_4opt_dev.jsonl)

# 步骤 2: 创建任务（使用 .env 中的 file_id）
python fine_tune_automation.py --create

# 步骤 3: 监控进度
python fine_tune_automation.py --monitor ft-xxxxx

# 步骤 4: 测试模型（训练完成后）
python fine_tune_automation.py --test qwen-xxxxx
```

### 示例 3: 使用命令行工具

```bash
# 设置 API Key（Windows PowerShell）
$env:DASHSCOPE_API_KEY="sk-1c720921b5694dd5ad1ec8258d121039"

# 上传文件
dashscope files.upload -f "../datasets/MedQA_BaiLian/mainland_4opt_train.jsonl" -p fine_tune -d "训练集"

# 创建微调任务（LoRA）
dashscope fine_tunes.call \
  -m qwen2.5-7b-instruct \
  -t '<file_id>' \
  --mode efficient_sft \
  -e 3 -l 1e-4 \
  --hyper_parameters "lora_rank=64 target_modules=ALL"

# 查看任务状态
dashscope fine_tunes.get -j '<job_id>'
```

## 📊 数据集说明

项目包含 3 个地区的医学选择题数据：

| 数据集 | 训练集 | 验证集 | 测试集 | 推荐用途 |
|--------|--------|--------|--------|----------|
| **中国大陆** | mainland_4opt_train.jsonl | mainland_4opt_dev.jsonl | mainland_4opt_test.jsonl | ⭐ 中文医学问答 |
| **台湾** | taiwan_train.jsonl | taiwan_dev.jsonl | taiwan_test.jsonl | 繁体中文 |
| **美国** | us_4opt_train.jsonl | us_4opt_dev.jsonl | us_4opt_test.jsonl | 英文医学问答 |

**推荐：** 首次训练使用 `mainland_4opt` 系列数据集。

## ⚙️ 配置选项说明

### 基础模型选择

| 模型 | 代码 | 参数量 | 适用场景 | 性价比 |
|------|------|--------|----------|--------|
| 通义千问 2.5-7B | `qwen2.5-7b-instruct` | 7B | 快速测试、小数据集 | ⭐⭐⭐⭐⭐ |
| 通义千问 2.5-14B | `qwen2.5-14b-instruct` | 14B | 平衡性能和成本 | ⭐⭐⭐⭐ |
| 通义千问 2.5-32B | `qwen2.5-32b-instruct` | 32B | 最佳效果 | ⭐⭐⭐ |

### 训练类型选择

| 类型 | 代码 | 特点 | 训练时间 | 成本 | 推荐度 |
|------|------|------|----------|------|--------|
| **LoRA 微调** | `efficient_sft` | 快速、低成本 | 短 | 低 | ⭐⭐⭐⭐⭐ |
| **全参数微调** | `sft` | 效果最好 | 长 | 高 | ⭐⭐⭐ |

### 超参数调整建议

#### 数据量 < 10,000 条

```bash
N_EPOCHS=3-5          # 多循环几次
LEARNING_RATE=1e-4    # LoRA 推荐学习率
MAX_LENGTH=2048       # 标准长度
```

#### 数据量 > 10,000 条

```bash
N_EPOCHS=1-2          # 减少循环次数
LEARNING_RATE=1e-4    # LoRA 推荐学习率
MAX_LENGTH=4096       # 支持更长文本
```

## 💰 成本估算

### mainland_4opt_train.jsonl 示例

```
数据量: ~10,000 条
平均长度: ~200 tokens/条
训练类型: efficient_sft (LoRA)
循环次数: 3 次

计算:
总 tokens = 10,000 × 200 × 3 = 6,000,000 tokens

预估费用:
训练费用: ~12 元
部署费用: 按调用量计费
```

**节省成本建议：**
1. 使用 `efficient_sft`（LoRA）而不是 `sft`
2. 减少循环次数（但可能影响效果）
3. 使用较小的模型（如 7B 而不是 32B）
4. 先用小数据集测试，确认效果后再用完整数据

## 📖 文档导航

- 🚀 **[快速开始-微调流程.md](doc/快速开始-微调流程.md)** - 新手入门指南
- 📚 **[百炼微调使用指南.md](doc/百炼微调使用指南.md)** - 详细使用说明
- 🔧 **[模型调优与部署.md](阿里云百炼官方doc/模型调优与部署-使用%20API%20或命令行进行模型调优.md)** - 官方文档

## ❓ 常见问题 FAQ

### Q1: 我需要手动填写所有 .env 配置吗？

**A:** 不需要！使用 `fine_tune_automation.py --auto`，脚本会自动：
- ✅ 上传文件并获取 file_id
- ✅ 创建任务并获取 job_id
- ✅ 自动更新 .env 文件

你只需要在训练完成后，在控制台部署模型，并手动填写 `FINE_TUNED_MODEL_ID`。

### Q2: 文件超过 300MB 怎么办？

**A:** 百炼平台限制单文件 300MB。解决方法：
1. 分割数据为多个文件
2. 上传多个文件并在创建任务时指定多个 file_id

### Q3: 如何选择训练类型？

**A:** 推荐决策流程：
```
首次尝试？ → efficient_sft
数据量 < 50,000？ → efficient_sft
追求最佳效果且预算充足？ → sft
```

### Q4: 训练失败了怎么办？

**A:** 检查以下几点：
1. 数据格式是否正确（JSON 格式）
2. 文件大小是否超限（< 300MB）
3. 查看控制台的详细错误日志
4. 确认 API Key 是否有效

### Q5: 如何评估模型效果？

**A:** 三种方法：
1. **训练曲线**：在控制台查看 Loss 和 Accuracy
2. **验证集评估**：使用 dev.jsonl 测试准确率
3. **人工测试**：使用 `--test` 命令实际测试

## 🎯 最佳实践

1. **首次训练建议**
   - 使用 1000-2000 条数据快速测试
   - 选择 `qwen2.5-7b-instruct` + `efficient_sft`
   - 验证流程和配置无误后，再用完整数据集

2. **数据质量优先**
   - 高质量的 1000 条 > 低质量的 10000 条
   - 确保数据格式正确
   - 使用单独的验证集

3. **成本控制**
   - 优先使用 LoRA（efficient_sft）
   - 从小模型开始测试
   - 根据效果决定是否升级

4. **效果优化**
   - 观察训练曲线，判断是否过拟合
   - 调整循环次数和学习率
   - 使用更大的模型或全参数训练

## 🔗 快速链接

- 🌐 [百炼控制台](https://bailian.console.aliyun.com/)
- 📘 [百炼官方文档](https://help.aliyun.com/zh/model-studio/)
- 💻 [API 文档](https://help.aliyun.com/zh/model-studio/developer-reference/fine-tune-api)
- 🎓 [DashScope SDK](https://help.aliyun.com/zh/model-studio/developer-reference/sdk-overview)

## 🆘 获取帮助

遇到问题？可以：

1. 查看 [百炼微调使用指南.md](doc/百炼微调使用指南.md)
2. 访问百炼控制台查看详细日志
3. 查阅官方文档
4. 提交阿里云工单

## 🎉 开始你的微调之旅！

```bash
# 只需一条命令，开始你的第一次模型微调
cd 数据处理
python fine_tune_automation.py --auto
```

祝训练顺利！🚀

