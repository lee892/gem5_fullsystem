#!/bin/bash

GEM5_DIR=$(pwd)/../gem5

IMG=$(pwd)/../resources/rootfs.ext2
VMLINUX=$(pwd)/../resources/vmlinux
Bootld=$(pwd)/../resources/boot.arm64

FS_CONFIG=$(pwd)/armFS.py
GEM5_EXE=$GEM5_DIR/build/ARM/gem5.opt

SCRIPT=$(pwd)/rcS/single/hack_back_ckpt.rcS
NNODES=2

$GEM5_EXE $FS_CONFIG 						\
                    --kernel=$VMLINUX           		\
                    --disk=$IMG                 		\
                    --bootscript=$SCRIPT        		\
                    --bootloader=$Bootld 			\
                    --cpu=atomic				\
                    --num-cores=4
