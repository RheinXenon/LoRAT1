使用 API 或命令行进行模型调优
本文档以通义千问模型的微调操作为例进行说明，使用命令行（Shell）和 API （HTTP）两种方式，帮助您使用阿里云百炼提供的模型微调功能。模型调优包含模型微调（SFT）、继续预训练（CPT）、模型偏好训练（DPO）三种模型训练方式。

重要
本文档仅适用于中国大陆版（北京地域）。

前提条件
您已经完整阅读了模型调优简介，熟悉如何在阿里云百炼平台进行模型微调的基本步骤，并掌握了微调数据集构建技巧。

已开通服务并获得API-KEY， 请参考获取API Key。

已导入 API-KEY，请参考配置API Key到环境变量。

（可选，仅 Shell 需要）已安装 DashScope SDK，请参考安装SDK。

上传训练文件
准备训练文件
CPT 训练集
CPT 纯文本格式训练数据，一行训练数据展开后结构如下：
{"text":"文本内容"}

SFT 训练集
SFT ChatML（Chat Markup Language）格式训练数据，支持多轮对话和多种角色设置，一行训练数据展开后结构如下：
{"messages": [
  {"role": "system", "content": "<系统输入1>"}, 
  {"role": "user", "content": "<用户输入1>"}, 
  {"role": "assistant", "content": "<模型期望输出1>"}, 
  {"role": "user", "content": "<用户输入2>"}, 
  {"role": "assistant", "content": "<模型期望输出2>"}
  ...
  ...
  ...
  ]
}
system/user/assistant 区别请参见文本生成模型概述。
不支持OpenAI 的name、weight参数，所有的 assistant 输出都会被训练。

SFT 图像理解训练集
SFT图像理解 ChatML 格式训练数据（图片文件会与文本训练数据在同一目录下一起打包成 zip），一行训练数据展开后结构如下：
{"messages":[
  {"role":"user",
    "content":[
      {"text":"<用户输入1>"},
      {"image":"<图像文件名1>"}]},
  {"role":"assistant",
    "content":[
      {"text":"<模型期望输出1>"}]},
  {"role":"user",
    "content":[
      {"text":"<用户输入2>"}]},
  {"role":"assistant",
    "content":[
      {"text":"<模型期望输出2>"}]},
  ...
  ...
  ...
 ]}
system/user/assistant 区别请参见文本生成模型概述。
不支持OpenAI 的name、weight参数，所有的 assistant 输出都会被训练。

DPO 数据集
DPO ChatML 格式训练数据，一行训练数据展开后结构如下：
{"messages":[
  {"role":"system","content":"<系统输入>"},
  {"role":"user","content":"<用户输入1>"},
  {"role":"assistant","content":"<模型输出1>"},
  {"role":"user","content":"<用户输入2>"},
  {"role":"assistant","content":"<模型输出2>"},
  {"role":"user","content":"<用户输入3>"}],
 "chosen":
   {"role":"assistant","content":"<赞同的模型期望输出3>"},
 "rejected":
   {"role":"assistant","content":"<反对的模型期望输出3>"}}
模型将 messages 内的所有内容均作为输入，DPO 用于训练模型对"<用户输入3>"的正负反馈。
system/user/assistant 区别请参见文本生成模型概述。

将训练文件上传至阿里云百炼
Shell
一次调用只能上传一个文件
dashscope files.upload -f '<替换为训练数据集的本地文件路径>' -p fine_tune -d 'training dataset'

说明
SFT、DPO、CPT数据集支持.jsonl文件；SFT图像理解训练集支持.zip压缩包。

使用限制：

单个文件大小最大为300MB。

有效文件（未删除）总使用空间配额为5GB。

有效文件（未删除）总数量配额为100个。
返回结果：
Upload success, file id: 976bd01a-f30b-4414-86fd-50c54486e3ef

