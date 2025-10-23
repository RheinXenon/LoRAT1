"""
将 MedQA 数据集转换为阿里云百炼平台所需的 SFT 格式

原始格式：
{
    "question": "问题文本",
    "options": {"A": "选项A", "B": "选项B", "C": "选项C", "D": "选项D"},
    "answer": "正确答案文本",
    "meta_info": "元信息",
    "answer_idx": "A"
}

目标格式：
{
    "messages": [
        {"role": "system", "content": "系统提示"},
        {"role": "user", "content": "用户输入"},
        {"role": "assistant", "content": "模型期望输出"}
    ]
}
"""

import json
import argparse
from pathlib import Path


def format_question_with_options(question, options):
    """将问题和选项格式化为完整的提示"""
    formatted = question + "\n\n选项：\n"
    for key in sorted(options.keys()):
        formatted += f"{key}. {options[key]}\n"
    return formatted.strip()


def convert_to_bailian_format(input_file, output_file, system_prompt=None):
    """
    转换单个 JSONL 文件为百炼格式
    
    Args:
        input_file: 输入文件路径
        output_file: 输出文件路径
        system_prompt: 系统提示（可选）
    """
    if system_prompt is None:
        system_prompt = "你是一个专业的医学助手，擅长回答医学选择题。请根据题目和选项，给出正确答案及简要解释。"
    
    converted_count = 0
    skipped_count = 0
    
    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', encoding='utf-8') as outfile:
        
        for line_num, line in enumerate(infile, 1):
            line = line.strip()
            if not line:
                continue
            
            try:
                data = json.loads(line)
                
                # 提取字段
                question = data.get('question', '')
                options = data.get('options', {})
                answer_idx = data.get('answer_idx', '')
                answer_text = data.get('answer', '')
                
                # 格式化用户输入（问题 + 选项）
                user_content = format_question_with_options(question, options)
                
                # 格式化助手输出（答案索引 + 答案文本）
                assistant_content = f"答案是 {answer_idx}. {answer_text}"
                
                # 构建百炼格式
                bailian_format = {
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_content},
                        {"role": "assistant", "content": assistant_content}
                    ]
                }
                
                # 写入输出文件
                outfile.write(json.dumps(bailian_format, ensure_ascii=False) + '\n')
                converted_count += 1
                
            except json.JSONDecodeError as e:
                print(f"警告: 第 {line_num} 行 JSON 解析错误: {e}")
                skipped_count += 1
            except Exception as e:
                print(f"警告: 第 {line_num} 行处理错误: {e}")
                skipped_count += 1
    
    return converted_count, skipped_count


def main():
    parser = argparse.ArgumentParser(description='转换 MedQA 数据集为百炼平台 SFT 格式')
    parser.add_argument('input', help='输入 JSONL 文件路径')
    parser.add_argument('output', help='输出 JSONL 文件路径')
    parser.add_argument('--system-prompt', 
                       default="你是一个专业的医学助手，擅长回答医学选择题。请根据题目和选项，给出正确答案及简要解释。",
                       help='系统提示词')
    
    args = parser.parse_args()
    
    # 检查输入文件是否存在
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"错误: 输入文件 '{args.input}' 不存在")
        return
    
    # 确保输出目录存在
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"开始转换: {args.input} -> {args.output}")
    print(f"系统提示: {args.system_prompt}\n")
    
    converted, skipped = convert_to_bailian_format(
        args.input, 
        args.output, 
        args.system_prompt
    )
    
    print(f"\n转换完成!")
    print(f"成功转换: {converted} 条")
    print(f"跳过: {skipped} 条")
    print(f"输出文件: {args.output}")
    
    # 显示文件大小
    output_size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"输出文件大小: {output_size_mb:.2f} MB")
    
    if output_size_mb > 300:
        print("\n警告: 文件大小超过 300MB，百炼平台限制单个文件最大 300MB")
        print("建议将数据分割成多个文件上传")


if __name__ == '__main__':
    main()

