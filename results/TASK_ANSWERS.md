# Assignment 3 – CO3: Calculation and analysis notes

This document records the reasoning used by the executable programs. Values from the assignment brief are kept explicit. Modelled or inferred values are labelled; actual experiment outputs are stored separately in `results/`.

## Q1 – Which Socket Gets the Segment? (7 marks)

### Socket demultiplexing

TCP uses the connection's four-tuple (source IP, source port, destination IP, destination port), together with the protocol, to distinguish established connections. UDP normally delivers datagrams to a socket bound to the local address/port; the application can inspect each datagram's source address/port using `recvfrom`, but a single bound UDP socket can serve many viewers.

| Arriving segment | Receiving socket |
|---|---|
| TCP `49.37.2.8:50001` → `203.0.113.5:443` | Established TCP connection for `49.37.2.8:50001` |
| TCP `117.96.4.2:50000` → `203.0.113.5:443` | Established TCP connection for `117.96.4.2:50000` |
| New TCP SYN `106.51.7.7:41000` → port 443 | TCP listening socket on port 443; after handshake, a new established socket is created |
| UDP `49.37.2.8:50000` → port 5004 | UDP socket bound to `203.0.113.5:5004`; source tuple is available to the application |

Two TCP connections can use source port 50000 because their source IP addresses differ (and the complete four-tuples differ). TCP connection identity is not determined by source port alone. A UDP socket's local port identifies the receiving endpoint; multiple viewers' datagrams arrive at that same socket and are distinguished by source address/port in the datagram metadata.

### Header overhead for a 100-byte application update

Assuming IPv4 without options, UDP header = 8 bytes and TCP base header = 20 bytes; IPv4 header = 20 bytes.

- UDP packet size = 100 + 8 + 20 = 128 bytes. Headers = 28 bytes = **28% of payload**, or **21.875% of the complete IP packet**.
- TCP packet size = 100 + 20 + 20 = 140 bytes. Headers = 40 bytes = **40% of payload**, or **28.57% of the complete IP packet**.

These are base-header calculations and exclude link-layer headers, TCP options, TLS records and retransmissions.

### Protocol choice

- Live video: UDP-based real-time transport (for example RTP/WebRTC) is appropriate when low delay is more important than retransmitting late packets. Use congestion control, jitter buffering and packet-loss concealment/FEC as appropriate.
- Scores: TCP or HTTPS is suitable because updates are small and correctness/order matter more than avoiding every millisecond of delay. A reliable QUIC/HTTP3 stream is also viable.
- Ball-by-ball commentary: TCP/HTTPS or a reliable QUIC stream is preferred because missing or reordered text changes the meaning. A separate real-time event channel may use a datagram transport if the application can tolerate loss and recover state.

### Executed socket program

`Task01/q1_sockets.py` completes the two supplied TODOs. The UDP server receives three datagrams with `recvfrom(1024)` and replies with `ACK:` plus the received bytes. The TCP server reads chunks up to 4096 bytes until `recv()` returns `b''`, counting all bytes.

Executed output:

```text
UDP lab1 -> ACK:lab1
UDP lab2 -> ACK:lab2
UDP lab3 -> ACK:lab3
TCP server received 100000 bytes in order
```

This verifies the local client/server logic. It does not substitute for the requested Wireshark capture or netem loss experiment.

### TCP video freeze estimate

At 500 packets/s, 2% loss gives 10 lost packets/s, or **600 lost packets/minute**. With 60 ms RTT, each loss can cause at least one RTT of recovery delay, so the minimum per-loss freeze interval is **60 ms**. If all 600 events caused separate non-overlapping freezes, the simple upper-bound sum would be 600 × 0.06 = **36 seconds of freeze intervals per minute**. Actual visible freezes depend on frame/packet mapping, loss bursts, retransmission timing, buffering and whether several losses overlap.

### Reply to “UDP is unreliable, so never use it”

UDP does not guarantee delivery, ordering or retransmission at the transport layer. That is not the same as being unusable. For interactive media, a late retransmitted packet may be less useful than skipping it and continuing with current video. Applications can add sequence numbers, jitter buffers, FEC and congestion control. TCP is preferable when reliable ordered delivery is required.

---

