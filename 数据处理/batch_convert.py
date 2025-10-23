"""
批量转换 MedQA 数据集为百炼格式的脚本
"""

import os
from pathlib import Path
from convert_to_bailian_format import convert_to_bailian_format


def batch_convert():
    """批量转换所有 MedQA 数据集"""
    
    # 由于脚本在"数据处理"子文件夹中，需要向上一层找到项目根目录
    base_dir = Path(__file__).parent.parent / "datasets" / "MedQA" / "questions"
    output_dir = Path(__file__).parent.parent / "datasets" / "MedQA_BaiLian"
    
    # 定义要转换的数据集
    datasets = [
        # 中国大陆数据集（4选项）
        ("Mainland/4_options/train.jsonl", "mainland_4opt_train.jsonl"),
        ("Mainland/4_options/dev.jsonl", "mainland_4opt_dev.jsonl"),
        ("Mainland/4_options/test.jsonl", "mainland_4opt_test.jsonl"),
        
        # 台湾数据集
        ("Taiwan/train.jsonl", "taiwan_train.jsonl"),
        ("Taiwan/dev.jsonl", "taiwan_dev.jsonl"),
        ("Taiwan/test.jsonl", "taiwan_test.jsonl"),
        
        # 美国数据集（4选项）
        ("US/4_options/phrases_no_exclude_train.jsonl", "us_4opt_train.jsonl"),
        ("US/4_options/phrases_no_exclude_dev.jsonl", "us_4opt_dev.jsonl"),
        ("US/4_options/phrases_no_exclude_test.jsonl", "us_4opt_test.jsonl"),
    ]
    
    system_prompt = "你是一个专业的医学助手，擅长回答医学选择题。请根据题目和选项，给出正确答案。"
    
    # 创建输出目录
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("批量转换 MedQA 数据集为百炼平台格式")
    print("=" * 60)
    print()
    
    results = []
    
    for input_rel, output_name in datasets:
        input_path = base_dir / input_rel
        output_path = output_dir / output_name
        
        if not input_path.exists():
            print(f"⚠️  跳过 (文件不存在): {input_rel}")
            continue
        
        print(f"正在转换: {input_rel}")
        print(f"  -> {output_path}")
        
        try:
            converted, skipped = convert_to_bailian_format(
                str(input_path),
                str(output_path),
                system_prompt
            )
            
            file_size_mb = output_path.stat().st_size / (1024 * 1024)
            
            results.append({
                'name': output_name,
                'converted': converted,
                'skipped': skipped,
                'size_mb': file_size_mb
            })
            
            status = "✅" if file_size_mb <= 300 else "⚠️  (超过300MB限制)"
            print(f"  完成: {converted} 条, {file_size_mb:.2f} MB {status}\n")
            
        except Exception as e:
            print(f"  ❌ 错误: {e}\n")
            continue
    
    # 显示汇总
    print("=" * 60)
    print("转换汇总")
    print("=" * 60)
    
    total_converted = sum(r['converted'] for r in results)
    total_size = sum(r['size_mb'] for r in results)
    
    for result in results:
        print(f"{result['name']:<35} {result['converted']:>6} 条  {result['size_mb']:>8.2f} MB")
    
    print("-" * 60)
    print(f"{'总计':<35} {total_converted:>6} 条  {total_size:>8.2f} MB")
    print()
    print(f"输出目录: {output_dir}")
    print()
    
    # 大文件警告
    large_files = [r for r in results if r['size_mb'] > 300]
    if large_files:
        print("⚠️  以下文件超过 300MB，需要分割:")
        for r in large_files:
            print(f"  - {r['name']}: {r['size_mb']:.2f} MB")
        print()


if __name__ == '__main__':
    batch_convert()

