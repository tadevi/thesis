set ns [new Simulator]
$ns color 1 Blue
set file [open out.tr w]
$ns trace-all $file
set namfile [open out.nam w]
$ns namtrace-all $namfile

proc finish {} {
    global ns file namfile
    $ns flush-trace
    close $file
    close $namfile
    exec nam out.nam &
    exit 0
}

set n1 [$ns node]
set n2 [$ns node]

$ns duplex-link $n1 $n2 1Mb 5ms DropTail


set source [new Agent/UDP]
$ns attach-agent $n1 $source
$source set fid_ 1

set sink [new Agent/Null]
$ns attach-agent $n2 $sink

$ns connect $source $sink

set cbr [new Application/Traffic/CBR]
$cbr set packet_size_ 1000
$cbr set interval_ 0.01
$cbr attach-agent $source



$ns at 0.5 "$cbr start"
$ns at 4.5 "$cbr stop"

$ns at 5.0 "finish"

$ns run