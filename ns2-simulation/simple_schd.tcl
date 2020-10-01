# Copyright (C) 1999 by USC/ISI
# All rights reserved.                                            
#                                                                
# Redistribution and use in source and binary forms are permitted
# provided that the above copyright notice and this paragraph are
# duplicated in all such forms and that any documentation, advertising
# materials, and other materials related to such distribution and use
# acknowledge that the software was developed by the University of
# Southern California, Information Sciences Institute.  The name of the
# University may not be used to endorse or promote products derived from
# this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED "AS IS" AND WITHOUT ANY EXPRESS OR IMPLIED
# WARRANTIES, INCLUDING, WITHOUT LIMITATION, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
# 
# An example script that simulates large-scale web traffic. 
# See web-traffic.tcl for a smaller scale web traffic simulation.
#
# This is intended to be a simpler version than the large-scale-web-traffic.tcl
# but consists of more than one objects per page. 
#
# Created by Polly Huang (huang@catarina.usc.edu)
# Modified by Haobo Yu (haoboy@isi.edu)
# Modified by Liang Guo <guol@cs.bu.edu>

# Basic ns setup
set ns [new Simulator]

set nf [open out.nam w]
$ns namtrace-all $nf

#setup colors for nam
for {set i 0} {$i <= 100} {incr i} {
    set color [expr $i % 6]
    if {$color == 0} {
        $ns color $i cyan
    } elseif {$color == 1} {
        $ns color $i red
    } elseif {$color == 2} {
        $ns color $i blue
    } elseif {$color == 3} {
        $ns color $i yellowf
    } elseif {$color == 4} {
        $ns color $i brown
    } elseif {$color == 5} {
        $ns color $i purple
    }
}

proc node_with_classifier { clsfr } {
    global ns

    set nd [$ns node]
    $nd instvar reg_module_

    set mod [new RtModule/Base]
    $mod instvar classifier_
    set classifier_ $clsfr
    $classifier_ set mask_ [AddrParams NodeMask 1]
    $classifier_ set shift_ [AddrParams NodeShift 1]
    # XXX Base should ALWAYS be the first module to be installed.
    $nd install-entry $mod $clsfr

    $mod attach-node $nd
    $nd route-notify $mod
    $nd port-notify $mod

    set reg_module_([$mod module-name]) $mod

    return $nd
}

set cls [new Classifier/Hash/SizeAware 128]
$cls set default_ -1
$cls set flowlen_thr_ 5
$cls set refresh_intv_ 2
$cls set dynamic_update_ 0
set n(0) [node_with_classifier $cls]
$n(0) shape "hexagon"
set n(1) [$ns node]
set n(2) [$ns node]

set s(0) [$ns node]
set s(1) [$ns node]

set r(0) [$ns node]
set r(1) [$ns node]

$ns duplex-link $s(0) $n(0) 1Mb 5ms DropTail
$ns duplex-link-op $s(0) $n(0) orient right-down
$ns duplex-link $s(1) $n(0) 1Mb 5ms DropTail
$ns duplex-link-op $s(1) $n(0) orient right-up

$ns duplex-link $n(0) $n(1) 1Mb 20ms RED/myRIO
$ns duplex-link-op $n(0) $n(1) orient right
$ns duplex-link $n(1) $n(2) 700Kb 25ms RED/myRIO
$ns duplex-link-op $n(1) $n(2) orient right

$ns duplex-link $n(2) $r(0) 1Mb 5ms DropTail
$ns duplex-link $n(2) $r(1) 1Mb 5ms DropTail
$ns duplex-link-op $n(2) $r(0) orient right-up
$ns duplex-link-op $n(2) $r(1) orient right-down

Agent/TCP set packetSize_ 500
Agent/TCP set rtxcur_init_ 1.0
Agent/TCP set window_ 256

Queue/RED/myRIO set gentle_ true
Queue/RED/myRIO set thresh_ 1
Queue/RED/myRIO set maxthresh_ 15
Queue/RED/myRIO set weight_ 10
Queue/RED/myRIO set setbit_ false

set redq [[$ns link $n(1) $n(2)] queue]
$redq set q_weight_ [expr 1.0/2]
$redq set linterm_ [expr 4.0]
$ns queue-limit $n(1) $n(0) 30

proc build-fore-tcp { idx size intv stime } {
	global ns ftcp fsink

	set ftcp($idx) [new Agent/TCP/Newreno]
	set fsink($idx) [new Agent/TCPSink]

	$ns at $stime "start-conn 1 $idx $intv $size"
}

proc start-conn { firsttime idx intv size } {
	global ns ftcp fsink s r

	set now [$ns now]

	if { $firsttime == 0 } {
		$ns detach-agent $s([expr $idx%2]) $ftcp($idx)
		$ns detach-agent $r([expr $idx%2]) $fsink($idx)
		$ftcp($idx) reset
		$fsink($idx) reset
	}
	$ns attach-agent $s([expr $idx%2]) $ftcp($idx)
	$ns attach-agent $r([expr $idx%2]) $fsink($idx)
	$ns connect $ftcp($idx) $fsink($idx)
	$ftcp($idx) set fid_ 0

	$ftcp($idx) proc done {} "close-conn $idx $intv $size"
	$ftcp($idx) advanceby $size
}

proc close-conn { idx intv size } {
	global ns 

	set now [$ns now]
	$ns at [expr $now + $intv] "start-conn 0 $idx $intv $size"
	puts "at $now + $intv start next"
}

set forel_intv 1
set fores_intv 0.05
set ssize 4
set lsize 1000
build-fore-tcp 1 $ssize 1 0.1
build-fore-tcp 0 $lsize $forel_intv 0.5

for {set i 0} {$i < 5} { incr i} {

	build-fore-tcp [expr 2*$i+3] $ssize $fores_intv [expr 1.2+$i*0.1]
}

## Start the simulation
$ns at 4 "finish"

$ns at 0.0 "show-simtime"

proc show-simtime {} {
        global ns
	puts [$ns now]
	$ns at [expr [$ns now]+500.0] "show-simtime"
}

proc finish {} {
	global ns nf
	$ns flush-trace

	close $nf
	exit 0
}

puts "ns started"
$ns run

