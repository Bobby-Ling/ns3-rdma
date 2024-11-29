import matplotlib.pyplot as plt
from collections import Counter


def parse_and_count_dst(filename):
    dst_counts = []

    with open(filename, "r") as f:
        # 读取第一行（flow数量）
        total_flows = int(f.readline().strip())

        # 只读取指定数量的行
        for _ in range(total_flows):
            line = f.readline().strip()
            if not line:  # 防止意外的空行
                break

            parts = line.split()
            if len(parts) >= 2:
                dst = int(parts[1])
                dst_counts.append(dst)

    return dst_counts


def plot_dst_line_chart(dst_counts):
    # 使用Counter统计dst出现次数
    dst_frequency = Counter(dst_counts)

    plt.figure(figsize=(20, 8))

    # 排序的dst和对应频率
    sorted_dsts = sorted(dst_frequency.items(), key=lambda x: x[0])
    dsts, frequencies = zip(*sorted_dsts)

    # 折线图 - 精确到每个dst
    plt.plot(dsts, frequencies, marker='o', linestyle='-', linewidth=2, markersize=6)
    plt.title('Destination Node Frequency', fontsize=15)
    plt.xlabel('Destination Node', fontsize=12)
    plt.ylabel('Frequency', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)

    # 调整x轴刻度，防止重叠
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    # plt.savefig('dst_line_distribution.png', dpi=300)
    plt.show()

    # 打印统计信息
    print("\n--- Destination Node Statistics ---")
    for dst, count in sorted_dsts:
        print(f"Dst {dst}: {count} times ({count/len(dst_counts)*100:.2f}%)")

    print(f"\nTotal unique destinations: {len(dst_frequency)}")
    print(f"Total flows: {len(dst_counts)}")

    return dst_frequency


def main(filename):
    dst_counts = parse_and_count_dst(filename)
    plot_dst_line_chart(dst_counts)


# 使用示例
main("flow.txt")
