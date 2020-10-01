	
#Create a simulator object
set n_cameras 10
set n_sink 4


set ns [new Simulator]
 
 
#Open the NAM trace file
set nf [open out.nam w]
$ns namtrace-all $nf

#Open trace file
set tf [open out.tr w]
$ns trace-all $tf


for {set i 0} {$i < $n_sink} {incr i} {
        set f($i) [open "trace$i.tr" w]
}


proc record {} {
        global udp ns f sink n_cameras n_sink
        #Set the time after which the procedure should be called again
        set time 0.5
        #How many bytes have been received by the traffic sinks?
        for {set i 0} {$i < $n_sink} {incr i} {
        set bw($i) [$sink($i) set bytes_]
        }
        #Get the current time
        set now [$ns now]
        #Calculate the bandwidth (in MBit/s) and write it to the files
        for {set i 0} {$i < $n_sink} {incr i} {
        puts $f($i) "$now [expr $bw($i)/$time*8/1000000]"
        $sink($i) set bytes_ 0
        }
        #Reset the bytes_ values on the traffic sinks
        #Re-schedule the procedure
        $ns at [expr $now+$time] "record"
}
#Define a 'finish' procedure
proc finish {} {
 global ns nf tf f n_sink
 $ns flush-trace
 #Close the NAM trace file
 close $tf
 close $nf

 for {set i 0} {$i < [array size f]} {incr i} {
         close $f($i)
 }


 #exec nam out.nam &
set result ""
 for {set i 0} {$i < $n_sink} {incr i} {
        append result "trace$i.tr "
 }
 
 exec xgraph {*}$result -geometry 800x800 &
 exit 0
}
 
$ns color 1 Blue
$ns color 2 Red
$ns color 3 Yellow
$ns color 4 Green



#Create four nodes
#Define different colors for data flows (for NAM)
for {set i 0} {$i < $n_cameras} {incr i} {
        set n($i) [$ns node]
}

set r [$ns node]        
$r shape "hexagon"
set cloud [$ns node]
 
#Create links between the nodes
for {set i 0} {$i < [array size n]} {incr i} {
    $ns duplex-link $n($i) $r 96Mb 30ms DropTail
}


$ns duplex-link $r $cloud 1Gb 100ms DropTail
$ns queue-limit $r $cloud 10

 
# #Monitor the queue for link (n2-n3). (for NAM)
$ns duplex-link-op $r $cloud queuePos 0.5
 
 
#Setup a UDP connection

for {set i 0} {$i < $n_cameras} {incr i} {
        set sink($i) [new Agent/LossMonitor]
        $ns attach-agent $cloud $sink($i)
}



for {set i 0} {$i < $n_cameras} {incr i} {
        set udp($i) [new Agent/UDP]
        $ns attach-agent $n($i) $udp($i)
        $ns connect $udp($i) $sink($i)
        $udp($i) set fid_ [expr $i + 1]

        set cbr($i) [new Application/Traffic/CBR]
        $cbr($i) attach-agent $udp($i)
        $cbr($i) set type_ CBR
        $cbr($i) set packet_size_ 1000
        $cbr($i) set rate_ 96mb
        $cbr($i) set random_ 1
}

# $udp set fid_ 2

 
#Schedule events for the CBR and FTP agents
for {set i 0} {$i < [array size n]} {incr i} {
        $ns at 0.1 "$cbr($i) start"
        $ns at 5 "$cbr($i) stop"
}

 
#Detach tcp and sink agents (not really necessary)
# $ns at 4.5 "$ns detach-agent $n0 $tcp ; $ns detach-agent $n3 $sink"
 
#Call the finish procedure after 5 seconds of simulation time
$ns at 0.0 "record" 

$ns at 5.0 "finish"
 
#Print CBR packet size and interval
# for {set i 0} {$i < [array size n]} {incr i} {
#         puts "CBR packet size = [$cbr($i) set packet_size_]"
#         puts "CBR interval = [$cbr($i) set interval_]"
# }
 
#Run the simulation
$ns run