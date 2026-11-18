# Optional real-network experiment commands

These commands are templates to execute on the student's own Linux/Windows environment. They are not evidence of completed experiments. Run only on a system/network you own or are authorised to test. `tc netem` generally requires root/CAP_NET_ADMIN.

## Q1 – socket capture, sockets list and loss

1. Start Wireshark and select the loopback interface (`lo` on Linux; Npcap Loopback Adapter on Windows).
2. Run `python Task01/q1_sockets.py` in a terminal.
3. Wireshark display filter: `tcp.port == <observed-server-port> || udp.port == <observed-server-port>`.
4. In the TCP stream, identify SYN, SYN-ACK, ACK, sequence and acknowledgement numbers. For UDP, expand the UDP header and note source/destination ports and length.
5. List sockets:

```bash
ss -tunap
```

6. Example controlled impairment on loopback (check interface name first; restore afterwards):

```bash
sudo tc qdisc add dev lo root netem loss 1%
sudo tc qdisc change dev lo root netem loss 5%
sudo tc qdisc change dev lo root netem loss 10%
sudo tc qdisc del dev lo root
```

Run the UDP/TCP test during each setting and record application-delivered messages/bytes. TCP retransmission means application data can still arrive intact but with delay; UDP datagrams lost in transit are not retransmitted by UDP itself.

## Q2 – iperf3, TCP info and netem

```bash
# Terminal 1
iperf3 -s
# Terminal 2
iperf3 -c 127.0.0.1 -t 30
# Two simultaneous clients in separate terminals
iperf3 -c <server-ip> -t 30
iperf3 -c <server-ip> -t 30
# Inspect TCP state/metrics
ss -ti
# Add delay/loss to a chosen test interface, then remove it
sudo tc qdisc add dev <interface> root netem delay 40ms loss 1%
sudo tc qdisc del dev <interface> root
```

Use a controlled lab link, not a shared production interface.

## Q3 – browser DevTools

Open the university page with browser Developer Tools → Network. Enable “Preserve log”, record protocol (h1/h2/h3), connection count, transferred bytes and total load time. Repeat with cache disabled/enabled and with network throttling or a controlled proxy adding 0, 50 and 200 ms. Record first visit, second visit and a page with many small objects versus fewer bundled objects.

## Q4 – DNS

```bash
dig +trace results.simats.ac.in

dig @1.1.1.1 results.simats.ac.in

dig @8.8.8.8 results.simats.ac.in

dig @9.9.9.9 results.simats.ac.in

dig does-not-exist-assignment3.simats.ac.in
```

Run each resolver query twice and record answer, TTL and query time. `dig +trace` shows the iterative delegation chain from root to authoritative server. A nonexistent name normally produces NXDOMAIN, potentially with negative caching governed by SOA data.

## Q5 – queue shaping and ping

```bash
ping <gateway-or-lab-server>
sudo tc qdisc add dev <interface> root tbf rate 2mbit burst 1mb latency 100ms
# Run backup transfer and ping concurrently; record ping RTTs.
sudo tc qdisc del dev <interface> root
```

For strict-priority comparison, configure an authorised lab router/Linux traffic-control hierarchy and mark video and backup traffic separately. Record the queue discipline and class counters. Do not infer strict-priority delay without traffic rates and packet sizes.

## Q6 – TLS and HTTP/3

```bash
openssl s_client -connect example.com:443 -servername example.com -tls1_2
openssl s_client -connect example.com:443 -servername example.com -tls1_3
```

Use browser DevTools → Network and inspect the Protocol column (`h2`/`h3`). Wireshark TLS 1.3 captures may show ClientHello, ServerHello, encrypted handshake messages, Finished, and application data; some handshake details are encrypted unless session secrets are available.

## Q7 – impairment test

For an actual TCP test, use `tc netem` on a dedicated test interface and repeat the file transfer/chat program. For a 100 ms RTT, add approximately 50 ms one-way delay (netem delay 50ms on one direction; use an IFB/second-direction rule if you need a symmetric 100 ms RTT). For 5% loss:

```bash
sudo tc qdisc add dev <interface> root netem delay 50ms loss 5%
# execute transfer and chat client/server
sudo tc qdisc del dev <interface> root
```

Save checksums, elapsed time, retransmission observations and chat delivery. Avoid applying impairment to the interface carrying your remote desktop/SSH session.
