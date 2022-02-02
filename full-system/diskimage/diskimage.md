Disk Image
==================

- [Disk Image](#disk-image)
- [Create root filesystem image](#create-root-filesystem-image)
  - [Step 1: Download buildroot source](#step-1-download-buildroot-source)
  - [Step 2: Configure buildroot](#step-2-configure-buildroot)
  - [Step 3: Build the diskimage](#step-3-build-the-diskimage)
  - [Step 4: Add `m5` binary to the root image](#step-4-add-m5-binary-to-the-root-image)
  - [Step 5: Change the startup script](#step-5-change-the-startup-script)
  - [Step 6: Rebuild the diskimage and copy rootfs.ext2 to the resources directory](#step-6-rebuild-the-diskimage-and-copy-rootfsext2-to-the-resources-directory)
- [Advanced diskimage usage](#advanced-diskimage-usage)
  - [Move files to root file system image](#move-files-to-root-file-system-image)
  - [Mount disk image](#mount-disk-image)
  - [Chroot to diskimage](#chroot-to-diskimage)
  - [Increase the size of diskimage](#increase-the-size-of-diskimage)

# Create root filesystem image

Follow the folowing steps to create a buildroot image. Note: you can follow the same steps by accessing (Minimul root filesystem) section in [Running Trusted Firmware-A on gem5](https://community.arm.com/developer/research/b/articles/posts/running-trusted-firmware-a-on-gem5). 


## Step 1: Download buildroot source

    git clone https://github.com/buildroot/buildroot.git -b 2020.05-rc3
    make ARCH=aarch64 BR2_JLEVEL=$(nproc) CROSS_COMPILE=aarch64-linux-gnu- \
        -C buildroot/ arm_foundationv8_defconfig

## Step 2: Configure buildroot

we use `menuconfig` to visually configure the root filesystem image. You probably need to install `ncurses5` package to be able to use `menuconfig`. Please check [buildroot manual](https://buildroot.org/downloads/manual/manual.html) section 2.1 and 2.2 for required packages for buildroot.

    make ARCH=aarch64 BR2_JLEVEL=$(nproc) CROSS_COMPILE=aarch64-linux-gnu- \
        -C buildroot/ menuconfig

Then in the GUI select the following parameter values:

- Target Options
  - Target Architecture Variant -> cortex-A57
- Toolchain
  - Kernel Headers -> Manually specified Linux version
  - linux version -> 5.4
  - Custom kernel headers series -> 5.4.x or later
- Kernel -> Disabled
  - We build the Linux Kernel externally.
- Target packages
  - BusyBox configuration file to use?
    - package/busybox/busybox-minimal.config

## Step 3: Build the diskimage

This step will take a few minutes.

    make ARCH=aarch64 BR2_JLEVEL=$(nproc) CROSS_COMPILE=aarch64-linux-gnu- \
        -C buildroot/


## Step 4: Add `m5` binary to the root image
You should (cross)compile and add m5 binary to the diskimage to be able to use gem5 magic instructions. Take a look at `<gem5_source_dir>/util/m5/README.md` in the gem5 source to find out more info about gem5 magic instructions and their usage. 

Prerequisite packages for arm64 cross compilation:

    sudo apt-get install g++-aarch64-linux-gnu


Cross compiling m5 binary:

    cd <gem5_source_dir>/util/m5
    scons arm64.CROSS_COMPILE=aarch64-linux-gnu- build/arm64/out/m5

Then you should move the compiled m5 binary to the disk image. 

    cp <gem5_source_dir>/util/m5/build/arm64/out/m5 <buildroot_dir>/output/target/sbin


## Step 5: Change the startup script

Once the Linux boot completes, we want to hand over the executing to a simulation script instead of interacting with the simulated Linux using a terminal. In rootfs disk image, after the boot `/etc/init.d/rcS` script execute all the scripts in the `/etc/init.d` folder one by one in numerical order. So we can add an script named `S98` under `/etc/init.d` which gets executed after all other script in there. The following would be the content of S98 if we want to load and execute the specified user script after Linux boot up:

    #!/bin/sh
    echo "Loading new script..."
    /sbin/m5 readfile > /tmp/runscript
    chmod 755 /tmp/runscript
    # Execute the new runscript
    if [ -s /tmp/runscript ]
    then
            /tmp/runscript
    else
        echo "Script not specified. Dropping into shell..."
        /bin/bash
    fi
    echo "Fell through script. Exiting..."
    /sbin/m5 exit

Create S98 script with the above content and copy it to the rootfs image:

    cp S98 <buildroot_dir>/output/target/etc/init.d

We need to do one last thing and update `/etc/inittab` content of the rootfs image to ensure gem5 will execute `/etc/init.d/rcS` right after bootup. You need to modify the content of `<buildroot_dir>/output/target/etc/inittab` to the following:

    ::sysinit:/bin/mount -t proc proc /proc
    ::sysinit:/bin/mkdir -p /dev/pts
    ::sysinit:/bin/mkdir -p /dev/shm
    ::sysinit:/bin/mount -a
    ::sysinit:/bin/hostname -F /etc/hostname
    ::sysinit:/etc/init.d/rcS
    ::respawn:-/bin/sh
    ::ctrlaltdel:/sbin/reboot
    ::shutdown:/etc/init.d/rcK
    ::shutdown:/sbin/swapoff -a
    ::shutdown:/bin/umount -a -r



## Step 6: Rebuild the diskimage and copy rootfs.ext2 to the resources directory

This step will take a few seconds this time.

    cd <buildroot_dir>
    make ARCH=aarch64 BR2_JLEVEL=$(nproc) CROSS_COMPILE=aarch64-linux-gnu-
    mv output/images/rootfs.ext2 <gem5-learning>/resources/



# Advanced diskimage usage
You only need the following for advanced use of diskimages.

## Move files to root file system image
You already did that in [step 4](#step-4-add-m5-binary-to-the-root-image) and [step 5](#step-5-change-the-startup-script) above. All you need to do is to copy files that you need to to `<buildroot_dir>/output/target` and rebuild the diskimage like [step 3](#step-3-build-the-diskimage) above. 

## Mount disk image

    sudo mount -o loop <diskPath>/rootfs.ext2 /mnt


## Chroot to diskimage

You first need to install `qemu` to be able to use chroot into an arm diskimage:

    sudo apt-get install qemu-user-static

Make the emulator available for the arm architecture inside the chroot. We assume that the `rootfs.ext2` is [already mounted](#mount-disk-image):

    sudo cp /usr/bin/qemu-arm-static /target_fs/usr/bin

Then you should be able to `chroot` into the diskimage:

    sudo chroot /mnt /bin/sh 


## Increase the size of diskimage

    dd if=/dev/zero of=disk.img bs=1024k seek=6144 count=0
    mkfs -t ext2 disk.img