SNACK in Action
=================

Flow table
-----------

### Intra-dept. switches

i.e. `swS`, `swO`

| Priority | Match                    | Action               | Parameters | Type |
|----------|--------------------------|----------------------|------------|------|
| 1 | `dst_ip=[intra dept.]`   | Forward: to host     | | Proactive |
| 1 | `dst_ip=[outside dept.]` | Forward: `swCentral` | | Proactive |
| 1 | ARP                      | Flood                | | Proactive |

- `intra dept`: IP block that matches for hosts inside the department
- `outside dept`: Other IP; can be inter-dept. or network outside the office (i.e. the internet)

### `swCentral`

| Priority | Match                                   | Action      | Parameters                               | Type      |
|----------|-----------------------------------------|-------------|------------------------------------------|-----------|
| 12       | `src_ip=[host_ip]` `dst_ip=[server_ip]` | Forward: p3 | `hard-timeout=[allowed_time]`              | Reactive  |
| 11       | `src_ip=[host_ip]` `dst_ip=[server_ip]` | Block       | `hard-timeout=[allowed_time + block_time]` | Reactive  |
| 1        | ARP                                     | Flood       |                                          | Proactive |

- `host_ip`: IP address of the host inside the office and not in the Social Media dept. which accessing social media
- `server_ip`: IP address of the social media service that accessed by the host 
- `allowed_time`: How long the user can access the site (in seconds)
- `block_time`: How long the user will be blocked after accessing the service (in seconds)

### `swISP`

| Priority | Match           | Action            | Parameters | Type |
|----------|-----------------|-------------------|------------|------|
| 1 | dst_ip=10.1.1.1 | Forward to port 1 | | Proactive |
| 1 | dst_ip=10.1.1.2 | Forward to port 2 | | Proactive |
| 1 | ARP | Flood             | | Proactive |
