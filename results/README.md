# CSA07 – Computer Networks Assignment 3 (CO3)

**Student:** S. Swetha  
**Register number:** 192521076  
**Assignment:** CO3 – TCP, UDP, HTTP, DNS, QoS, QUIC and TLS 1.3

## Environment used for the executed work

- Operating system: Linux x86_64 execution environment (kernel 6.18.57)
- Python: 3.13.5
- Matplotlib: 3.10.8
- Execution date: 16 November 2026

> The Python programs in this archive were executed in the available Linux environment. The output logs in `results/` are from those executions. This environment did not have Wireshark/tshark, iperf3, dig, or Cisco Packet Tracer available. `tc` and OpenSSL executables were present, but privileged network shaping and external-site tests were not represented as completed. No packet captures, browser measurements, Packet Tracer screenshots, or external network measurements have been fabricated. Reproducible commands are provided in `configs/EXPERIMENT_COMMANDS.md`.

## Folder structure

- `Task01/` – UDP/TCP socket server and client; completed TODO 1 and TODO 2.
- `Task02/` – TCP Reno/Tahoe congestion-window simulation; completed TODO and graph.
- `Task03/` – HTTP load-time calculations and bundling comparison.
- `Task04/` – iterative DNS resolution simulation, cache and TTL; completed TODO.
- `Task05/` – M/M/1 calculations, queue simulation and delay graph; completed TODO.
- `Task06/` – TCP/TLS and QUIC connection setup RTT calculations.
- `Task07/` – reliable file-transfer and chat socket demonstration with integrity verification.
- `graphs/` – generated plots.
- `results/` – captured stdout from each executed Python task.
- `configs/` – reproducible commands for optional network experiments.
- `TASK_ANSWERS.md` – calculation notes, interpretations and engineering decisions for Q1–Q7.

## Run everything

From this directory:

```bash
python run_all.py
```

Run one task:

```bash
cd Task01 && python q1_sockets.py
cd Task02 && python q2_congestion.py
cd Task03 && python q3_http_performance.py
cd Task04 && python q4_dns_cache.py
cd Task05 && python q5_mm1_queue.py
cd Task06 && python q6_quic_tls.py
cd Task07 && python q7_telemedicine_demo.py
```

Install plotting dependency if needed:

```bash
python -m pip install -r requirements.txt
```

## Important interpretation notes

1. The Q1 socket program uses loopback sockets and verifies the expected UDP acknowledgements and 100,000-byte TCP receive count. It is not a WAN loss experiment.
2. Q2 reproduces the assignment's supplied 20-RTT Reno/Tahoe model and its expected segment totals. This is a simplified teaching model, not a full TCP stack.
3. Q3 uses an explicit RTT accounting model with negligible transmission times, as stated in the brief. Browser DevTools measurements remain to be collected on a real browser/network.
4. Q4 is an iterative DNS delegation simulation based on the supplied `SERVERS` dictionary. It is not a live public DNS lookup.
5. Q5 includes the exact M/M/1 formula results and a seeded discrete-event queue model. These are analytical/simulated results, not measurements from the office router.
6. Q6 uses RTT accounting. Actual TLS negotiation and HTTP/3 support must be checked against live websites using the commands in `configs/`.
7. Q7 transfers a test file over a real local TCP socket and verifies its SHA-256 digest. The 100 ms RTT and 5% loss are a separate application-level impairment illustration; localhost TCP itself was not subjected to `tc netem`.
