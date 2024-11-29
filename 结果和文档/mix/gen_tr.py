import re
import sys

def ip_parse(ip_hex):
    """Convert hex format (0b000101) to x.y format"""
    try:
        # Remove '0b' prefix and convert to integer
        ip_int = int(ip_hex[2:], 16)
        # Extract second and fourth octets
        second = (ip_int >> 16) & 0xFF
        fourth = ip_int & 0xFF
        return f"{second}.{fourth}"
    except:
        return "0.0"

def process_trace(input_file, output_file):
    # Regular expression pattern for line parsing
    pattern = r'(\d+)\s+n:(\d+).*?0b(\w+)\s+0b(\w+)\s+(\d+).*?U\s+(\d+)\s+\d+\s+(\d+)'

    with open(input_file, 'r') as fin, open(output_file, 'w', buffering=8192*1024) as fout:
        for line in fin:
            match = re.search(pattern, line)
            if match:
                # Extract values from regex match
                time, node, src_ip, dst_ip, sport, seq, pg = match.groups()

                # Convert time to seconds with 7 decimal places
                time_s = float(time) / 1e9

                # Write formatted output
                fout.write(f"{time_s:.7f} /{node} {ip_parse(f'0b{src_ip}')}>{ip_parse(f'0b{dst_ip}')} u {sport} {seq} {pg}\n")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py input.tr output.txt")
        sys.exit(1)

    process_trace(sys.argv[1], sys.argv[2])