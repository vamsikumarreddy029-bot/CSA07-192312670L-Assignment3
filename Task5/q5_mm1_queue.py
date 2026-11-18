"""Q5: M/M/1 calculations and reproducible FIFO/priority queue simulation."""
import random
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def mm1(lam, mu):
    if lam >= mu: return None
    rho = lam / mu
    L = rho / (1 - rho)
    W = 1 / (mu - lam)
    return rho, L, W

def simulate_queue(n=5000, video_rate=120, backup_rate=680, service_rate=1000, seed=7, priority=False):
    """M/M/1 arrivals; service times exponential. Priority is non-preemptive video priority."""
    rng = random.Random(seed)
    events=[]
    for cls, rate in [('video', video_rate), ('backup', backup_rate)]:
        t=0.0
        for i in range(n):
            t += rng.expovariate(rate)
            events.append((t, cls, i))
    events.sort()
    # Work-conserving single server. Non-preemptive priority among jobs waiting at service completion.
    import heapq
    waiting=[]; server_free=0.0; video_delays=[]; backup_delays=[]; idx=0; now=0.0
    while idx < len(events) or waiting:
        if not waiting and idx < len(events) and server_free < events[idx][0]: server_free=events[idx][0]
        while idx < len(events) and events[idx][0] <= server_free:
            at, cls, seq=events[idx]; rank=0 if (priority and cls=='video') else 1
            heapq.heappush(waiting, (rank, at, seq, cls)); idx+=1
        if not waiting:
            continue
        rank, at, seq, cls=heapq.heappop(waiting)
        start=max(server_free, at)
        finish=start+rng.expovariate(service_rate)
        delay=finish-at
        (video_delays if cls=='video' else backup_delays).append(delay)
        server_free=finish
    return sum(video_delays)/len(video_delays), sum(backup_delays)/len(backup_delays)

def main():
    mu=1000
    print('M/M/1 results:')
    for lam in (500,800,900,950,990,1000):
        r=mm1(lam,mu)
        if r is None: print(f'load {lam:4d} pkt/s: unstable, queue grows without limit')
        else:
            rho,L,W=r; print(f'load {lam:4d} pkt/s: rho {rho:.2f} L {L:6.1f} pkts W {W*1000:6.1f} ms')
    w450=mm1(450,1000)[2]*1000; w900=mm1(900,1000)[2]*1000
    print(f'450 pkt/s delay={w450:.3f} ms; 900 pkt/s delay={w900:.3f} ms; ratio={w900/w450:.2f}x (not 10x under stated M/M/1 inputs)')
    print(f'Token bucket burst: 1 MB = 8 Mb; excess rate = 10-2 = 8 Mbps; burst duration = {8/8:.2f} s')
    print(f'For lambda=1500 pkt/s and W<10ms, mu must be > {1500+100:.0f} pkt/s')
    print(f'Doubled link: mu=2000, lambda=1800 => W={mm1(1800,2000)[2]*1000:.1f} ms')
    loads=list(range(100,1000,25)); delays=[mm1(x,mu)[2]*1000 for x in loads]
    plt.figure(figsize=(8,5)); plt.plot(loads,delays); plt.axhline(20,linestyle='--',label='20 ms'); plt.xlabel('Arrival rate (packets/s)'); plt.ylabel('Mean system delay (ms)'); plt.title('M/M/1 delay vs offered load'); plt.grid(True,alpha=.3); plt.legend(); plt.tight_layout(); plt.savefig('../graphs/q5_mm1_delay.png',dpi=160)
    fifo=simulate_queue(priority=False); prio=simulate_queue(priority=True)
    print(f'Queue simulation (seeded, video mean delay): FIFO={fifo[0]*1000:.2f} ms; non-preemptive video priority={prio[0]*1000:.2f} ms')
    print('Note: queue simulation uses generated Poisson arrivals and exponential service; it is a model, not a measurement from a physical router.')

if __name__ == '__main__': main()
