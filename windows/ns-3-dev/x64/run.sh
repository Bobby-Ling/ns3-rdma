#!/bin/bash

# bash -c "cd mix/simple/ && python gen_flow.py"
# ./main.exe mix/simple/config.txt
# python mix/gen_result.py --config  mix/simple/config.txt --trace mix/simple/mix.tr

NS_LOG="*=logic" ./main.exe mix/small/config.txt
python mix/gen_result.py --config  mix/small/config.txt --trace mix/small/mix.tr