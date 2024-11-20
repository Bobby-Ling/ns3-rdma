#python gen_result.py --config config.txt --trace mix.tr

import matplotlib.pyplot as plt
import configparser
import argparse

# 创建参数解析器
parser = argparse.ArgumentParser(description='Configuration File Reader')
parser.add_argument('--config', type=str, required=True, help='Path to the configuration file')
parser.add_argument('--trace', type=str, required=True, help='Path to the trace file')

# 解析命令行参数
args = parser.parse_args()

# 读取配置文件
with open(args.config, 'r') as file:
    for line in file:
        if line.startswith('PACKET_PAYLOAD_SIZE'):
            # 获取等号后的数值
            packet_payload_size = int(line.split(' ')[1].strip())
            break

print(f"The value of PACKET_PAYLOAD_SIZE is: {packet_payload_size}")

# 初始化变量
timestamps = []
sequence_numbers = []
packet_size = packet_payload_size + 18  # 每个数据包的大小，单位为字节

# 读取数据文件
with open(args.trace, 'r') as file:
    for line in file:
        parts = line.split()
        if len(parts) < 7:
            continue
        timestamps.append(float(parts[0]))
        sequence_numbers.append(int(parts[5]))

# 计算每个时隙的带宽
time_slots = []
bandwidths = []
time_slot_duration = 1e-4  # 时隙的持续时间，单位为秒
current_slot_start = timestamps[0]
current_slot_packets = 0

for i in range(len(timestamps)):
    if timestamps[i] < current_slot_start + time_slot_duration:
        current_slot_packets += 1
    else:
        # 计算当前时隙的带宽
        throughput = (current_slot_packets * packet_size * 8) / time_slot_duration / 1e9  # 带宽单位为 Gbps
        time_slots.append(current_slot_start)
        bandwidths.append(throughput)

        # 移动到下一个时隙
        current_slot_start += time_slot_duration
        current_slot_packets = 0

# 计算平均带宽
average_bandwidth = sum(bandwidths) / len(bandwidths)
print(f'Average Bandwidth: {average_bandwidth:.6f} Gbps')

# 计算指定时间区间后的平均带宽和波动率
start_time_1 = 1e-4  # 区间起始时间，单位为秒
end_time_1 = 5e-3 # 区间结束时间，单位为秒

start_index = next(i for i, t in enumerate(time_slots) if t >= start_time_1)
end_index = next(i for i, t in enumerate(time_slots) if t >= end_time_1)

specified_bandwidths = bandwidths[start_index:end_index]
specified_average_bandwidth_1 = sum(specified_bandwidths) / len(specified_bandwidths)
specified_max_bandwidth = max(specified_bandwidths)
specified_min_bandwidth = min(specified_bandwidths)
print(specified_max_bandwidth, specified_min_bandwidth)
fluctuation_rate_1 = (specified_max_bandwidth - specified_min_bandwidth) / specified_average_bandwidth_1

print(f'Average Bandwidth from {start_time_1:.6f} s to {end_time_1:.6f} s: {specified_average_bandwidth_1:.6f} Gbps')
print(f'Fluctuation Rate from {start_time_1:.6f} s to {end_time_1:.6f} s: {fluctuation_rate_1:.6f}')


# 计算指定时间区间后的平均带宽和波动率
start_time_2 = 0.04  # 区间起始时间，单位为秒
end_time_2 = 0.06 # 区间结束时间，单位为秒

start_index = next(i for i, t in enumerate(time_slots) if t >= start_time_2)
end_index = next(i for i, t in enumerate(time_slots) if t >= end_time_2)

specified_bandwidths = bandwidths[start_index:end_index]
specified_average_bandwidth_2 = sum(specified_bandwidths) / len(specified_bandwidths)
specified_max_bandwidth = max(specified_bandwidths)
specified_min_bandwidth = min(specified_bandwidths)
fluctuation_rate_2 = (specified_max_bandwidth - specified_min_bandwidth) / specified_average_bandwidth_2

print(f'Average Bandwidth from {start_time_2:.6f} s to {end_time_2:.6f} s: {specified_average_bandwidth_2:.6f} Gbps')
print(f'Fluctuation Rate from {start_time_2:.6f} s to {end_time_2:.6f} s: {fluctuation_rate_2:.6f}')

# 计算指定时间区间后的平均带宽和波动率
start_time_3 = 0.09  # 区间起始时间，单位为秒
end_time_3 = 0.1 # 区间结束时间，单位为秒

start_index = next(i for i, t in enumerate(time_slots) if t >= start_time_3)
end_index = next(i for i, t in enumerate(time_slots) if t >= end_time_3)

specified_bandwidths = bandwidths[start_index:end_index]
specified_average_bandwidth_3 = sum(specified_bandwidths) / len(specified_bandwidths)
specified_max_bandwidth = max(specified_bandwidths)
specified_min_bandwidth = min(specified_bandwidths)
fluctuation_rate_3 = (specified_max_bandwidth - specified_min_bandwidth) / specified_average_bandwidth_3

print(f'Average Bandwidth from {start_time_3:.6f} s to {end_time_3:.6f} s: {specified_average_bandwidth_3:.6f} Gbps')
print(f'Fluctuation Rate from {start_time_3:.6f} s to {end_time_3:.6f} s: {fluctuation_rate_3:.6f}')

with open('result.txt', 'w') as file:
    file.write(f'flow_completion_time {timestamps[-1]}\n')
    file.write(f'average_bandwidth {average_bandwidth}\n')
    file.write(f'fluctuation_rate_1 {fluctuation_rate_1}\n')
    file.write(f'fluctuation_rate_2 {fluctuation_rate_2}\n')
    file.write(f'fluctuation_rate_3 {fluctuation_rate_3}\n')