## Q2 – Read the Congestion Window (7 marks)

### Reading the supplied trace

The initial slow-start threshold is **16 segments**: the window doubles 1, 2, 4, 8, 16 and then grows additively. At the first drop (after the value 19 at RTT 8), `ssthresh = floor(19/2) = 9`; the window resumes at 9. At the second drop (after 14 at RTT 14), `ssthresh = floor(14/2) = 7`.

- RTT 8: the reduction from 19 to 9 is consistent with fast retransmit/fast recovery after duplicate ACKs (Reno behaviour), rather than a timeout reset to 1.
- RTT 14: the reset from 14 to 1 is consistent with a retransmission timeout. The graph alone cannot prove the exact packet-level cause, but the shape supports that interpretation.
- The sender is consistent with **TCP Reno** because the first loss halves the window instead of resetting it to 1. The second reset can occur when a timeout happens.

### Throughput at RTT 7

At RTT 7, `cwnd = 18` segments. With 1,460 bytes/segment and 40 ms RTT:

`throughput ≈ cwnd × MSS × 8 / RTT`

`= 18 × 1,460 × 8 / 0.040 = 5,256,000 bit/s ≈ 5.256 Mbps`.

This is the window-limited estimate, ignoring headers and other bottlenecks.

### Executed Tahoe/Reno model

`Task02/q2_congestion.py` completes the supplied TODO and plots both traces. The program reproduces the supplied expected segment totals:

- Reno: **211 segments**
- Tahoe: **144 segments**
- Reno advantage in this 20-RTT model: **67 segments**

The exact traces are in `results/task02_output.txt`; the plot is `graphs/q2_tahoe_reno.png`.

AIMD tends towards fairness because additive increase gives flows comparable absolute growth while multiplicative decrease reduces each competing flow proportionally. Under similar RTTs and bottleneck conditions, this tends to move flows toward a fair share. Different RTTs, application behaviour and loss response can prevent exact equality.

### BBR vs Reno under 1% random non-congestion loss

Reno interprets loss as a congestion signal and reduces its congestion window, even if the loss is random rather than caused by a full queue. BBR estimates bottleneck bandwidth and minimum RTT and does not use random loss as its primary congestion signal, so it can maintain a higher sending rate when the path has spare capacity. BBR can therefore achieve higher throughput on a random-loss link, but the actual result depends on implementation/version, competing traffic and whether the path is truly uncongested.

CUBIC vs BBR decision: use BBR when measured delay and random loss indicate a high-bandwidth, non-congestion-loss path and the implementation is supported; use CUBIC where compatibility and conventional loss-based behaviour are preferred. Validate fairness and queueing delay before deployment.

---

## Q3 – Why Does the Home Page Take 8 Seconds? (7 marks)

Given RTT = 50 ms, one HTML file + 80 objects, negligible transmission time. Assumptions: a new TCP connection costs 1 RTT; each HTTP request/response costs 1 RTT; no TLS setup is included in this simplified comparison.

| Model | RTT accounting | Time |
|---|---:|---:|
| Non-persistent, one connection at a time | 2 RTT × 81 resources = 162 RTT | 8,100 ms |
| Persistent HTTP/1.1, no pipelining | 1 setup RTT + 81 request/response RTTs = 82 RTT | 4,100 ms |
| Persistent HTTP/1.1, pipelining | 1 setup + 1 HTML request + 1 pipelined object batch = 3 RTT | 150 ms |
| 6 parallel non-persistent connections | 2 RTT for HTML + 14 waves × 2 RTT for 80 objects = 30 RTT | 1,500 ms |

For 6 parallel connections, `ceil(80/6) = 14` waves. Real browser scheduling, server limits, TLS, congestion and object dependencies can change measured times.

### HTTP/2 and HTTP/3

HTTP/2 multiplexes streams over one TCP connection, but TCP delivers an ordered byte stream. Loss of one TCP segment can hold up delivery of later bytes on all streams until TCP repairs the gap (transport-level head-of-line blocking). HTTP/3 uses QUIC over UDP, with independent streams; loss affecting one stream need not block delivery of data on unrelated streams.

### Caching

