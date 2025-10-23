"""
使用示例：如何调用微调后的模型
"""

import os
from dotenv import load_dotenv

try:
    from dashscope import Generation
except ImportError:
    print("❌ 未安装 dashscope SDK")
    print("请运行: pip install dashscope")
    exit(1)

# 加载配置
load_dotenv()

# 获取微调后的模型 ID
model_id = os.getenv("FINE_TUNED_MODEL_ID")
if not model_id:
    print("❌ 请在 .env 文件中设置 FINE_TUNED_MODEL_ID")
    print("提示：在百炼控制台部署模型后可获取模型 ID")
    exit(1)

# 设置 API Key
api_key = os.getenv("DASHSCOPE_API_KEY")
if not api_key:
    print("❌ 请在 .env 文件中设置 DASHSCOPE_API_KEY")
    exit(1)

print(f"🤖 使用微调模型: {model_id}\n")

# 测试问题
test_questions = [
    """卧位腰椎穿刺，脑脊液压力正常值是（　　）。

选项：
A. 80～180mmH2O（0.78～1.76kPa）
B. 50～70mmH2O（0.49～0.69kPa）
C. 230～250mmH2O（2.25～2.45kPa）
D. 260～280mmH2O（2.55～2.74kPa）""",
    
    """急性阑尾炎最常见的并发症是（　　）。

选项：
A. 阑尾穿孔
B. 腹膜炎
C. 肠梗阻
D. 脓肿形成""",
]

# 系统提示词
system_prompt = "你是一个专业的医学助手，擅长回答医学选择题。请根据题目和选项，给出正确答案。"

# 测试每个问题
for i, question in enumerate(test_questions, 1):
    print(f"{'='*60}")
    print(f"问题 {i}:")
    print(f"{'='*60}")
    print(question)
    print(f"\n{'─'*60}")
    print("模型回答:")
    print(f"{'─'*60}\n")
    
    try:
        response = Generation.call(
            model=model_id,
            api_key=api_key,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': question}
            ]
        )
        
        if response.status_code == 200:
            print(response.output.text)
        else:
            print(f"❌ 调用失败: {response.message}")
    
    except Exception as e:
        print(f"❌ 发生错误: {str(e)}")
    
    print()

print("✅ 测试完成!")

