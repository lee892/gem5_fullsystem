#!/bin/bash

GEM5_DIR=$(pwd)/../gem5

IMG=$(pwd)/../resources/rootfs.ext2
VMLINUX=$(pwd)/../resources/vmlinux
Bootld=$(pwd)/../boot.arm64

FS_CONFIG=$(pwd)/armFS.py
GEM5_EXE=$GEM5_DIR/build/ARM/gem5.opt

SCRIPT=$(pwd)/rcS/dist/hack_back_ckpt.rcS
NNODES=2

$GEM5_DIR/util/dist/gem5-dist.sh -n $NNODES                     \
                -r $(pwd)/../rundir -c $(pwd)/../ckpts          \
                -s $FS_CONFIG                  			\
                -f $FS_CONFIG                   		\
                -x $GEM5_EXE                    		\
                --fs-args                       		\
                    --kernel=$VMLINUX           		\
                    --disk=$IMG                 		\
                    --bootscript=$SCRIPT        		\
                    --bootloader=$Bootld 			\
                    --cpu=atomic				\
                    --num-cores=4