`Cache-Control: max-age=...` lets the browser reuse a fresh object without contacting the server during the freshness period. `ETag` allows conditional revalidation using `If-None-Match`; a 304 response avoids retransmitting the object body, but still requires a network round trip. If all 80 objects are fresh in cache, a second visit can avoid their requests; only uncached/revalidated resources need network access.

### Engineering ranking

1. Enable HTTP/2 or HTTP/3 and multiplex resources to reduce serial RTT waits.
2. Bundle or reduce the number of small objects and use effective caching.
3. Reduce RTT through geographically close CDN/edge delivery and optimise critical-resource dependencies.

### Alternative: combine 80 objects into 8 bundles

There are now 9 resources including the HTML file:

- Non-persistent one-at-a-time: 2 × 9 = 18 RTT = **900 ms**.
- Persistent HTTP/1.1 without pipelining: 1 setup + 9 request/response RTTs = 10 RTT = **500 ms**.

Bundling reduces serial request overhead substantially. HTTP/2 can still help through multiplexing and header compression, especially when resources are independent and the connection is already established.

---

## Q4 – How Many Queries Reach the University DNS Server? (7 marks)

For one recursive resolver, assuming one authoritative refresh per TTL expiry and a continuously requested record:

- TTL 300 s: `3600/300 = 12` authoritative lookups/hour per resolver.
- TTL 30 s: `3600/30 = 120` lookups/hour per resolver.

If there is one relevant resolver in each of 40 cities, this would be approximately **480 queries/hour** at 300 s TTL or **4,800 queries/hour** at 30 s TTL. Actual traffic depends on the number of distinct recursive caches, query patterns, cache prefetch/stale policies and record set.

The number of students is not the direct multiplier at the authoritative server because many students share recursive resolvers and cached answers. The number of independent resolver caches and TTL expiry frequency are more directly related to authoritative query volume.

### Resolution flow

A phone generally sends a recursive query to its configured recursive resolver and asks it to return the final answer. The resolver then performs iterative queries: root server → `.in` TLD server → `ac.in` delegation → authoritative `simats.ac.in` server. The resolver caches the answer according to TTL and returns it to the phone.

### DNS records

- A: IPv4 address for the website.
- AAAA: IPv6 address.
- CNAME: alias where an alias name is required.
- MX: mail exchangers for the domain.
- NS: authoritative name servers/delegation.
- TXT: verification and policy text (for example SPF/other domain policies).

DNS commonly uses UDP for small queries/responses because it has low setup overhead. TCP is used for zone transfers and responses that are truncated or otherwise require reliable stream transport; modern DNS may also use encrypted transports such as DoT/DoH.

A very long TTL reduces resolver traffic but makes a moved result server harder to redirect quickly because clients may continue using cached old addresses until expiry.

### Executed resolver simulation

The supplied server dictionary is followed by longest matching suffix. The executed output is:

```text
results.simats.ac.in.    10.20.30.40     queries sent: 4
www.example.com.         93.184.216.34   queries sent: 3
results.simats.ac.in.    10.20.30.40     queries sent: 0
```

The third lookup sends zero queries because the first lookup cached the answer. The program includes a 300-second expiry time. `dig +trace` and public resolver timing still need to be run on a connected machine.

### CDN / anycast alternative

If the result hostname is delegated to a CDN/managed DNS provider, user queries are answered by that provider's authoritative DNS infrastructure rather than the university's own authoritative server. The university's own DNS may receive no direct per-student lookups for that hostname (except management/control or other records still hosted there). Anycast routes the query to a nearby DNS point of presence, which can reduce lookup latency for distant cities. The exact authoritative query count depends on the CDN DNS TTL and resolver cache population.

Recommendation: use a moderate TTL such as 300 seconds for normal result-day operation, lower it ahead of a planned migration (after allowing the previous TTL to expire), and use redundant authoritative DNS/CDN service. Monitor resolver query rates and keep an emergency traffic-switch plan.

---

## Q5 – When Will the Video Call Freeze? (6 marks)

For M/M/1, service rate `μ = 1000 packets/s`, arrival rate `λ`:

`ρ = λ/μ`, `L = ρ/(1−ρ)`, `W = 1/(μ−λ)`.

