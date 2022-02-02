gem5 Learning
==================
This repo is trying to create a systematic way for learning gem5 at all levels, from beginners to advanced users.


- [gem5 Learning](#gem5-learning)
- [Full System (FS) Simulation for ARM](#full-system-fs-simulation-for-arm)
  - [Step 1: Download and compile gem5](#step-1-download-and-compile-gem5)
  - [Step 2: Prepare a diskimage, Linux kernel binary, and bootloader](#step-2-prepare-a-diskimage-linux-kernel-binary-and-bootloader)
    - [Step 2.1: Diskimage](#step-21-diskimage)
    - [Step 2.2: Linux kernel](#step-22-linux-kernel)
    - [Step 2.3: Bootloader](#step-23-bootloader)
- [Step  3: Run Simulation](#step--3-run-simulation)
  - [Single Node Simulation](#single-node-simulation)
  - [Dist Simulation](#dist-simulation)
  - [rcS script](#rcs-script)
  - [Restore from a checkpoint](#restore-from-a-checkpoint)


# Full System (FS) Simulation for ARM

Steps for preparing for a FS mode simulation:
## Step 1: Download and compile gem5

Follow the steps in [Download and build gem5](docs/build.md) to download and build gem5. Here is where gem5 source should be placed in the directory tree:

```
gem5-learning
 ┗ gem5
```

## Step 2: Prepare a diskimage, Linux kernel binary, and bootloader

Follow steps 2.1-2.3 and create a "resources" directory and move the diskimage, linux kernel binary, and bootloader there. Now the repository tree include "gem5" and "resources":

```

gem5-learning
 ┣ resources
 ┃ ┣ boot.arm64
 ┃ ┣ vmlinux
 ┃ ┗ rootfs.ext2
 ┗ gem5

```

### Step 2.1: Diskimage

Follow the steps in [Create diskimage](full-system/diskimage/diskimage.md) to prepare a diskimage.

### Step 2.2: Linux kernel

Follow the steps in [Build Linux](full-system/linux/build_linux.md) to download and compile linux kernel. 

### Step 2.3: Bootloader
Follow the steps in [Build bootloader](full-system/linux/build_linux.md#Bootloader) to create a bootloader. 


# Step  3: Run Simulation

Now everything is ready for running a simulation. There are two ready to use run scripts for single node simulation and multi-node (dist) simulation.

## Single Node Simulation

    cd configs
    bash run-single.sh

## Dist Simulation

dist-gem5 can be used to simulate a multi-node computer cluster. The following script will simulate a 2-node client-server setup.

    cd configs
    bash run-dist.sh

## rcS script

The way that we interact with a simulated system in FS mode is through `rcS` scripts. You can specify an `rcS` script using the `--bootscript` option in `armFS.py`. One best practice for FS simulation is to boot linux with atomic CPU and then take a checkpoint and exit. Then, restore from the checkponit, load a new script that contains the actual application that you want to simulation with a detailed CPU. The `configs/rcS/*/hack_back_ckpt.rcS` does this for you.

Note that you need to [move applications to the diskimage](full-system/diskimage/diskimage.md#move-files-to-root-file-system-image) before you run any application. 

## Restore from a checkpoint

After a checkpoint is taken, you can restore from the checkpoint by specifying the location of the checkpoint directory using `checkpoint-dir` option. You should pass `--restore` option to restore from the specified checkpoint. 

