# Example gem5 Configuration Files

We assume to have to following file structure for simulations:


```
gem5-learning
 ┣ configs
 ┃ ┣ arm
 ┃ ┃ ┗ system.py
 ┃ ┣ x86
 ┃ ┃ ┗ system.py
 ┃ ┣ armFS.py
 ┃ ┣ x86FS.py
 ┃ ┣ run-dist.sh
 ┃ ┣ run-single.sh
 ┃ ┗ rcS
 ┃   ┣ dist
 ┃   ┃  ┗ hack_back_ckpt.rcS
 ┃   ┗ single
 ┃      ┗ hack_back_ckpt.rcS
 ┣ resources
 ┃ ┣ boot.arm64
 ┃ ┣ vmlinux
 ┃ ┗ rootfs.ext2
 ┗ gem5

```