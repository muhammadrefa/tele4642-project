SNACK in Action
=================

Topology
---------
```commandline
mininet> links
swCentral-eth2<->swO-eth3 (OK OK) 
swCentral-eth1<->swS-eth3 (OK OK) 
swISP-eth3<->facebook-eth0 (OK OK) 
swISP-eth4<->google-eth0 (OK OK) 
swISP-eth5<->m365-eth0 (OK OK) 
swISP-eth1<->swCentral-eth3 (OK OK) 
swISP-eth2<->twitter-eth0 (OK OK) 
swO-eth1<->hostO0-eth0 (OK OK) 
swO-eth2<->hostO1-eth0 (OK OK) 
swS-eth1<->hostS0-eth0 (OK OK) 
swS-eth2<->hostS1-eth0 (OK OK)
```

```commandline
mininet> dump
<Host facebook: facebook-eth0:10.2.2.1 pid=2393> 
<Host google: google-eth0:10.2.3.1 pid=2395> 
<Host hostO0: hostO0-eth0:10.1.2.1 pid=2397> 
<Host hostO1: hostO1-eth0:10.1.2.2 pid=2399> 
<Host hostS0: hostS0-eth0:10.1.1.1 pid=2401> 
<Host hostS1: hostS1-eth0:10.1.1.2 pid=2403> 
<Host m365: m365-eth0:10.2.4.1 pid=2405> 
<Host twitter: twitter-eth0:10.2.1.1 pid=2407> 
<OVSSwitch swCentral: lo:127.0.0.1,swCentral-eth1:None,swCentral-eth2:None,swCentral-eth3:None pid=2412> 
<OVSSwitch swISP: lo:127.0.0.1,swISP-eth1:None,swISP-eth2:None,swISP-eth3:None,swISP-eth4:None,swISP-eth5:None pid=2415> 
<OVSSwitch swO: lo:127.0.0.1,swO-eth1:None,swO-eth2:None,swO-eth3:None pid=2418> 
<OVSSwitch swS: lo:127.0.0.1,swS-eth1:None,swS-eth2:None,swS-eth3:None pid=2421> 
<RemoteController{'ip': '192.168.56.1'} c0: 192.168.56.1:6653 pid=2387>
```

Flow table
-----------

### Intra-dept. switches

i.e. `swS`, `swO`

| Priority | Match                                  | Action                          | Parameters | Type |
|----------|----------------------------------------|---------------------------------|------------|------|
| 0        | IP packet `dst_ip=[intra_dept_subnet]` | Forward: normal L2/L3 switching | | Proactive |
| 0        | IP packet                              | Forward: `swCentral`            | | Proactive |
| 0        | ARP packet                             | Flood                           | | Proactive |

- `intra_dept_subnet`: IP subnet that matches for hosts inside the department

#### swS
```commandline
$ sudo ovs-ofctl dump-flows swS
 cookie=0x0, duration=11.828s, table=0, n_packets=0, n_bytes=0, priority=0,ip,nw_dst=10.1.1.0/24 actions=NORMAL
 cookie=0x0, duration=11.828s, table=0, n_packets=0, n_bytes=0, priority=0,ip actions=output:"swS-eth3"
 cookie=0x0, duration=11.828s, table=0, n_packets=0, n_bytes=0, priority=0,arp actions=FLOOD
```

#### swO
```commandline
$ sudo ovs-ofctl dump-flows swO
 cookie=0x0, duration=14.665s, table=0, n_packets=0, n_bytes=0, priority=0,ip,nw_dst=10.1.2.0/24 actions=NORMAL
 cookie=0x0, duration=14.665s, table=0, n_packets=0, n_bytes=0, priority=0,ip actions=output:"swO-eth3"
 cookie=0x0, duration=14.664s, table=0, n_packets=0, n_bytes=0, priority=0,arp actions=FLOOD
```

### `swCentral`