HTTP
Windows CMD 请将${DASHSCOPE_API_KEY}替换为 %DASHSCOPE_API_KEY%，PowerShell 请替换为 $env:DASHSCOPE_API_KEY
curl --location --request POST \
'https://dashscope.aliyuncs.com/api/v1/files' \
--header 'Authorization: Bearer '${DASHSCOPE_API_KEY} \
--form 'files=@"./qwen-fine-tune-sample.jsonl"' \
--form 'purpose="fine-tune"'\
--form 'descriptions="a sample fine-tune data file for qwen"'

说明
使用限制：

单个文件大小最大为300MB

所有有效文件（未删除）总使用空间配额为5GB

所有有效文件（未删除）总数量配额为100个

更多详细信息请参见模型微调文件管理服务。
返回结果：
{
  "request_id":"xx",
  "data":{
    "uploaded_files":[{
      "file_id":"976bd01a-f30b-4414-86fd-50c54486e3ef",
      "name":"qwen-fine-tune-sample.jsonl"}],
  　"failed_uploads":[]}
 }

模型微调
创建微调任务
Shell
dashscope fine_tunes.call -m qwen-turbo -t '<替换为训练数据集的file_id1>' '<替换为训练数据集的file_id2>' \
--mode sft -b 16 -e 1 -l 1.6e-5 \
--hyper_parameters split=0.9 warmup_ratio=0.0 eval_steps=1
微调指令进程即使在微调结束后也不会自动关闭，可以随时终止微调指令进程，不会影响阿里云百炼平台上的模型微调任务。

您可以使用后续介绍的命令或前往控制台查看当前任务状态并获取微调任务日志。


HTTP
Windows CMD 请将${DASHSCOPE_API_KEY}替换为 %DASHSCOPE_API_KEY%，PowerShell 请替换为 $env:DASHSCOPE_API_KEY
curl --location 'https://dashscope.aliyuncs.com/api/v1/fine-tunes' \
--header 'Authorization: Bearer '${DASHSCOPE_API_KEY} \
--header 'Content-Type: application/json' \
--data '{
    "model":"qwen-turbo",
    "training_file_ids":[
        "<替换为训练数据集的file_id1>",
        "<替换为训练数据集的file_id2>"
    ],
    "hyper_parameters":{
        "n_epochs":1,
        "batch_size":16,
        "learning_rate":"1.6e-5",
        "split":0.9,
        "warmup_ratio":0.0,
        "eval_steps":1
    },
    "training_type":"sft"
}'

| 字段 | 必选 | 类型 | 传参方式 | 描述 |
|------|------|------|----------|------|
| training_file_ids | 是 | Array | Body | 训练集文件列表。 |
| validation_file_ids | 否 | Array | Body | 验证集文件列表。 |
| model | 是 | String | Body | **用于微调的基础模型 ID，或其他微调任务产出的模型 ID。** |
| hyper_parameters | 否 | Map | Body | 用于微调模型的超参数，缺失该参数时系统会使用默认值进行微调。 |
| training_type | 否 | String | Body | 训练方法，可选值为：<br>• `cpt`<br>• `sft`<br>• `efficient_sft`<br>• `dpo_full`<br>• `dpo_lora` |
返回样例
{
    "request_id":"8ee17797-028c-43f6-b444-0598d6bfb0f9",
    "output":{
        "job_id":"ft-202410121111-a590",
        "job_name":"ft-202410121111-a590",
        "status":"PENDING",
        "model":"qwen-turbo",
        "base_model":"qwen-turbo",
        "training_file_ids":[
            "976bd01a-f30b-4414-86fd-50c54486e3ef"],
      "validation_file_ids":[],
      "hyper_parameters":{
          "n_epochs":1,
          "batch_size":16,
          "learning_rate":"1.6e-5",
          "split":0.9,
          "warmup_ratio":0.0,
          "eval_steps":1},
      "training_type":"sft",
      "create_time":"2024-10-12 11:55:45",
      "user_identity":"1396993924585947",
      "modifier":"1396993924585947",
      "creator":"1396993924585947",
      "group":"llm"
    }
}

