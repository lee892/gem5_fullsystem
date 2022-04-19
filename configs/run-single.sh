#!/bin/bash

GEM5_DIR=$(pwd)/../gem5

IMG=$(pwd)/../resources/rootfs.ext2
VMLINUX=$(pwd)/../resources/vmlinux
Bootld=$(pwd)/../resources/boot.arm64

FS_CONFIG=$(pwd)/armFS.py
GEM5_EXE=$GEM5_DIR/build/ARM/gem5.opt

SCRIPT=$(pwd)/rcS/single/hack_back_ckpt.rcS
opt="--mem-type=DRAMSim2 --dramsim-config=ini/DDR3_micron_64M_8B_x4_sg15.ini --dramsim-filepath=$(pwd)/../gem5/ext/dramsim2/DRAMSim2 --cpu=timing"
#debug="--debug-flags=AddrRanges,DRAMsim3 "

$GEM5_EXE $debug $FS_CONFIG 						\
                    --kernel=$VMLINUX           		\
                    --disk=$IMG                 		\
                    --bootscript=$SCRIPT        		\
                    --bootloader=$Bootld 			\
                    --cpu=atomic				\
                    --num-cores=4 $opt