| Priority | Match                                                     | Action             | Parameters                               | Type      |
|----------|-----------------------------------------------------------|--------------------|------------------------------------------|-----------|
| 12       | `src_ip=[host_ip]` `dst_ip=[socmed_server_ip]`            | Forward: `swISP`   | `hard-timeout=[allow_time]`              | Reactive  |
| 11       | `src_ip=[host_ip]` `dst_ip=[socmed_server_ip]`            | Drop               | `hard-timeout=[allow_time + block_time]` | Reactive  |
| 1        | `src_ip=[socmed_dept_subnet]` `dst_ip=[socmed_server_ip]` | Forward: `swISP`   |                                          | Proactive |
| 1        | `dst_ip=[socmed_server_ip]`                               | Send to controller |                                          | Proactive |
| 0        | `dst_ip=[socmed_dept_subnet]`                             | Forward: `swS`     |                                          | Proactive |
| 0        | `dst_ip=[other_dept_subnet]`                              | Forward: `swO`     |                                          | Proactive |
| 0        | `dst_ip=[internet]`                                       | Forward: `swISP`   |                                          | Proactive |
| 0        | ARP                                                       | Flood              |                                          | Proactive |

- `host_ip`: Host IP address
- `socmed_server_ip`: IP address of the social media service that accessed by the host
- `socmed_dept_subnet`: IP block for hosts inside the social media department
- `other_dept_subnet`: IP block for hosts in other department
- `allow_time`: How long the user can access the site (in seconds)
- `block_time`: How long the user will be blocked after accessing the service (in seconds)

Without reactive flow
```commandline$ sudo ovs-ofctl dump-flows swCentral
 cookie=0x0, duration=3.474s, table=0, n_packets=0, n_bytes=0, priority=1,ip,nw_src=10.1.1.0/24,nw_dst=10.2.1.1 actions=output:"swCentral-eth3"
 cookie=0x0, duration=3.474s, table=0, n_packets=0, n_bytes=0, priority=1,ip,nw_src=10.1.1.0/24,nw_dst=10.2.2.1 actions=output:"swCentral-eth3"
 cookie=0x0, duration=3.474s, table=0, n_packets=0, n_bytes=0, priority=1,ip,nw_dst=10.2.1.1 actions=CONTROLLER:65535
 cookie=0x0, duration=3.474s, table=0, n_packets=0, n_bytes=0, priority=1,ip,nw_dst=10.2.2.1 actions=CONTROLLER:65535
 cookie=0x0, duration=3.474s, table=0, n_packets=0, n_bytes=0, priority=0,ip,nw_dst=10.1.1.0/24 actions=output:"swCentral-eth1"
 cookie=0x0, duration=3.474s, table=0, n_packets=0, n_bytes=0, priority=0,ip,nw_dst=10.1.2.0/24 actions=output:"swCentral-eth2"
 cookie=0x0, duration=3.474s, table=0, n_packets=0, n_bytes=0, priority=0,ip,nw_dst=10.2.0.0/16 actions=output:"swCentral-eth3"
 cookie=0x0, duration=3.474s, table=0, n_packets=0, n_bytes=0, priority=0,arp actions=FLOOD
```

With reactive flow
```commandline
$ sudo ovs-ofctl dump-flows swCentral
 cookie=0x0, duration=2.014s, table=0, n_packets=1, n_bytes=98, hard_timeout=10, priority=12,ip,nw_src=10.1.2.2,nw_dst=10.2.2.1 actions=output:"swCentral-eth3"
 cookie=0x0, duration=2.014s, table=0, n_packets=0, n_bytes=0, hard_timeout=30, priority=11,ip,nw_src=10.1.2.2,nw_dst=10.2.2.1 actions=drop
 cookie=0x0, duration=61.063s, table=0, n_packets=0, n_bytes=0, priority=1,ip,nw_src=10.1.1.0/24,nw_dst=10.2.1.1 actions=output:"swCentral-eth3"
 cookie=0x0, duration=61.063s, table=0, n_packets=0, n_bytes=0, priority=1,ip,nw_src=10.1.1.0/24,nw_dst=10.2.2.1 actions=output:"swCentral-eth3"
 cookie=0x0, duration=61.063s, table=0, n_packets=0, n_bytes=0, priority=1,ip,nw_dst=10.2.1.1 actions=CONTROLLER:65535
 cookie=0x0, duration=61.063s, table=0, n_packets=1, n_bytes=98, priority=1,ip,nw_dst=10.2.2.1 actions=CONTROLLER:65535
 cookie=0x0, duration=61.063s, table=0, n_packets=0, n_bytes=0, priority=0,ip,nw_dst=10.1.1.0/24 actions=output:"swCentral-eth1"
 cookie=0x0, duration=61.063s, table=0, n_packets=1, n_bytes=98, priority=0,ip,nw_dst=10.1.2.0/24 actions=output:"swCentral-eth2"
 cookie=0x0, duration=61.063s, table=0, n_packets=0, n_bytes=0, priority=0,ip,nw_dst=10.2.0.0/16 actions=output:"swCentral-eth3"
 cookie=0x0, duration=61.063s, table=0, n_packets=0, n_bytes=0, priority=0,arp actions=FLOOD
```

