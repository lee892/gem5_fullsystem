# Copyright (c) 2016 Jason Lowe-Power
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met: redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer;
# redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution;
# neither the name of the copyright holders nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
import argparse
import sys
import os

import m5
import m5.ticks
from m5.objects import *

from x86.system import *

m5.util.addToPath("../gem5/configs/dist")
m5.util.addToPath("../gem5/configs")
import sw


def addOptions(parser):
   # Options for distributed simulation (i.e. dist-gem5)
    parser.add_argument("--dist", action="store_true", help="Distributed gem5"\
                      " simulation.")
    parser.add_argument("--is-switch", action="store_true",
                        help="Select the network switch simulator process for"\
                      " a distributed gem5 run.")
    parser.add_argument("--dist-rank", default=0, action="store", type=int,
                      help="Rank of this system within the dist gem5 run.")
    parser.add_argument("--dist-size", default=0, action="store", type=int,
                      help="Number of gem5 processes within the dist gem5"\
                      " run.")
    parser.add_argument("--dist-server-name",
                      default="127.0.0.1",
                      action="store", type=str,
                      help="Name of the message server host\nDEFAULT:"\
                      " localhost")
    parser.add_argument("--dist-server-port",
                      default=2200,
                      action="store", type=int,
                      help="Message server listen port\nDEFAULT: 2200")
    parser.add_argument("--dist-sync-repeat",
                      default="0us",
                      action="store", type=str,
                      help="Repeat interval for synchronisation barriers"\
                      " among dist-gem5 processes\nDEFAULT:"\
                      " --ethernet-linkdelay")
    parser.add_argument("--dist-sync-start",
                      default="1000000000000t",
                      action="store", type=str,
                      help="Time to schedule the first dist synchronisation"\
                      " barrier\nDEFAULT:1000000000000t")
    parser.add_argument("--ethernet-linkspeed", default="10Gbps",
                        action="store", type=str,
                        help="Link speed in bps\nDEFAULT: 10Gbps")
    parser.add_argument("--ethernet-linkdelay", default="10us",
                      action="store", type=str,
                      help="Link delay in seconds\nDEFAULT: 10us")
    parser.add_argument("--etherdump", action="store", type=str, default="",
                        help="Specify the filename to dump a pcap capture of"\
                        " the ethernet traffic")
    # Used by util/dist/gem5-dist.sh
    parser.add_argument("--checkpoint-dir", type=str,
                        default=m5.options.outdir,
                        help="Directory to save/read checkpoints")

    # non dist-gem5 options
    parser.add_argument("--kernel", type=str,
                        help="Linux kernel")
    parser.add_argument("--disk", type=str, default="",
                        help="Disk")
    parser.add_argument("--bootscript", action="append", type=str, default=[],
                        help="Linux bootscripts")
    parser.add_argument("--cpu-type", type=str,
                        default="atomic",
                        help="CPU simulation mode. Default: %(default)s")
    parser.add_argument("--num-cpus", type=int, default=1,
                        help="Number of CPUs to instantiate")
    parser.add_argument("--cpu-clock", type=str, default="3GHz",
                        help="CPU clock frequency")
    parser.add_argument("--restore-from", action="store_true",
                                    help="Restore from checkpoint")
    parser.add_argument("--dual", action="store_true", help="Dual mode gem5"\
                      " simulation.")

def addDistEthernet(root, options):
    # create distributed ethernet link
    root.system.etherlink = DistEtherLink(speed = options.ethernet_linkspeed,
                                     delay = options.ethernet_linkdelay,
                                     dist_rank = options.dist_rank,
                                     dist_size = options.dist_size,
                                     server_name = options.dist_server_name,
                                     server_port = options.dist_server_port,
                                     sync_start = options.dist_sync_start,
                                     sync_repeat = options.dist_sync_repeat)

    root.system.etherlink.int0 = root.system.pc.south_bridge.ethernet.interface

def buildDist(options):
    if options.is_switch:
        root = Root(full_system = True,
                    system = sw.build_switch(options))
    else:
        root = Root(full_system = True)
        root.system =  CompleteX86System(options) #.kernel, options.disk, options.cpu_type, options.num_cpus)
        addDistEthernet(root, options)
        root.system.readfile = options.bootscript[0]

    # instantiate all of the objects we've created above
    if options.restore_from is not None:
        m5.instantiate(options.checkpoint_dir)
    else:
        m5.instantiate()

    print("Running the simulation")
    exit_event = m5.simulate()

    # Handle exit condtions
    if (exit_event.getCause()) == "checkpoint":
        print("Taking Checkpoint")
        m5.checkpoint(options.checkpoint_dir)
        print("Success!")
    elif exit_event.getCause() != "m5_exit instruction encountered":
        print(exit_event.getCause())
        exit(1)
    else:
        print("Success!")
        exit(0)



def buildDual(options):
    root = Root(full_system = True)
    root.testsys =  CompleteX86System(options.kernel, options.disk, options.cpu_type, options.num_cpus)
    root.drivesys =  CompleteX86System(options.kernel, options.disk, options.cpu_type, options.num_cpus)
    root.etherlink = EtherLink(speed = options.ethernet_linkspeed,
                               delay = options.ethernet_linkdelay)
    root.etherlink.int0 = root.testsys.pc.south_bridge.ethernet.interface
    root.etherlink.int1 = root.drivesys.pc.south_bridge.ethernet.interface

    root.testsys.readfile = options.bootscript[0]
    root.drivesys.readfile = options.bootscript[1]

    # instantiate all of the objects we've created above
    if options.restore_from is not None:
        m5.instantiate(options.checkpoint_dir)
    else:
        m5.instantiate()

    print("Running the simulation")
    exit_event = m5.simulate()

    # Handle exit condtions
    if (exit_event.getCause()) == "checkpoint":
        print("Taking Checkpoint")
        m5.checkpoint(options.checkpoint_dir)
        print("Success!")
    elif exit_event.getCause() != "m5_exit instruction encountered":
        print(exit_event.getCause())
        exit(1)
    else:
        print("Success!")
        exit(0)

def buildSingle(options):
    root = Root(full_system = True)
    root.testsys =  CompleteX86System(options.kernel, options.disk, options.cpu_type, options.num_cpus)

    root.testsys.readfile = options.bootscript[0]

    # instantiate all of the objects we've created above
    if options.restore_from is not None:
        m5.instantiate(options.checkpoint_dir)
    else:
        m5.instantiate()

    print("Running the simulation")
    exit_event = m5.simulate()

    # Handle exit condtions
    if (exit_event.getCause()) == "checkpoint":
        print("Taking Checkpoint")
        m5.checkpoint(options.checkpoint_dir)
        print("Success!")
    elif exit_event.getCause() != "m5_exit instruction encountered":
        print(exit_event.getCause())
        exit(1)
    else:
        print("Success!")
        exit(0)

def main():
    parser = argparse.ArgumentParser(
        description="X86 configuration with dist-gem5 support")
    addOptions(parser)
    options = parser.parse_args()

    if options.dist or options.is_switch:
        buildDist(options)
    elif options.dual:
        buildDual(options)
    else:
        buildSingle(options)

main()