| λ (packets/s) | ρ | L (packets) | W (ms) |
|---:|---:|---:|---:|
| 500 | 0.50 | 1 | 2 |
| 800 | 0.80 | 4 | 5 |
| 900 | 0.90 | 9 | 10 |
| 950 | 0.95 | 19 | 20 |
| 990 | 0.99 | 99 | 100 |
| 1000 | 1.00 | Unbounded | Unstable |

The average delay first becomes **greater than 20 ms at 990 packets/s**; at 950 packets/s it is exactly 20 ms.

### Important numerical inconsistency in the brief

With μ = 1000 packets/s, at λ = 450, `W = 1/(1000−450) = 1.818 ms`; at λ = 900, `W = 1/(1000−900) = 10 ms`. This is a **5.5×** increase, not 10×. The statement in the assignment that it multiplies by ten does not follow from the supplied M/M/1 formula and service rate. The report should show the formula and flag this discrepancy rather than repeat an incorrect factor.

### Token bucket

Bucket capacity = 1 MB = 8 Mb. Backup attempts 10 Mbps while tokens are replenished at 2 Mbps. Net bucket depletion = 8 Mbps. Starting with a full bucket, burst duration = 8 Mb / 8 Mbps = **1 second**, after which the backup is limited to the configured 2 Mbps average rate.

### DiffServ choice

- EF: interactive voice / tightly latency-sensitive audio.
- AF (for example AF41): video stream with controlled assured forwarding and appropriate queue allocation.
- Best effort: ordinary web browsing and non-urgent bulk traffic.
- Patient/backup file transfer may use a suitable AF class if assured service is required, but it should not starve interactive media.

### Capacity needed for W < 10 ms at λ = 1500

`1/(μ−1500) < 0.010` implies `μ−1500 > 100`, therefore **μ > 1600 packets/s**. At exactly 1600, W is 10 ms, so capacity must be greater than 1600 for strictly below 10 ms.

### Double link alternative

With μ = 2000 packets/s and λ = 1800 packets/s, `W = 1/(2000−1800) = 0.005 s = 5 ms`.

Strict priority on the old link can protect video from backup queueing, but an exact delay cannot be calculated without the video arrival rate, packet sizes, service discipline and higher-priority traffic load. The seeded queue simulation in `Task05/q5_mm1_queue.py` illustrates FIFO vs non-preemptive video priority under one declared traffic model; it is not a measured router result.

Decision: shape the backup and apply QoS first when the link has enough total capacity but bulk traffic is causing contention. Upgrade capacity if aggregate sustained demand approaches/exceeds service capacity or if QoS cannot meet the latency target.

---

## Q6 – Count the Round Trips Before the First Byte (6 marks)

RTT = 100 ms. Time until request data can be sent (full handshakes unless noted):

| Protocol | RTTs before request data | Time |
|---|---:|---:|
| TCP + TLS 1.2 | TCP 1 RTT + TLS 1.2 full handshake 2 RTT | 300 ms |
| TCP + TLS 1.3 | TCP 1 RTT + TLS 1.3 handshake 1 RTT | 200 ms |
| QUIC first visit | Integrated QUIC/TLS 1.3 1-RTT handshake | 100 ms |
| QUIC 0-RTT resumption | Early data can be sent with the first flight | 0 RTT additional wait |

0-RTT early data can be replayed by an attacker in some threat scenarios. Do not send non-idempotent operations such as money transfers, account changes or one-time actions as 0-RTT. Safe read-only/idempotent requests may be considered subject to application policy and server replay protections.

QUIC connection IDs identify a QUIC connection independently of the network 4-tuple, allowing migration from Wi-Fi to 5G while retaining the connection. QUIC may validate the new path, typically adding up to about one RTT in this simplified estimate. TCP connections are identified by their endpoint tuple; a change of IP/interface generally breaks the existing connection and requires reconnecting. With TCP + TLS 1.3, a full new connection typically costs about 2 RTT (200 ms) before request data, excluding detection and retransmission delays.

Some firewalls block or rate-limit UDP/443, which can prevent QUIC. The app/browser should fall back to TCP-based HTTPS, usually HTTP/2, rather than fail the service.

Recommendation: QUIC is useful for mobile banking because it reduces initial handshake delay and supports connection migration. Retain secure TCP/TLS fallback. Do not put money transfers in 0-RTT early data.