With reactive forwarding flow expired
```commandline
$ sudo ovs-ofctl dump-flows swCentral
 cookie=0x0, duration=13.778s, table=0, n_packets=4, n_bytes=392, hard_timeout=30, priority=11,ip,nw_src=10.1.2.2,nw_dst=10.2.2.1 actions=drop
 cookie=0x0, duration=103.512s, table=0, n_packets=0, n_bytes=0, priority=1,ip,nw_src=10.1.1.0/24,nw_dst=10.2.1.1 actions=output:"swCentral-eth3"
 cookie=0x0, duration=103.512s, table=0, n_packets=0, n_bytes=0, priority=1,ip,nw_src=10.1.1.0/24,nw_dst=10.2.2.1 actions=output:"swCentral-eth3"
 cookie=0x0, duration=103.512s, table=0, n_packets=0, n_bytes=0, priority=1,ip,nw_dst=10.2.1.1 actions=CONTROLLER:65535
 cookie=0x0, duration=103.512s, table=0, n_packets=1, n_bytes=98, priority=1,ip,nw_dst=10.2.2.1 actions=CONTROLLER:65535
 cookie=0x0, duration=103.512s, table=0, n_packets=0, n_bytes=0, priority=0,arp actions=FLOOD
 cookie=0x0, duration=103.512s, table=0, n_packets=0, n_bytes=0, priority=0,ip,nw_dst=10.1.1.0/24 actions=output:"swCentral-eth1"
 cookie=0x0, duration=103.512s, table=0, n_packets=18, n_bytes=1764, priority=0,ip,nw_dst=10.1.2.0/24 actions=output:"swCentral-eth2"
 cookie=0x0, duration=103.512s, table=0, n_packets=0, n_bytes=0, priority=0,ip,nw_dst=10.2.0.0/16 actions=output:"swCentral-eth3"
```

### `swISP`

| Priority | Match                | Action               | Parameters | Type |
|----------|----------------------|----------------------|------------|------|
| 0        | `dst_ip=10.1.1.0/24` | Forward: `swCentral` | | Proactive |
| 0        | `dst_ip=10.2.1.1`    | Forward: `port1`     | | Proactive |
| 0        | `dst_ip=10.2.2.1`    | Forward: `port2`     | | Proactive |
| 0        | `dst_ip=10.2.3.1`    | Forward: `port3`     | | Proactive |
| 0        | `dst_ip=10.2.4.1`    | Forward: `port4`     | | Proactive |
| 0        | ARP                  | Flood                | | Proactive |

```commandline
$ sudo ovs-ofctl dump-flows swISP
 cookie=0x0, duration=141.649s, table=0, n_packets=0, n_bytes=0, priority=0,ip,nw_dst=10.2.1.0/24 actions=output:"swISP-eth2"
 cookie=0x0, duration=141.649s, table=0, n_packets=0, n_bytes=0, priority=0,ip,nw_dst=10.2.2.0/24 actions=output:"swISP-eth3"
 cookie=0x0, duration=141.649s, table=0, n_packets=0, n_bytes=0, priority=0,ip,nw_dst=10.2.3.0/24 actions=output:"swISP-eth4"
 cookie=0x0, duration=141.649s, table=0, n_packets=0, n_bytes=0, priority=0,ip,nw_dst=10.2.4.0/24 actions=output:"swISP-eth5"
 cookie=0x0, duration=141.649s, table=0, n_packets=0, n_bytes=0, priority=0,ip,nw_dst=10.1.0.0/16 actions=output:"swISP-eth1"
 cookie=0x0, duration=141.649s, table=0, n_packets=0, n_bytes=0, priority=0,arp actions=FLOOD
```

