# Building gem5

Please follow this link to find out more on how to download gem5, install dependencies, and build it. 

## Dependencies
For Ubuntu 20.04

    sudo apt install build-essential git m4 scons zlib1g zlib1g-dev \
        libprotobuf-dev protobuf-compiler libprotoc-dev libgoogle-perftools-dev \
        python3-dev python3-six python-is-python3 libboost-all-dev pkg-config

## Download gem5
    git clone https://gem5.googlesource.com/public/gem5
    
## Building with Scons
    scons build/{ISA}/gem5.{variant} -j {cpus}

ISA can be ARM or X86


