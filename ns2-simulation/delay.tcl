set ns [new Simulator]

set nodes 4

set out [open delay.tr w]


#Open the NAM trace file
set nf [open out.nam w]
$ns namtrace-all $nf

#Open trace file
set tf [open out.tr w]
$ns trace-all $tf

proc finish {} {
        global delay tf ns out
        $ns flush-trace
        #Close the output files
        close $out
        close $tf
        #Call xgraph to display the results
        exec xgraph delay.tr -geometry 800x500 &
        exec nam out.nam &
        exit 0
}

proc record {} {
        global sink out nodes
        #Get an instance of the simulator
        set ns [Simulator instance]
        #Set the time after which the procedure should be called again
        set time 0.5
        #How many bytes have been received by the traffic sinks?

        set total 0
        for {set i 0} {$i < $nodes} {incr i} {
                set bw [$sink($i) set bytes_]
                set total [expr $total + $bw]
        }
        set total [expr $total / $nodes]
        #Get the current time
        set now [$ns now]
        #Calculate the bandwidth (in MBit/s) and write it to the files
        puts $out "$now [expr $total/$time*8/1000000]"

        #Reset the bytes_ values on the traffic sinks
        for {set i 0} {$i < $nodes} {incr i} {
                $sink($i) set bytes_ 0
        }
        #Re-schedule the procedure
        $ns at [expr $now+$time] "record"
}


for {set i 0} {$i < $nodes} {incr i} {
        set n($i) [$ns node]
}

set isp [$ns node]
set cloud [$ns node]

for {set i 0} {$i < $nodes} {incr i} {
       $ns duplex-link $n($i) $isp 12Mb 100ms DropTail
}

$ns duplex-link $isp $cloud 1Gb 300ms DropTail
$ns queue-limit $isp $cloud 10

proc attach-expoo-traffic { node sink size burst idle rate} {
	#Get an instance of the simulator
	set ns [Simulator instance]

	#Create a UDP agent and attach it to the node
	set source [new Agent/UDP]
	$ns attach-agent $node $source

	#Create an Expoo traffic agent and set its configuration parameters

	# set traffic [new Application/Traffic/Exponential]
	# $traffic set packetSize_ $size
	# $traffic set burst_time_ $burst
	# $traffic set idle_time_ $idle
	# $traffic set rate_ $rate

        set traffic [new Application/Traffic/CBR]
        $traffic set packetSize $size
        $traffic set interval_ $burst
        $traffic attach-agent $source
        
    # Attach traffic source to the traffic generator
    $traffic attach-agent $source
	#Connect the source and the sink
	$ns connect $source $sink
	return $traffic
}

for {set i 0} {$i < $nodes} {incr i} {
        set sink($i) [new Agent/LossMonitor]
        $ns attach-agent $cloud $sink($i)
        set source($i) [attach-expoo-traffic $n($i) $sink($i) 0.12M 0.01s 0.01s 400k]
}

        $ns at 0.0 "record"
for {set i 0} {$i < $nodes} {incr i} {
       $ns at 0.1 "$source($i) start"
       $ns at 5.0 "$source($i) stop" 
}

$ns at 6.0 "finish"

$ns run