Ping test
----------

The system tested using these parameters
- `allow_time` = 10 secs.
- `block_time` = 20 secs.

### Social media department to Other department
```
mininet> hostS1 ping hostO1
PING 10.1.2.2 (10.1.2.2) 56(84) bytes of data.
64 bytes from 10.1.2.2: icmp_seq=1 ttl=64 time=0.404 ms
64 bytes from 10.1.2.2: icmp_seq=2 ttl=64 time=0.099 ms
64 bytes from 10.1.2.2: icmp_seq=3 ttl=64 time=0.097 ms
64 bytes from 10.1.2.2: icmp_seq=4 ttl=64 time=0.170 ms
64 bytes from 10.1.2.2: icmp_seq=5 ttl=64 time=0.329 ms
64 bytes from 10.1.2.2: icmp_seq=6 ttl=64 time=0.134 ms
64 bytes from 10.1.2.2: icmp_seq=7 ttl=64 time=0.139 ms
64 bytes from 10.1.2.2: icmp_seq=8 ttl=64 time=0.215 ms
64 bytes from 10.1.2.2: icmp_seq=9 ttl=64 time=0.157 ms
64 bytes from 10.1.2.2: icmp_seq=10 ttl=64 time=0.112 ms
64 bytes from 10.1.2.2: icmp_seq=11 ttl=64 time=0.239 ms
64 bytes from 10.1.2.2: icmp_seq=12 ttl=64 time=0.176 ms
64 bytes from 10.1.2.2: icmp_seq=13 ttl=64 time=0.161 ms
64 bytes from 10.1.2.2: icmp_seq=14 ttl=64 time=0.130 ms
64 bytes from 10.1.2.2: icmp_seq=15 ttl=64 time=0.174 ms
64 bytes from 10.1.2.2: icmp_seq=16 ttl=64 time=0.189 ms
64 bytes from 10.1.2.2: icmp_seq=17 ttl=64 time=0.148 ms
64 bytes from 10.1.2.2: icmp_seq=18 ttl=64 time=0.145 ms
64 bytes from 10.1.2.2: icmp_seq=19 ttl=64 time=0.152 ms
64 bytes from 10.1.2.2: icmp_seq=20 ttl=64 time=0.099 ms
^C
--- 10.1.2.2 ping statistics ---
20 packets transmitted, 20 received, 0% packet loss, time 19425ms
rtt min/avg/max/mdev = 0.097/0.173/0.404/0.074 ms
```

### Other department to Social media department
```
mininet> hostO0 ping hostS0
PING 10.1.1.1 (10.1.1.1) 56(84) bytes of data.
64 bytes from 10.1.1.1: icmp_seq=1 ttl=64 time=0.419 ms
64 bytes from 10.1.1.1: icmp_seq=2 ttl=64 time=0.170 ms
64 bytes from 10.1.1.1: icmp_seq=3 ttl=64 time=0.200 ms
64 bytes from 10.1.1.1: icmp_seq=4 ttl=64 time=0.160 ms
64 bytes from 10.1.1.1: icmp_seq=5 ttl=64 time=0.101 ms
64 bytes from 10.1.1.1: icmp_seq=6 ttl=64 time=0.164 ms
64 bytes from 10.1.1.1: icmp_seq=7 ttl=64 time=0.173 ms
64 bytes from 10.1.1.1: icmp_seq=8 ttl=64 time=0.148 ms
64 bytes from 10.1.1.1: icmp_seq=9 ttl=64 time=0.127 ms
64 bytes from 10.1.1.1: icmp_seq=10 ttl=64 time=0.182 ms
64 bytes from 10.1.1.1: icmp_seq=11 ttl=64 time=0.193 ms
64 bytes from 10.1.1.1: icmp_seq=12 ttl=64 time=0.184 ms
64 bytes from 10.1.1.1: icmp_seq=13 ttl=64 time=0.170 ms
64 bytes from 10.1.1.1: icmp_seq=14 ttl=64 time=0.177 ms
64 bytes from 10.1.1.1: icmp_seq=15 ttl=64 time=0.167 ms
64 bytes from 10.1.1.1: icmp_seq=16 ttl=64 time=0.160 ms
64 bytes from 10.1.1.1: icmp_seq=17 ttl=64 time=0.146 ms
64 bytes from 10.1.1.1: icmp_seq=18 ttl=64 time=0.155 ms
64 bytes from 10.1.1.1: icmp_seq=19 ttl=64 time=0.154 ms
64 bytes from 10.1.1.1: icmp_seq=20 ttl=64 time=0.153 ms
^C
--- 10.1.1.1 ping statistics ---
20 packets transmitted, 20 received, 0% packet loss, time 19436ms
rtt min/avg/max/mdev = 0.101/0.175/0.419/0.060 ms
```

