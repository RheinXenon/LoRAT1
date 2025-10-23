"""
阿里云百炼平台微调自动化脚本
功能：
1. 自动转换数据格式
2. 上传训练和验证文件
3. 创建微调任务
4. 查询任务状态
5. 调用微调后的模型
"""

import os
import sys
import json
import time
from pathlib import Path
from dotenv import load_dotenv

try:
    import dashscope
    from dashscope import Generation
except ImportError:
    print("❌ 未安装 dashscope SDK")
    print("请运行: pip install dashscope")
    sys.exit(1)


class FineTuneAutomation:
    def __init__(self):
        """初始化配置"""
        # 加载 .env 文件
        load_dotenv()
        
        # 获取配置
        self.api_key = os.getenv("DASHSCOPE_API_KEY")
        if not self.api_key:
            raise ValueError("❌ 请在 .env 文件中设置 DASHSCOPE_API_KEY")
        
        # 设置 API Key
        dashscope.api_key = self.api_key
        
        # 微调配置
        self.base_model = os.getenv("FINE_TUNE_BASE_MODEL", "qwen2.5-7b-instruct")
        self.training_type = os.getenv("TRAINING_TYPE", "efficient_sft")
        
        # 超参数配置
        self.hyper_params = {
            "n_epochs": int(os.getenv("N_EPOCHS", "3")),
            "batch_size": int(os.getenv("BATCH_SIZE", "16")),
            "learning_rate": os.getenv("LEARNING_RATE", "1e-4"),
            "split": float(os.getenv("SPLIT", "0.9")),
            "warmup_ratio": float(os.getenv("WARMUP_RATIO", "0.05")),
            "eval_steps": int(os.getenv("EVAL_STEPS", "50")),
            "max_length": int(os.getenv("MAX_LENGTH", "2048")),
        }
        
        # 如果是 LoRA 训练，添加 LoRA 参数
        if self.training_type == "efficient_sft":
            self.hyper_params.update({
                "lora_rank": int(os.getenv("LORA_RANK", "64")),
                "lora_alpha": int(os.getenv("LORA_ALPHA", "32")),
                "lora_dropout": float(os.getenv("LORA_DROPOUT", "0.1")),
                "target_modules": os.getenv("TARGET_MODULES", "ALL"),
            })
        
        self.project_root = Path(__file__).parent.parent
        self.data_dir = self.project_root / "datasets" / "MedQA_BaiLian"

    def list_available_datasets(self):
        """列出可用的数据集"""
        print("\n" + "="*60)
        print("📁 可用的数据集:")
        print("="*60)
        
        if not self.data_dir.exists():
            print("❌ 数据集目录不存在，请先运行 batch_convert.py 转换数据")
            return []
        
        datasets = []
        for i, file in enumerate(sorted(self.data_dir.glob("*.jsonl")), 1):
            file_size = file.stat().st_size / (1024 * 1024)  # MB
            datasets.append(str(file))
            print(f"{i}. {file.name} ({file_size:.2f} MB)")
        
        return datasets

    def upload_file(self, file_path, description=""):
        """上传文件到百炼平台"""
        print(f"\n⬆️  上传文件: {Path(file_path).name}")
        
        try:
            # 使用 HTTP API 方式上传文件
            import requests
            
            url = "https://dashscope.aliyuncs.com/api/v1/files"
            headers = {
                "Authorization": f"Bearer {self.api_key}"
            }
            
            with open(file_path, 'rb') as f:
                files = {
                    'files': (Path(file_path).name, f, 'application/json')
                }
                data = {
                    'purpose': 'fine-tune',
                    'descriptions': description
                }
                
                response = requests.post(url, headers=headers, files=files, data=data)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('data', {}).get('uploaded_files'):
                    file_id = result['data']['uploaded_files'][0]['file_id']
                    print(f"✅ 上传成功! File ID: {file_id}")
                    return file_id
                else:
                    print(f"❌ 上传失败: {result}")
                    return None
            else:
                print(f"❌ 上传失败: HTTP {response.status_code}")
                print(f"   响应内容: {response.text}")
                return None
        except Exception as e:
            print(f"❌ 上传出错: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

    def create_fine_tune_job(self, train_file_ids, validation_file_ids=None):
        """创建微调任务"""
        print(f"\n🚀 创建微调任务...")
        print(f"   基础模型: {self.base_model}")
        print(f"   训练类型: {self.training_type}")
        print(f"   超参数: {json.dumps(self.hyper_params, indent=2, ensure_ascii=False)}")
        
        try:
            import requests
            
            # 准备参数
            url = "https://dashscope.aliyuncs.com/api/v1/fine-tunes"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.base_model,
                "training_file_ids": train_file_ids if isinstance(train_file_ids, list) else [train_file_ids],
                "hyper_parameters": self.hyper_params,
                "training_type": self.training_type,
            }
            
            if validation_file_ids:
                data["validation_file_ids"] = validation_file_ids if isinstance(validation_file_ids, list) else [validation_file_ids]
            
            # 创建任务
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 200:
                result = response.json()
                job_id = result['output']['job_id']
                print(f"\n✅ 微调任务创建成功!")
                print(f"   Job ID: {job_id}")
                print(f"   状态: {result['output'].get('status', 'UNKNOWN')}")
                print(f"\n💡 提示: 请将以下内容保存到 .env 文件:")
                print(f"   FINE_TUNE_JOB_ID={job_id}")
                return job_id
            else:
                print(f"❌ 创建失败: HTTP {response.status_code}")
                print(f"   响应内容: {response.text}")
                return None
        except Exception as e:
            print(f"❌ 创建出错: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

    def get_job_status(self, job_id):
        """查询任务状态"""
        try:
            import requests
            
            url = f"https://dashscope.aliyuncs.com/api/v1/fine-tunes/{job_id}"
            headers = {
                "Authorization": f"Bearer {self.api_key}"
            }
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                return result.get('output', {})
            else:
                print(f"❌ 查询失败: HTTP {response.status_code}")
                print(f"   响应内容: {response.text}")
                return None
        except Exception as e:
            print(f"❌ 查询出错: {str(e)}")
            return None

    def monitor_job(self, job_id, check_interval=30):
        """监控任务进度"""
        print(f"\n👀 监控微调任务: {job_id}")
        print(f"   检查间隔: {check_interval}秒")
        print("   按 Ctrl+C 可退出监控（不影响训练任务）\n")
        
        status_map = {
            "PENDING": "⏳ 等待中",
            "RUNNING": "🏃 运行中",
            "SUCCEEDED": "✅ 成功",
            "FAILED": "❌ 失败",
            "CANCELLED": "🚫 已取消",
        }
        
        try:
            while True:
                status_data = self.get_job_status(job_id)
                
                if status_data:
                    status = status_data.get('status', 'UNKNOWN')
                    status_text = status_map.get(status, status)
                    
                    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 状态: {status_text}")
                    
                    # 显示额外信息
                    if 'trained_tokens' in status_data:
                        print(f"   已训练 tokens: {status_data['trained_tokens']}")
                    if 'training_progress' in status_data:
                        print(f"   训练进度: {status_data['training_progress']}%")
                    
                    # 检查是否完成
                    if status in ["SUCCEEDED", "FAILED", "CANCELLED"]:
                        print(f"\n{'='*60}")
                        print(f"🎯 任务已完成: {status_text}")
                        
                        if status == "SUCCEEDED":
                            model_id = status_data.get('fine_tuned_model', '')
                            print(f"   微调后的模型 ID: {model_id}")
                            print(f"\n💡 提示: 请将以下内容保存到 .env 文件:")
                            print(f"   FINE_TUNED_MODEL_ID={model_id}")
                            print(f"\n📝 下一步: 在百炼控制台部署模型")
                            print(f"   控制台地址: https://bailian.console.aliyun.com/")
                        elif status == "FAILED":
                            error_msg = status_data.get('error_message', '未知错误')
                            print(f"   错误信息: {error_msg}")
                        
                        print("="*60)
                        break
                
                time.sleep(check_interval)
        except KeyboardInterrupt:
            print("\n\n⚠️  退出监控（训练任务仍在后台继续）")
            print(f"💡 使用以下命令继续查看状态:")
            print(f"   python {Path(__file__).name} --status {job_id}")

    def test_model(self, model_id, test_question=None):
        """测试微调后的模型"""
        print(f"\n🧪 测试微调模型: {model_id}\n")
        
        if not test_question:
            test_question = """卧位腰椎穿刺，脑脊液压力正常值是（　　）。

选项：
A. 80～180mmH2O（0.78～1.76kPa）
B. 50～70mmH2O（0.49～0.69kPa）
C. 230～250mmH2O（2.25～2.45kPa）
D. 260～280mmH2O（2.55～2.74kPa）"""
        
        try:
            response = Generation.call(
                model=model_id,
                messages=[
                    {
                        'role': 'system',
                        'content': '你是一个专业的医学助手，擅长回答医学选择题。'
                    },
                    {
                        'role': 'user',
                        'content': test_question
                    }
                ]
            )
            
            if response.status_code == 200:
                print("📊 模型回答:")
                print("-" * 60)
                print(response.output.text)
                print("-" * 60)
            else:
                print(f"❌ 调用失败: {response.message}")
        except Exception as e:
            print(f"❌ 测试出错: {str(e)}")

    def update_env_file(self, key, value):
        """更新 .env 文件"""
        env_file = self.project_root / ".env"
        
        # 读取现有内容
        lines = []
        if env_file.exists():
            with open(env_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        
        # 查找并更新
        updated = False
        for i, line in enumerate(lines):
            if line.strip().startswith(f"{key}="):
                lines[i] = f"{key}={value}\n"
                updated = True
                break
        
        # 如果没找到，添加到末尾
        if not updated:
            lines.append(f"{key}={value}\n")
        
        # 写回文件
        with open(env_file, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        print(f"✅ 已更新 .env 文件: {key}={value}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='阿里云百炼平台微调自动化工具')
    parser.add_argument('--upload', action='store_true', help='上传训练文件')
    parser.add_argument('--create', action='store_true', help='创建微调任务')
    parser.add_argument('--status', type=str, help='查询任务状态（提供 job_id）')
    parser.add_argument('--monitor', type=str, help='监控任务进度（提供 job_id）')
    parser.add_argument('--test', type=str, help='测试模型（提供 model_id）')
    parser.add_argument('--auto', action='store_true', help='自动执行完整流程')
    
    args = parser.parse_args()
    
    try:
        automation = FineTuneAutomation()
        
        # 如果没有参数，显示交互式菜单
        if not any([args.upload, args.create, args.status, args.monitor, args.test, args.auto]):
            print("\n" + "="*60)
            print("🎯 阿里云百炼平台微调自动化工具")
            print("="*60)
            print("\n请选择操作:")
            print("1. 上传训练文件")
            print("2. 创建微调任务")
            print("3. 查询任务状态")
            print("4. 监控任务进度")
            print("5. 测试微调模型")
            print("6. 自动执行完整流程")
            print("0. 退出")
            
            choice = input("\n请输入选项 (0-6): ").strip()
            
            if choice == "1":
                args.upload = True
            elif choice == "2":
                args.create = True
            elif choice == "3":
                job_id = input("请输入 Job ID: ").strip()
                args.status = job_id
            elif choice == "4":
                job_id = input("请输入 Job ID: ").strip()
                args.monitor = job_id
            elif choice == "5":
                model_id = input("请输入 Model ID: ").strip()
                args.test = model_id
            elif choice == "6":
                args.auto = True
            elif choice == "0":
                print("👋 再见!")
                return
            else:
                print("❌ 无效的选项")
                return
        
        # 执行操作
        if args.upload or args.auto:
            datasets = automation.list_available_datasets()
            if not datasets:
                return
            
            print("\n请选择训练集:")
            train_idx = input("输入编号: ").strip()
            train_file = datasets[int(train_idx) - 1]
            
            print("\n请选择验证集（可选，直接回车跳过）:")
            val_idx = input("输入编号: ").strip()
            val_file = datasets[int(val_idx) - 1] if val_idx else None
            
            # 上传文件
            train_file_id = automation.upload_file(train_file, "训练集")
            val_file_id = automation.upload_file(val_file, "验证集") if val_file else None
            
            if train_file_id:
                automation.update_env_file("TRAIN_FILE_ID", train_file_id)
            if val_file_id:
                automation.update_env_file("VALIDATION_FILE_ID", val_file_id)
            
            # 如果是自动模式，继续创建任务
            if args.auto and train_file_id:
                args.create = True
        
        if args.create:
            # 从 .env 获取或从参数获取
            train_file_id = os.getenv("TRAIN_FILE_ID")
            val_file_id = os.getenv("VALIDATION_FILE_ID")
            
            if not train_file_id:
                train_file_id = input("请输入训练集 File ID: ").strip()
            
            val_input = input(f"请输入验证集 File ID（当前: {val_file_id or '无'}，直接回车使用当前值）: ").strip()
            if val_input:
                val_file_id = val_input
            
            job_id = automation.create_fine_tune_job(train_file_id, val_file_id)
            
            if job_id:
                automation.update_env_file("FINE_TUNE_JOB_ID", job_id)
                
                # 如果是自动模式，开始监控
                if args.auto:
                    args.monitor = job_id
        
        if args.status:
            status_data = automation.get_job_status(args.status)
            if status_data:
                print("\n" + "="*60)
                print(f"📊 任务状态: {args.status}")
                print("="*60)
                print(json.dumps(status_data, indent=2, ensure_ascii=False))
        
        if args.monitor:
            automation.monitor_job(args.monitor)
        
        if args.test:
            automation.test_model(args.test)
    
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

