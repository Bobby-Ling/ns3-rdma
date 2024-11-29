import sys
import argparse
from pathlib import Path

# 修正相对路径
from pathlib import Path
file_dir = Path(__file__).parent

def read_config_PACKET_PAYLOAD_SIZE(config_path):
    """读取配置文件"""
    with open(config_path, 'r') as file:
        for line in file:
            if line.startswith('PACKET_PAYLOAD_SIZE'):
                return int(line.split(' ')[1].strip())
    return None

def read_config_FLOW_FILE(config_path):
    """读取配置文件"""
    with open(config_path, 'r') as file:
        for line in file:
            if line.startswith('FLOW_FILE'):
                return line.split(' ')[1].strip()
    return None

def read_flow_SIZE(flow_path):
    with open(flow_path, 'r') as file:
        first_line = file.readline()
        return int(first_line.split()[0])
    return None

def read_trace(trace_path):
    """读取跟踪文件"""
    timestamps = []
    sequence_numbers = []
    with open(trace_path, 'r') as file:
        for line in file:
            parts = line.split()
            if len(parts) < 7:
                continue
            timestamps.append(float(parts[0]))
            sequence_numbers.append(int(parts[5]))
    return timestamps, sequence_numbers

def calculate_bandwidths(timestamps, packet_size, time_slot_duration=1e-4):
    """计算每个时隙的带宽"""
    time_slots = []
    bandwidths = []
    current_slot_start = timestamps[0]
    current_slot_packets = 0

    for i in range(len(timestamps)):
        if timestamps[i] < current_slot_start + time_slot_duration:
            current_slot_packets += 1
        else:
            # 计算当前时隙的带宽
            throughput = (current_slot_packets * packet_size * 8) / time_slot_duration / 1e9
            time_slots.append(current_slot_start)
            bandwidths.append(throughput)

            # 移动到下一个时隙
            current_slot_start += time_slot_duration
            current_slot_packets = 1

    # 处理最后一个时隙
    if current_slot_packets > 0:
        throughput = (current_slot_packets * packet_size * 8) / time_slot_duration / 1e9
        time_slots.append(current_slot_start)
        bandwidths.append(throughput)

    return time_slots, bandwidths

def calculate_interval_metrics(time_slots, bandwidths, start_time, end_time):
    """计算指定时间区间的指标"""
    try:
        start_index = next(i for i, t in enumerate(time_slots) if t >= start_time)
        end_index = next(i for i, t in enumerate(time_slots) if t >= end_time)

        specified_bandwidths = bandwidths[start_index:end_index]
        if not specified_bandwidths:
            return 0, 0

        average_bandwidth = sum(specified_bandwidths) / len(specified_bandwidths)
        max_bandwidth = max(specified_bandwidths)
        min_bandwidth = min(specified_bandwidths)
        fluctuation_rate = (max_bandwidth - min_bandwidth) / average_bandwidth

        return average_bandwidth, fluctuation_rate
    except StopIteration:
        return 0, 0

# def get_intervals(timestamps, origin_6400 = False):
#     """根据trace文件的行数确定时间区间"""
#     max_time = timestamps[-1]

#     # 获取trace文件的总行数
#     total_lines = len(timestamps)

#     if origin_6400:  # 原始硬编码的情况
#         return [
#             (1e-4, 5e-3),    # 区间1: 0.1ms-5ms
#             (0.04, 0.06),    # 区间2: 40ms-60ms
#             (0.09, 0.1)      # 区间3: 90ms-100ms
#         ]
#     else:  # 按比例计算新的区间
#         # 将原始区间的比例应用到新的总时间上
#         return [
#             (max_time * 0.001, max_time * 0.042),  # 约对应 0.1ms-5ms
#             (max_time * 0.333, max_time * 0.5),    # 约对应 40ms-60ms
#             (max_time * 0.75, max_time * 0.833)    # 约对应 90ms-100ms
#         ]

