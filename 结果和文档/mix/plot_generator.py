import argparse
import matplotlib.pyplot as plt
import numpy as np
from score_calculator import calculate_score

def determine_sample_interval(time_slots, min_samples=100, max_samples=500):
    """
    根据数据量自动确定合适的采样间隔
    
    参数:
    time_slots: 时间序列数据
    min_samples: 最少期望的采样点数
    max_samples: 最多期望的采样点数
    
    返回:
    sample_interval: 建议的采样间隔
    """
    total_time = time_slots[-1] - time_slots[0]
    data_points = len(time_slots)

    # 计算原始数据的平均时间间隔
    avg_interval = total_time / (data_points - 1)

    # 根据数据量确定合适的采样间隔
    if data_points < min_samples:
        # 数据点较少时，使用原始间隔
        return avg_interval
    elif data_points > max_samples:
        # 数据点较多时，增加采样间隔
        return total_time / max_samples
    else:
        # 数据点适中时，使用原始间隔
        return avg_interval

def plot_metrics(time_slots, bandwidths, intervals, show_plot=True):
    """生成带宽和波动率随时间变化的图"""
    def calculate_window_metrics(start_time, window_size):
        """计算窗口内的指标"""
        try:
            start_index = next(i for i, t in enumerate(time_slots) if t >= start_time)
            end_index = next(i for i, t in enumerate(time_slots) if t >= start_time + window_size)

            window_bandwidths = bandwidths[start_index:end_index]
            if not window_bandwidths:
                return 0, 0

            avg_bandwidth = sum(window_bandwidths) / len(window_bandwidths)
            if avg_bandwidth == 0:
                return 0, 0

            max_bandwidth = max(window_bandwidths)
            min_bandwidth = min(window_bandwidths)
            fluctuation_rate = (max_bandwidth - min_bandwidth) / avg_bandwidth

            return avg_bandwidth, fluctuation_rate
        except StopIteration:
            return 0, 0

    # 确定采样间隔
    sample_interval = determine_sample_interval(time_slots)
    window_size = sample_interval * 2  # 设置窗口大小为采样间隔的2倍

    # 采样计算
    max_time = time_slots[-1]
    min_time = time_slots[0]
    sample_points = np.arange(min_time, max_time, sample_interval)

    # 打印采样信息
    print(f"\nPlotting information:")
    print(f"Total time range: {min_time:.6f}s to {max_time:.6f}s")
    print(f"Number of original data points: {len(time_slots)}")
    print(f"Selected sample interval: {sample_interval:.6f}s")
    print(f"Number of sampling points: {len(sample_points)}")

    sample_bandwidths = []
    sample_fluctuations = []

    for t in sample_points:
        avg_bw, fluct = calculate_window_metrics(t, window_size)
        sample_bandwidths.append(avg_bw)
        sample_fluctuations.append(fluct)

    # 创建图表
    plt.figure(figsize=(12, 8))

    # 带宽随时间变化
    plt.subplot(2, 1, 1)
    plt.plot(sample_points * 1000, sample_bandwidths, 'b-', linewidth=1, label='Bandwidth')
    plt.title('Bandwidth over Time')
    plt.xlabel('Time (ms)')
    plt.ylabel('Bandwidth (Gbps)')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.ylim(bottom=0)

    # 添加平均带宽线
    avg_bw = sum(bandwidths) / len(bandwidths)
    plt.axhline(y=avg_bw, color='r', linestyle='--', alpha=0.5, label=f'Avg: {avg_bw:.2f} Gbps')
    plt.legend()

    # 波动率随时间变化
    plt.subplot(2, 1, 2)
    plt.plot(sample_points * 1000, sample_fluctuations, 'r-', linewidth=1, label='Fluctuation Rate')
    plt.title('Fluctuation Rate over Time')
    plt.xlabel('Time (ms)')
    plt.ylabel('Fluctuation Rate')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.ylim(bottom=0)

    # 添加平均波动率线
    avg_fluct = sum(sample_fluctuations) / len(sample_fluctuations)
    plt.axhline(y=avg_fluct, color='b', linestyle='--', alpha=0.5, label=f'Avg: {avg_fluct:.2f}')
    plt.legend()

    # 突出显示三个关键时间区间
    # key_intervals = [
    #     (0.1, 5),    # 0.1ms-5ms
    #     (40, 60),    # 40ms-60ms
    #     (90, 100)    # 90ms-100ms
    # ]
    key_intervals = [(start * 1000, end * 1000) for start, end in intervals]

    colors = [
        'lightblue',    # 浅蓝
        'lightgreen',   # 浅绿
        'lightsalmon',  # 浅橙红
        'lightpink',    # 浅粉
        'plum',         # 梅红
        'peachpuff',    # 桃色
        'paleturquoise',# 淡绿松石
        'khaki',        # 卡其色
        'bisque',       # 橘黄
        'lavender',     # 薰衣草紫
        'wheat',        # 小麦色
        'palegreen',    # 淡绿
        'powderblue',   # 粉蓝
        'moccasin',     # 鹿皮色
        'thistle',      # 蓟色
        'lightyellow',  # 浅黄
        'azure',        # 天蓝
        'lemonchiffon', # 柠檬雪纺
        'mistyrose',    # 玫瑰褐
        'honeydew'      # 蜜瓜色
    ]
    alpha = 0.2

    for (ax1, ax2) in [(plt.subplot(211), plt.subplot(212))]:
        for i, (start, end) in enumerate(key_intervals):
            ax1.axvspan(start, end, color=colors[i], alpha=alpha,
                       label=f'Interval {i+1}: {start:.1f}-{end:.1f}ms')
            ax2.axvspan(start, end, color=colors[i], alpha=alpha)
        ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        ax2.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    plt.tight_layout()
    plt.savefig('bandwidth_fluctuation.png', dpi=300, bbox_inches='tight')
    if show_plot:
        plt.show()
    plt.close()

def main():
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='带宽波动率分析')
    parser.add_argument('--no-show', action='store_true',
                      help='不显示图表界面')
    args = parser.parse_args()

    time_slots, bandwidths, intervals = calculate_score()

    # 生成图表，根据no-show参数决定是否显示
    plot_metrics(time_slots, bandwidths, intervals, show_plot=not args.no_show)

if __name__ == '__main__':
    main()