	
#Create a simulator object
set ns [new Simulator]
 
 
#Open the NAM trace file
set nf [open out.nam w]
$ns namtrace-all $nf

#Open trace file
set tf [open out.tr w]
$ns trace-all $tf
 

$ns color 1 Blue
$ns color 2 Red
$ns color 3 Yellow
$ns color 4 Green

#Define a 'finish' procedure
proc finish {} {
 global ns nf tf
 $ns flush-trace
 #Close the NAM trace file
 close $tf
 close $nf
 #Execute NAM on the trace file
 exec nam out.nam &
 #exec xgraph out.tr -geometry 800x800 &
 exit 0
}

#                       cloud        
#
#                       router
#       
#           fog1                       fog2
#
#      node1    node2           node3      node4

#  paramters simulate:
#     n_layer: numbers of layer
#     n_factor: [array of factor]
#


# create edge nodes
for {set i 0} {$i < 4} {incr i} {
    set n($i) [$ns node]
}

# create fog nodes
for {set i 0} {$i < 2} {incr i} {
    set f($i) [$ns node]
}

# create cloud fogs
set router [$ns node]
$router shape "hexagon"

set cloud [$ns node]


# create link between nodes
$ns duplex-link $n(0) $f(0) 1Mb 10ms DropTail
$ns duplex-link $n(1) $f(0) 1Mb 10ms DropTail

$ns duplex-link $n(2) $f(1) 1Mb 10ms DropTail
$ns duplex-link $n(3) $f(1) 1Mb 10ms DropTail

$ns duplex-link $f(0) $router 2Mb 10ms DropTail
$ns duplex-link $f(1) $router 2Mb 10ms DropTail

$ns duplex-link $router $cloud 3Mb 20ms DropTail
$ns queue-limit $router $cloud 10

# cloud only receive packet
set null [new Agent/Null]
$ns attach-agent $cloud $null

# monitor queue
$ns duplex-link-op $router $cloud queuePos 0.5


# attach cbr to edge nodes
for {set i 0} {$i < [array size n]} {incr i} {
        set udp($i) [new Agent/UDP]
        $ns attach-agent $n($i) $udp($i)
        $ns connect $udp($i) $null
        $udp($i) set fid_ [expr $i + 1]

        set cbr($i) [new Application/Traffic/CBR]
        $cbr($i) attach-agent $udp($i)
        $cbr($i) set type_ CBR
        $cbr($i) set packet_size_ 1000
        $cbr($i) set rate_ 1mb
        $cbr($i) set random_ true
}

# schedule event 
for {set i 0} {$i < [array size n]} {incr i} {
        $ns at [expr 0.1 * ($i + 1)] "$cbr($i) start"
        $ns at 5 "$cbr($i) stop"
}

$ns at 5.0 "finish"
 
#Print CBR packet size and interval
for {set i 0} {$i < [array size n]} {incr i} {
        puts "CBR packet size = [$cbr($i) set packet_size_]"
        puts "CBR interval = [$cbr($i) set interval_]"
}
 

$ns run