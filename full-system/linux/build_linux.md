# Building Linux
Download linux source code and compile it:

    git clone https://github.com/torvalds/linux.git -b v5.4
    make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- -C linux defconfig
    make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- -C linux -j $(nproc)

Then you need to copy the linux binary to `gem5-learning/resources` directory:
    cp linux/vmlinux <gem5-learning>/resources

# Bootloader
There are two different bootloaders for gem5. One of 32-bit kernels and one for 64-bit kernels. They can be compiled using the following command:

    make -C system/arm/bootloader/arm
    make -C system/arm/bootloader/arm64

Then you need to copy the bootloader binary to `gem5-learning/resources` directory:
    cp system/arm/bootloader/arm64/boot.arm64 <gem5-learning>/resources
