#!/bin/bash

NS_LOG="GENERIC_SIMULATION=level_info" LD_LIBRARY_PATH="../../../build:$LD_LIBRARY_PATH" ../../../build/scratch/third config.txt 2>&1 | tee out.txt