支持的基础模型ID（model）列表与训练类型（training_type）支持情况：
模型默认值为sft，如果未声明模型且模型不支持sft方法，微调任务将会失败。
| 模型名称 | 模型代码 | CPT 全参训练 (cpt) | SFT 全参训练 (sft) | SFT 高效训练 (efficient_sft) | DPO 全参训练 (dpo_full) | DPO 高效训练 (dpo_lora) |
|---|---|---|---|---|---|---|
| 通义千问 3-32B | qwen3-32b |  | ✅ | ✅ | ✅ | ✅ |
| 通义千问 3-14B | qwen3-14b |  | ✅ | ✅ | ✅ | ✅ |
| 通义千问 3-8B | qwen3-8b |  | ✅ | ✅ | ✅ | ✅ |
| 通义千问 3-32B-Base | qwen3-32b-base |  | ✅ | ✅ |  |  |
| 通义千问 3-14B-Base | qwen3-14b-base |  | ✅ | ✅ |  |  |
| 通义千问 3-8B-Base | qwen3-8b-base |  | ✅ | ✅ |  |  |
| 通义千问 2.5-72B | qwen2.5-72b-instruct | ✅ | ✅ | ✅ | ✅ | ✅ |
| 通义千问 2.5-32B | qwen2.5-32b-instruct | ✅ |  | ✅ | ✅ | ✅ |
| 通义千问 2.5-14B | qwen2.5-14b-instruct | ✅ | ✅ | ✅ | ✅ | ✅ |
| 通义千问 2.5-7B | qwen2.5-7b-instruct | ✅ | ✅ | ✅ | ✅ | ✅ |
| 通义千问 2.5-VL-72B | qwen2.5-vl-72b-instruct |  | ✅ | ✅ | ✅ | ✅ |
| 通义千问 2.5-VL-32B | qwen2.5-vl-32b-instruct |  | ✅ | ✅ |  |  |
| 通义千问 2.5-VL-7B | qwen2.5-vl-7b-instruct |  | ✅ | ✅ |  |  |
| 通义千问-Turbo-0624（通义商业版） | qwen-turbo-0624 |  | ✅ | ✅ | ✅ | ✅ |
| 通义千问-Plus-0723（通义商业版） | qwen-plus-0723 |  |  | ✅ |  | ✅ |
| 通义千问VL-Max-0201 | qwen-vl-max-0201 |  |  | ✅ |  |  |
| 通义千问VL-Plus | qwen-vl-plus |  |  | ✅ |  |  |

常用超参数
| 超参数名称 | 默认设置 | 推荐设置 | 超参数作用 |
|-------------|-----------|-----------|-------------|
| **循环次数** | 1 | 数据量 < 10,000，循环 3~5 次<br>数据量 > 10,000，循环 1~2 次<br>具体需要结合实验效果进行判断。 | 模型遍历训练的次数，请根据模型调优实际使用经验进行调整。<br>模型训练循环次数越多，训练时间越长，训练费用越高。 |
| 参数选项 | -e<br>--n_epochs<br>"n_epochs" | | |
| **学习率** | -l<br>--<br>learning_rate<br>"learning_rate" | • sft/dpo_full/dpo_lora：1e-5 量级<br>• efficient_sft：1e-4 量级<br>使用默认值<br>具体数值随模型选择变化。 | 控制模型修正权重的强度。<br>• 学习率设置得太高，模型参数会剧烈变化，导致微调后的模型表现不一定更好，甚至变差；<br>• 学习率太低，微调后的模型表现不会有太大变化。 |
| **批次大小** | -b<br>--batch_size<br>"batch_size" | 具体数值随模型选择变化。<br>模型越大，默认 batch_size 越小。<br>使用默认值 | 一次性送入模型进行训练的数据条数，参数过小会显著延长训练时间，推荐使用默认值。 |
| **参数无效** | -p/--<br>prompt_loss | / | / |

