Behind SNACK
================

SNACK employed SDN switches which the controller is powered by [Ryu](https://ryu-sdn.org/).  
Consider the office topology in the figure below, with the internet represented by 4 cloud services.

![Simplified office network topology](assets/office-topo.png "Office network topology, simple version")

Each department have their own switches which connecting all the hosts inside the department, and connect them
with the central switch. The central switch acts as a gateway for the office network to access the internet
and as the access limiter to the social media services. All switches are connected to the SDN controller.


TODO: Explain the proactive rules and how to push them

TODO: Explain the reactive rules and how to push them

TODO: Explain the hard-timeouts

TODO: Flow table


Simulating the network
-------------------------

The network simulated using [Mininet](https://mininet.org).  
Figure below shows the simulation topology with the nodes' name.

![Simulation scenario](assets/simulation-scenario.png "Simulation scenario")

Cloud services represented by mininet hosts. `swISP` exists in order to simulate the gateway from the ISP
to the internet. The simulation only employs one controller, so the `swISP` also connected to the controller
(which in the real world it is not; hence the dotted line between the switch and the controller).

The node details are shown in tables below

### Social Media dept.

Hosts

| Host name | IP       |
|-----------|----------|
| `hostS0`  | 10.1.1.1 |
| `hostS1`  | 10.1.1.2 |

`swS`  
Description: Switch in the Social Media Department  
DPID: `00:00:00:00:01:00:01`

| Port number | Connected to |
| ----------- | ------------ |
| 1 | `hostS0` |
| 2 | `hostS1` |
| 3 | `swCentral` |

### Other dept.

Hosts

| Host name | IP       |
|-----------|----------|
| `hostO0`  | 10.1.2.1 |
| `hostO1`  | 10.1.2.2 |

`swO`  
Description: Switch in the other department  
DPID: `00:00:00:00:01:00:02`

| Port number | Connected to |
| ----------- |--------------|
| 1 | `hostO0`     |
| 2 | `hostO1`     |
| 3 | `swCentral`  |

### Office Gateway/Central

`swCentral`  
Description: Central switch. Gateway to the internet  
DPID: `00:00:00:00:01:01:01`

| Port number | Connected to |
| ----------- |--------------|
| 1 | `swS`        |
| 2 | `swO`        |
| 3 | `swISP`      |

### The Internet

Hosts

| Host name      | IP       |
|----------------|----------|
| `twitter`      | 10.2.1.1 |
| `facebook`     | 10.2.2.1 |
| `google`       | 10.2.3.1 |
| `microsoft365` | 10.2.4.1 |

`swISP`  
Description: Switch in the Internet Service Provider (ISP)  
DPID: `00:00:00:00:02:00:01`

| Port number | Connected to   |
| ----------- |----------------|
| 1 | `swCentral`    |
| 2 | `twitter`      |
| 3 | `facebook`     |
| 3 | `google`       |
| 3 | `microsoft365` |

- - -

Icons used in the topology are provided by [JGraph/draw.io](https://jgraph.github.io/drawio/) (Citrix icon pack)
