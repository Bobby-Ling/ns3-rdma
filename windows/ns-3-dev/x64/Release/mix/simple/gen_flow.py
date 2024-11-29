import random
import argparse
from types import SimpleNamespace

def generate_flows(num_flows, start_time_range, end_time_range, data_size_range):
    compute_ports = list(range(4))
    storage_ports = list(range(4, 16)) + list(range(16, 28))

    flows = []
    for _ in range(num_flows):
        src_port = random.choice(compute_ports)
        dst_port = random.choice(storage_ports)
        priority = 3
        packet_count = 1

        start_time = 2.0
        # start_time = round(random.uniform(start_time_range[0], start_time_range[1]), 2)
        end_time = round(random.uniform(end_time_range[0], end_time_range[1]), 2)
        end_time = 9.5

        while end_time <= start_time:
            end_time = round(random.uniform(end_time_range[0], end_time_range[1]), 2)

        flows.append((src_port, dst_port, priority, packet_count, start_time, end_time))

    return flows

def save_flows(flows, filename):
    with open(filename, 'w') as f:
        f.write(f"{len(flows)}\n")
        for flow in flows:
            f.write(f"{flow[0]} {flow[1]} {flow[2]} {flow[3]} {flow[4]:.2f} {flow[5]:.2f}\n")

# 方法1：直接创建参数对象
def create_args_directly():
    args = SimpleNamespace(
        num_flows=500,
        start_time_min=2.0,
        start_time_max=2.0,
        end_time_min=9.5,
        end_time_max=9.5,
        output='flow.txt'
    )
    return args

# 方法2：使用argparse但手动设置参数
def create_args_with_parser():
    parser = argparse.ArgumentParser(description='Generate random flows for NS3 simulation')

    parser.add_argument('--num-flows', type=int, default=10)
    parser.add_argument('--start-time-min', type=float, default=0.0)
    parser.add_argument('--start-time-max', type=float, default=5.0)
    parser.add_argument('--end-time-min', type=float, default=5.0)
    parser.add_argument('--end-time-max', type=float, default=10.0)
    parser.add_argument('--output', type=str, default='flow.txt')

    # 手动设置参数
    args = parser.parse_args([])  # 创建空参数列表
    args.num_flows = 15  # 手动设置值
    args.start_time_min = 1.0
    args.start_time_max = 6.0
    args.end_time_min = 6.0
    args.end_time_max = 12.0
    args.output = 'custom_flow.txt'

    return args

if __name__ == "__main__":
    # 使用方法1：直接创建参数对象
    args = create_args_directly()

    # 或者使用方法2：通过parser手动设置
    # args = create_args_with_parser()

    flows = generate_flows(
        args.num_flows,
        (args.start_time_min, args.start_time_max),
        (args.end_time_min, args.end_time_max),
        (1, 1)
    )

    save_flows(flows, args.output)

    print(f"Generated {args.num_flows} flows and saved to {args.output}")
    # print("\nGenerated flows:")
    # print("Source Port | Destination Port | Priority | Packets | Start Time | End Time")
    # print("-" * 70)
    # for flow in flows:
        # print(f"{flow[0]:11d} | {flow[1]:15d} | {flow[2]:8d} | {flow[3]:7d} | {flow[4]:10.2f} | {flow[5]:8.2f}")