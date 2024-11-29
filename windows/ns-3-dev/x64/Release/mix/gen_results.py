import os
import subprocess
import argparse
import logging
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

# 配置常量
TRACE_FILE_SUFFIX = '.tr'
MAX_WORKERS = 14
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'

class CommandRunner:
    def __init__(self, dry_run=False, log_level=logging.DEBUG):
        self.dry_run = dry_run
        self.setup_logging(log_level)

    def setup_logging(self, log_level):
        """设置日志记录"""
        # 创建logs目录（如果不存在）
        if not os.path.exists('logs'):
            os.makedirs('logs')

        # 生成带时间戳的日志文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = f'logs/command_execution_{timestamp}.log'

        # 配置日志记录器
        logging.basicConfig(
            level=log_level,
            format=LOG_FORMAT,
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()  # 同时输出到控制台
            ]
        )
        logging.info(f"log_level: {log_level}")

    def run_commands_in_directory(self, directory):
        """在指定目录中运行命令"""
        original_dir = os.getcwd()  # 保存当前目录

        try:
            # 切换到目标目录
            os.chdir(directory)
            logging.info(f"Processing directory: {directory}")

            commands = [
                ['python', '../../plot_generator.py', '--no-show'],
                ['python', '../../gen_result.py']
            ]

            for cmd in commands:
                cmd_str = ' '.join(cmd)
                if self.dry_run:
                    logging.info(f"[DRY RUN] Would execute: {cmd_str} in {directory}")
                    continue

                try:
                    logging.info(f"Executing: {cmd_str} in \n\t{directory}")
                    result = subprocess.run(
                        cmd,
                        check=True,
                        capture_output=True,
                        text=True
                    )
                    logging.debug(f"Command output of {cmd_str} in \n\t{directory}:\n{result.stdout}--------------------------------------------\n")
                    if result.stderr:
                        logging.warning(f"Command stderr: {result.stderr}")
                except subprocess.CalledProcessError as e:
                    logging.error(f"Error running {cmd_str} in {directory}: {e}")
                    logging.error(f"Error output: {e.stderr}")
                except Exception as e:
                    logging.error(f"Unexpected error running {cmd_str}: {e}")

        finally:
            # 恢复原始目录
            os.chdir(original_dir)

    def find_trace_directories(self):
        """查找包含.tr文件的目录"""
        trace_dirs = []
        current_dir = os.getcwd()

        for dir_name in os.listdir(current_dir):
            if dir_name.isdigit():
                base_dir = os.path.join(current_dir, dir_name)

                if os.path.isdir(base_dir):
                    logging.info(f"Scanning directory: {dir_name}")

                    for subdir in os.listdir(base_dir):
                        subdir_path = os.path.join(base_dir, subdir)

                        if os.path.isdir(subdir_path):
                            tr_files = [f for f in os.listdir(subdir_path)
                                      if f.endswith(TRACE_FILE_SUFFIX)]
                            if tr_files:
                                trace_dirs.append(subdir_path)
                                logging.info(f"Found trace file in: {subdir_path}")

        return trace_dirs

    def process_directories(self):
        """处理所有符合条件的目录"""
        try:
            trace_dirs = self.find_trace_directories()

            if not trace_dirs:
                logging.warning("No directories with trace files found!")
                return

            logging.debug(f"Found {len(trace_dirs)} directories to process")

            if self.dry_run:
                for directory in trace_dirs:
                    logging.info(f"[DRY RUN] Would process: {directory}")
                return

            # 使用线程池并行处理
            with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                list(executor.map(self.run_commands_in_directory, trace_dirs))

        except Exception as e:
            logging.error(f"An error occurred while processing directories: {e}", exc_info=True)

def main():
    global TRACE_FILE_SUFFIX, MAX_WORKERS
    # 设置命令行参数
    parser = argparse.ArgumentParser(
        description='Run plot_generator.py and gen_result.py in directories containing trace files'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show commands that would be executed without actually running them'
    )
    parser.add_argument(
        '--trace-suffix',
        default=TRACE_FILE_SUFFIX,
        help=f'Specify the trace file suffix (default: {TRACE_FILE_SUFFIX})'
    )
    parser.add_argument(
        '--workers',
        type=int,
        default=MAX_WORKERS,
        help=f'Number of parallel workers (default: {MAX_WORKERS})'
    )
    parser.add_argument(
        '--log-level',
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Set the logging level (default: INFO)'
    )
    args = parser.parse_args()

    # 更新全局常量
    TRACE_FILE_SUFFIX = args.trace_suffix
    MAX_WORKERS = args.workers

    # 创建运行器实例并执行
    runner = CommandRunner(dry_run=args.dry_run, log_level=args.log_level)
    runner.process_directories()

if __name__ == "__main__":
    main()