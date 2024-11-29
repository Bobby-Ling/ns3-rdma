# %%
def generate_topology():
    """
    生成四层Fat-tree拓扑结构的topology.txt文件
    基于华为网络架构图的具体配置
    """
    # 基础参数定义
    compute_nodes = 160  # 计算节点，每个2×25G
    storage_nodes = 8  # 存储节点，每个12×25G

    # 每个节点的端口数
    compute_ports = compute_nodes * 2  # 320个计算端口
    storage_ports = storage_nodes * 12  # 96个存储端口
    total_end_ports = compute_ports + storage_ports  # 416个终端端口

    # 交换机数量
    l1_switches = 28  # L1层交换机
    l2_switches = 28  # L2层交换机
    l3_switches = 24  # L3层交换机
    l4_switches = 12  # L4层交换机
    total_switches = l1_switches + l2_switches + l3_switches + l4_switches

    # 总节点数（所有端口+所有交换机）
    total_nodes = total_end_ports + total_switches

    # 计算总链路数
    # 计算节点链路 + 存储节点链路 + L1到L2链路 + L2到L3链路 + L3到L4链路
    total_links = (
        (compute_ports)
        + (storage_ports)
        + (l1_switches * 16)
        + (l2_switches * 8)
        + (l3_switches * 8)
    )

    content = []

    # 第一行：总节点数 交换机数 链路数
    content.append(f"{total_nodes} {total_switches} {total_links}")

    # 第二行：交换机节点ID列表
    switch_start = total_end_ports
    switch_ids = list(range(switch_start, switch_start + total_switches))
    content.append(" ".join(map(str, switch_ids)))

    # 生成链路连接
    current_port = 0

    # 1. 计算节点到L1交换机的连接
    for i in range(compute_nodes):
        for j in range(2):  # 每个计算节点2个端口
            l1_sw = switch_start + (current_port // 16)
            content.append(f"{current_port} {l1_sw} 25Gbps 1us 0")
            current_port += 1

    # 2. 存储节点到L1交换机的连接
    for i in range(storage_nodes):
        for j in range(12):  # 每个存储节点12个端口
            l1_sw = switch_start + (current_port // 12)
            content.append(f"{current_port} {l1_sw} 25Gbps 1us 0")
            current_port += 1

    # 3. L1到L2的连接
    l2_start = switch_start + l1_switches
    for i in range(l1_switches):
        for j in range(16):  # 每个L1交换机16个上行端口
            l2_index = (i // 4) * 4 + (j % 4)
            content.append(f"{switch_start + i} {l2_start + l2_index} 25Gbps 1us 0")

    # 4. L2到L3的连接
    l3_start = l2_start + l2_switches
    for i in range(l2_switches):
        for j in range(8):  # 每个L2交换机8个上行端口
            l3_index = (i // 8) * 6 + (j % 6)
            content.append(f"{l2_start + i} {l3_start + l3_index} 25Gbps 1us 0")

    # 5. L3到L4的连接
    l4_start = l3_start + l3_switches
    for i in range(l3_switches):
        for j in range(8):  # 每个L3交换机8个上行端口
            l4_index = (i // 6) * 3 + (j % 3)
            content.append(f"{l3_start + i} {l4_start + l4_index} 25Gbps 1us 0")

    return "\n".join(content)


def write_topology_file(filename="./topology.txt"):
    """
    将生成的拓扑结构写入文件
    """
    topology_content = generate_topology()
    with open(filename, "w") as f:
        f.write(topology_content)
        f.write("\n\n")
        f.write("First line: total node #, switch node #, link #\n")
        f.write("Second line: switch node IDs...\n")
        f.write("src1 dst1 rate delay error_rate\n")
        f.write("...")


# %%
if __name__ == "__main__":
    write_topology_file()

# %%
