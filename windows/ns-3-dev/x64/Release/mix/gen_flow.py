import random
import argparse

# 修正相对路径
from pathlib import Path
file_dir = Path(__file__).parent

def pick_flows(input_file, output_file, num_flows):
    # 读取文件
    with open(input_file, 'r') as f:
        lines = f.readlines()

    # 获取原始流数量
    total_flows = int(lines[0].strip())
    flow_lines = lines[1:total_flows+1]  # 只取有效的flow行

    # 确保请求的流数量不超过总流数
    num_flows = min(num_flows, total_flows)

    # 随机选择流
    selected_flows = random.sample(flow_lines, num_flows)

    # 写入新文件
    with open(output_file, 'w') as f:
        # 写入新的流数量
        f.write(f"{num_flows}\n")
        # 写入选中的流
        for line in selected_flows:
            f.write(line)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Randomly pick flows from input file')
    parser.add_argument('--input', default=f'{file_dir/'full-origin/flow.txt'}', help='Input file path')
    parser.add_argument('--num_flows', type=int, default=100, help='Number of flows to pick')
    parser.add_argument('--output', default='flow.txt', help='Output file path')

    args = parser.parse_args()

    pick_flows(args.input, args.output, args.num_flows)