def get_intervals(timestamps, origin_6400 = False):
    """根据trace文件的时间戳确定采样区间"""
    max_time = timestamps[-1]

    if origin_6400:  # 原始6400行数据的硬编码情况
        return [
            (1e-4, 5e-3),    # 区间1: 0.1ms-5ms
            (0.04, 0.06),    # 区间2: 40ms-60ms
            (0.09, 0.1)      # 区间3: 90ms-100ms
        ]
    else:
        # 确保时间在3ms到120ms之间
        if max_time < 0.003:  # 小于3ms的情况
            return [(0.001, 0.002), (0.0015, 0.0025), (0.002, 0.003)]

        # 根据最大时间确定区间数量和大小
        if max_time <= 0.02:    # 3ms-20ms
            num_intervals = 5
        elif max_time <= 0.06:  # 20ms-60ms
            num_intervals = 8
        else:                   # 60ms-120ms
            num_intervals = 10

        # 计算区间大小，确保后期有更多采样
        interval_size = max_time / (num_intervals + 2)  # +2是为了留出前后空间

        intervals = []
        # 在整个时间范围内均匀分布区间，但后半段区间更密集
        for i in range(num_intervals):
            # 使用非线性分布，让后面的区间更密集
            progress = (i / (num_intervals - 1)) ** 0.8  # 指数0.8使得后期区间更密集
            start_time = max_time * progress
            end_time = start_time + interval_size

            # 确保end_time不超过最大时间
            end_time = min(end_time, max_time)

            # 只添加有效的区间
            if end_time > start_time:
                intervals.append((start_time, end_time))

        return intervals
def calculate_score(config_path = 'config.txt', trace_path = 'mix.tr'):
    # 读取配置和数据
    packet_payload_size = read_config_PACKET_PAYLOAD_SIZE(config_path)
    packet_size = packet_payload_size + 18
    timestamps, sequence_numbers = read_trace(trace_path)

    # 计算带宽
    time_slots, bandwidths = calculate_bandwidths(timestamps, packet_size)
    average_bandwidth = sum(bandwidths) / len(bandwidths)

    # 根据行数获取适当的时间区间
    intervals = get_intervals(timestamps, read_flow_SIZE(read_config_FLOW_FILE(config_path)) == 6400)

    # 存储每个区间的结果
    results = {}
    for i, (start_time, end_time) in enumerate(intervals, 1):
        avg_bw, fluct = calculate_interval_metrics(time_slots, bandwidths, start_time, end_time)
        results[f'interval_{i}'] = {
            'average_bandwidth': avg_bw,
            'fluctuation_rate': fluct
        }

    # 计算最终得分
    theoretical_bandwidth = 8 * 12 * 25
    bandwidth_utilization = average_bandwidth / theoretical_bandwidth

    num_intervals = len(intervals)
    total_fluctuation = sum(results[f'interval_{i}']['fluctuation_rate'] for i in range(1, num_intervals + 1)) / num_intervals

    final_score = (bandwidth_utilization - total_fluctuation) * 100

    # 输出结果
    print(f"The value of PACKET_PAYLOAD_SIZE is: {packet_payload_size}")
    print(f"Average Bandwidth: {average_bandwidth:.6f} Gbps")

    for i in range(1, len(intervals) + 1):
        interval = results[f'interval_{i}']
        print(f"\nAverage Bandwidth from {intervals[i-1][0]:.6f} s to {intervals[i-1][1]:.6f} s: "
              f"{interval['average_bandwidth']:.6f} Gbps")
        print(f"Fluctuation Rate from {intervals[i-1][0]:.6f} s to {intervals[i-1][1]:.6f} s: "
              f"{interval['fluctuation_rate']:.6f}")

    print(f"\nBandwidth Utilization: {bandwidth_utilization:.6f}")
    print(f"Final Score: {final_score:.2f}")

    # 保存结果
    with open('plot-result.txt', 'w') as file:
        file.write(f'flow_completion_time {timestamps[-1]}\n')
        file.write(f'average_bandwidth {average_bandwidth}\n')
        for i in range(1, len(intervals) + 1):
            file.write(f'fluctuation_rate_{i} {results[f"interval_{i}"]["fluctuation_rate"]}\n')
        file.write(f"\nBandwidth Utilization: {bandwidth_utilization:.6f}\n")
        file.write(f"Final Score: {final_score:.2f}")

    # 返回数据供绘图使用
    return time_slots, bandwidths, intervals

def main():
    # 参数解析
    parser = argparse.ArgumentParser(description='Score Calculator for Network Performance')
    parser.add_argument('--config', type=str, default='config.txt', help='Path to config file')
    parser.add_argument('--trace', type=str, default='mix.tr', help='Path to trace file')
    args = parser.parse_args()

    calculate_score(args.config, args.trace)

if __name__ == '__main__':
    main()