输入hyper_parameters超参数列表
| 超参数名称 | 默认设置 | 推荐设置 | 超参数作用 |
|-------------|-----------|-----------|-------------|
| `split`<br>(训练集在训练文件中占比) | 0.8 | 使用默认值 | 当不设置 `-v/--validation_file_ids/"validation_file_ids"` 时，阿里云百炼会自动把训练文件中的 80% 作为训练集，20% 作为验证集。 |
| `max_split_val_dataset_sample`<br>(验证集数据最大数量) | 1000 | 使用默认值 | 当不设置 `-v/--validation_file_ids/"validation_file_ids"` 时，阿里云百炼会自动分割的验证集最多只有 1000 条。 |
| `lr_scheduler_type`<br>(学习率调整策略) | cosine | 推荐 `linear / Inverse_sqrt` | 在模型训练中动态调整学习率的策略。<br>各策略详情请参考 [学习率调整策略介绍]。 |
| `eval_steps`<br>(验证步数) | 50 | 根据需求调整 | 训练阶段针对模型的验证间隔步长，用于阶段性评估模型训练准确率、训练损失。<br>该参数影响训练时的 Validation Loss 和 Validation Token Accuracy 的显示频率。 |
| `max_length`<br>(序列长度) | 2048 | 8192 | 指的是单条训练数据 token 支持的最大长度。如果单条数据 token 长度超过设定值，微调会直接丢弃该数据，不进行训练。<br>字符与 token 之间的关系请参考 [Token 和字符之间怎么换算]。 |
| `warmup_ratio`<br>(学习率预热比例) | 0.05 | 使用默认值 | 学习率预热占用总的训练过程的比例。学习率预热是指学习率在训练开始后由一个较小值线性递增至学习率设定值。<br>该参数主要是限制模型参数在训练初始阶段的变化幅度，从而帮助模型更稳定地进行训练。<br>比例过大效果与过高的学习率相同，会导致微调后的模型表现不会有太大变化。<br>比例过小效果与过高的学习率相同，可能导致微调后的模型表现不一定更好，甚至变差。<br>该参数仅对学习率调整策略 “Constant” 无效。 |
| `weight_decay`<br>(权重衰减) | 0.1 | 使用默认值 | L2 正则化强度。L2 正则化能在一定程度上保持模型的通用能力。数值过大会导致模型微调效果不明显。 |
| `max_grad_norm`<br>(梯度裁剪) | 1 | 使用默认值 | 梯度裁剪的最大值，用于防止参数微调时剧烈变化导致的微调失败。数值过大可能会导致微调失败，数值过小会导致模型微调效果不明显。 |
| `logging_steps`<br>(日志显示步数) | 5 | 根据需求调整 | 微调日志打印的步数。 |

输入hyper_parameters超参数列表（仅efficient_sft/dpo_lora生效）
| 超参数名称 | 默认设置 | 推荐设置 | 超参数作用 |
|-------------|-----------|-----------|-------------|
| **lora_rank**<br>(LoRA 秩值) | 8 | 64 | LoRA 训练中的低秩矩阵的秩大小。秩越大调优效果会更好一点，但训练会略慢。 |
| **lora_alpha**<br>(LoRA 阿尔法) | 32 | 使用默认值 | 用于控制原模型权重与 LoRA 的低秩修正项之间的结合缩放系数。<br>较大的 Alpha 值会给予 LoRA 修正项更多权重，使得模型更加依赖于微调任务的特定信息；<br>而较小的 Alpha 值则会让模型更倾向于保留原始预训练模型的知识。 |
| **lora_dropout**<br>(LoRA 丢弃率) | 0.1 | 使用默认值 | LoRA 训练中的低秩矩阵值的丢弃率。<br>使用推荐数值能增强模型通用化能力。<br>数值过大则会导致模型微调效果不明显。 |
| **target_modules**<br>(LoRA 目标模块) | AUTO | 推荐设置为 ALL | 选择模型的全部或特定模块层进行微调优化。<br>• **ALL** 是对所有的参数都加上 LoRA 训练；<br>• **AUTO** 是指对模型的关键参数加上 LoRA 训练。 |