### Social media department to Social media service
```
mininet> hostS1 ping facebook
PING 10.2.2.1 (10.2.2.1) 56(84) bytes of data.
64 bytes from 10.2.2.1: icmp_seq=1 ttl=64 time=0.391 ms
64 bytes from 10.2.2.1: icmp_seq=2 ttl=64 time=0.151 ms
64 bytes from 10.2.2.1: icmp_seq=3 ttl=64 time=0.125 ms
64 bytes from 10.2.2.1: icmp_seq=4 ttl=64 time=0.142 ms
64 bytes from 10.2.2.1: icmp_seq=5 ttl=64 time=0.190 ms
64 bytes from 10.2.2.1: icmp_seq=6 ttl=64 time=0.140 ms
64 bytes from 10.2.2.1: icmp_seq=7 ttl=64 time=0.160 ms
64 bytes from 10.2.2.1: icmp_seq=8 ttl=64 time=0.158 ms
64 bytes from 10.2.2.1: icmp_seq=9 ttl=64 time=0.156 ms
64 bytes from 10.2.2.1: icmp_seq=10 ttl=64 time=0.144 ms
64 bytes from 10.2.2.1: icmp_seq=11 ttl=64 time=0.154 ms
64 bytes from 10.2.2.1: icmp_seq=12 ttl=64 time=0.125 ms
64 bytes from 10.2.2.1: icmp_seq=13 ttl=64 time=0.160 ms
64 bytes from 10.2.2.1: icmp_seq=14 ttl=64 time=0.179 ms
64 bytes from 10.2.2.1: icmp_seq=15 ttl=64 time=0.163 ms
64 bytes from 10.2.2.1: icmp_seq=16 ttl=64 time=0.108 ms
64 bytes from 10.2.2.1: icmp_seq=17 ttl=64 time=0.163 ms
64 bytes from 10.2.2.1: icmp_seq=18 ttl=64 time=0.165 ms
64 bytes from 10.2.2.1: icmp_seq=19 ttl=64 time=0.194 ms
64 bytes from 10.2.2.1: icmp_seq=20 ttl=64 time=0.162 ms
^C
--- 10.2.2.1 ping statistics ---
20 packets transmitted, 20 received, 0% packet loss, time 19444ms
rtt min/avg/max/mdev = 0.108/0.166/0.391/0.055 ms
```