---

## Q7 – Choose Protocols from First Principles (10 marks)

### Stage 1 – Traffic requirements

| Traffic | Delay / loss / ordering needs | Security and measurable requirement |
|---|---|---|
| Live video consultation | Low delay and jitter; tolerate some loss; avoid waiting for late retransmissions | Encrypt media; target interactive latency and monitor packet loss/jitter; adapt bitrate to link |
| Patient records and X-ray images | Complete, ordered, reliable delivery; delay is less critical than integrity | TLS encryption, authentication and access control; verify file hash after transfer |
| Chat | Reliable ordered text; modest bandwidth; low perceived delay | TLS; message acknowledgement and delivery status |
| Service-name lookup | Small request/response; cacheable; low lookup delay | DNSSEC validation where available; protect resolver and use sensible TTL |

Example measurable design targets for evaluation (engineering targets, not supplied guarantees): interactive video one-way latency target below 400 ms where the 100–300 ms RTT path permits; jitter below 30 ms; monitor packet loss and adapt bitrate; records must pass end-to-end hash verification with no missing bytes; chat messages must arrive once and in order; DNS lookup should be cached and typically complete within a small number of RTTs.

### Stage 2 – Protocol comparison and decisions

- Live video: WebRTC-style media over UDP with SRTP encryption, congestion control, jitter buffer and adaptive bitrate. QUIC/HTTP3 can carry signalling or application streams but is not a replacement for a purpose-built real-time media pipeline in every deployment.
- Patient records/X-rays: HTTPS over HTTP/2 or HTTP/3 with TLS 1.3/QUIC or TCP fallback. Reliable stream delivery and integrity verification are essential.
- Chat: reliable HTTPS/WebSocket over HTTP/2 or a QUIC stream. Preserve message order and acknowledgement.
- DNS: recursive resolver with cache; publish A and AAAA records and keep TTLs appropriate for service changes.
- QoS: EF for voice/audio; AF class for video; controlled AF/best effort for bulk records; best effort for ordinary lookups, with admission control so priority classes do not overload the link.

### TCP throughput limit for 64 KiB window and 300 ms RTT

`throughput ≤ window / RTT = 65,536 bytes × 8 / 0.300 s = 1,747,627 bit/s ≈ 1.75 Mbps`.

If “64 KB” means decimal 64,000 bytes, the limit is about 1.71 Mbps. This is a window-limited upper bound before protocol overhead and loss. A large X-ray image may therefore take a long time over a 300 ms path unless the receive window is scaled/increased, the path is improved, or a suitable transport/application strategy is used.

### Stage 3 – Executed file/chat socket demonstration

`Task07/q7_telemedicine_demo.py` sends a 960,000-byte test image/file over a real local TCP socket, sends a chat message, receives the server response and verifies the file using SHA-256. The executed output reports integrity verified = True and the expected uppercase chat response.

The program separately generates a seeded 5% random-loss illustration and labels it as a model. The local TCP connection was not subjected to `tc netem`; actual 100–300 ms RTT and 5% loss testing must be run on a dedicated lab interface using the commands in `configs/EXPERIMENT_COMMANDS.md`.

### Stage 4 – Defend the design and 5G upgrade

Use UDP-based adaptive media for the live consultation, reliable encrypted streams for records and chat, and cached DNS. Measure video delay/jitter/loss and file completion time under the 4G impairment profile before final deployment. A 5G upgrade may reduce RTT and increase throughput, improving video quality and large file transfer time, but the application should still use congestion control, encryption, adaptive bitrate and reliable file integrity checks because 5G does not guarantee zero loss or constant latency.

### Vendor video service – questions and evidence

Ask the vendor for measured end-to-end latency, jitter and packet-loss performance across 100–300 ms RTT and 5% loss; congestion adaptation and recovery behaviour; encryption in transit and at rest; key management; data residency; access logging; retention/deletion; authentication; audit certifications; incident response; interoperability; availability SLA; and export/backup options. Request independent security audit reports, a data-processing agreement, a pilot test using representative rural links, packet/quality measurements and a documented failure/recovery test. Choose the vendor only if the measured quality meets clinical requirements and privacy/security obligations are contractually and technically verified.
