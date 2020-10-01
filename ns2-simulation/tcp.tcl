# Polly Huang 8-7-98

#source /a/home/netlab1/huang/research/vint/ns-2/tcl/lib/ns-default.tcl

set ns [new Simulator]

$ns color 0 blue
$ns color 1 red

set n0 [$ns node]
set n1 [$ns node]
set n2 [$ns node]
set n3 [$ns node]

set f [open tcp.tr w]
$ns trace-all $f
set nf [open tcp.nam w]
$ns namtrace-all $nf

$ns duplex-link $n0 $n2 5Mb 2ms DropTail
$ns duplex-link $n1 $n2 5Mb 2ms DropTail
$ns duplex-link $n2 $n3 1.5Mb 10ms DropTail
$ns queue-limit $n2 $n3 10

$ns duplex-link-op $n0 $n2 orient right-up
$ns duplex-link-op $n1 $n2 orient right-down
$ns duplex-link-op $n2 $n3 orient right

$ns duplex-link-op $n2 $n3 queuePos 0.5

set tcp [new Agent/TCP]
$tcp set class_ 0
set sink [new Agent/TCPSink]
$ns attach-agent $n0 $tcp
$ns attach-agent $n3 $sink
$ns connect $tcp $sink
# Equivelant of 
# set tcp [$ns create-connection TCP $n0 TCPSink $n3 0]

set ftp [new Application/FTP]
$ftp attach-agent $tcp
$ns at 0.2 "$ftp start"

$ns at 1.2 "$ns detach-agent $n0 $tcp ; $ns detach-agent $n3 $sink"

$ns at 3.0 "finish"

proc finish {} {
	global ns f nf
	$ns flush-trace
	close $f
	close $nf

	puts "running nam..."
	exec nam tcp.nam &
	exit 0
}

$ns run