### Other department to Social media service
```
mininet> hostO1 ping facebook
PING 10.2.2.1 (10.2.2.1) 56(84) bytes of data.
64 bytes from 10.2.2.1: icmp_seq=2 ttl=64 time=0.966 ms
64 bytes from 10.2.2.1: icmp_seq=3 ttl=64 time=0.089 ms
64 bytes from 10.2.2.1: icmp_seq=4 ttl=64 time=0.167 ms
64 bytes from 10.2.2.1: icmp_seq=5 ttl=64 time=0.097 ms
64 bytes from 10.2.2.1: icmp_seq=6 ttl=64 time=0.171 ms
64 bytes from 10.2.2.1: icmp_seq=7 ttl=64 time=0.136 ms
64 bytes from 10.2.2.1: icmp_seq=8 ttl=64 time=0.139 ms
64 bytes from 10.2.2.1: icmp_seq=9 ttl=64 time=0.190 ms
64 bytes from 10.2.2.1: icmp_seq=10 ttl=64 time=0.179 ms
64 bytes from 10.2.2.1: icmp_seq=32 ttl=64 time=0.715 ms
64 bytes from 10.2.2.1: icmp_seq=33 ttl=64 time=0.100 ms
64 bytes from 10.2.2.1: icmp_seq=34 ttl=64 time=0.130 ms
64 bytes from 10.2.2.1: icmp_seq=35 ttl=64 time=0.161 ms
64 bytes from 10.2.2.1: icmp_seq=36 ttl=64 time=0.088 ms
64 bytes from 10.2.2.1: icmp_seq=37 ttl=64 time=0.229 ms
64 bytes from 10.2.2.1: icmp_seq=38 ttl=64 time=0.143 ms
64 bytes from 10.2.2.1: icmp_seq=39 ttl=64 time=0.171 ms
64 bytes from 10.2.2.1: icmp_seq=40 ttl=64 time=0.194 ms
64 bytes from 10.2.2.1: icmp_seq=62 ttl=64 time=0.651 ms
64 bytes from 10.2.2.1: icmp_seq=63 ttl=64 time=0.168 ms
64 bytes from 10.2.2.1: icmp_seq=64 ttl=64 time=0.189 ms
^C
--- 10.2.2.1 ping statistics ---
64 packets transmitted, 21 received, 67.1875% packet loss, time 64474ms
rtt min/avg/max/mdev = 0.088/0.241/0.966/0.227 ms
```

### Other department to Productivity service
```
mininet> hostO1 ping m365
PING 10.2.4.1 (10.2.4.1) 56(84) bytes of data.
64 bytes from 10.2.4.1: icmp_seq=1 ttl=64 time=0.385 ms
64 bytes from 10.2.4.1: icmp_seq=2 ttl=64 time=0.165 ms
64 bytes from 10.2.4.1: icmp_seq=3 ttl=64 time=0.155 ms
64 bytes from 10.2.4.1: icmp_seq=4 ttl=64 time=0.199 ms
64 bytes from 10.2.4.1: icmp_seq=5 ttl=64 time=0.223 ms
64 bytes from 10.2.4.1: icmp_seq=6 ttl=64 time=0.145 ms
64 bytes from 10.2.4.1: icmp_seq=7 ttl=64 time=0.220 ms
64 bytes from 10.2.4.1: icmp_seq=8 ttl=64 time=0.169 ms
64 bytes from 10.2.4.1: icmp_seq=9 ttl=64 time=0.211 ms
64 bytes from 10.2.4.1: icmp_seq=10 ttl=64 time=0.148 ms
64 bytes from 10.2.4.1: icmp_seq=11 ttl=64 time=0.160 ms
64 bytes from 10.2.4.1: icmp_seq=12 ttl=64 time=0.201 ms
64 bytes from 10.2.4.1: icmp_seq=13 ttl=64 time=0.182 ms
64 bytes from 10.2.4.1: icmp_seq=14 ttl=64 time=0.186 ms
64 bytes from 10.2.4.1: icmp_seq=15 ttl=64 time=0.121 ms
64 bytes from 10.2.4.1: icmp_seq=16 ttl=64 time=0.209 ms
64 bytes from 10.2.4.1: icmp_seq=17 ttl=64 time=0.203 ms
64 bytes from 10.2.4.1: icmp_seq=18 ttl=64 time=0.168 ms
64 bytes from 10.2.4.1: icmp_seq=19 ttl=64 time=0.134 ms
64 bytes from 10.2.4.1: icmp_seq=20 ttl=64 time=0.120 ms
^C
--- 10.2.4.1 ping statistics ---
20 packets transmitted, 20 received, 0% packet loss, time 19430ms
rtt min/avg/max/mdev = 0.120/0.185/0.385/0.055 ms
```
