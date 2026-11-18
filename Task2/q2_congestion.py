"""Q2: Complete the supplied Tahoe/Reno TODO and compare 20-RTT traces."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def simulate(losses, ssthresh=16, reno=True):
    cwnd, trace = 1, []
    for rtt in range(1, 21):
        trace.append(cwnd)
        if rtt in losses:                              # TODO 1
            ssthresh = max(cwnd // 2, 2)
            cwnd = ssthresh if reno else 1
        elif cwnd < ssthresh:
            cwnd = min(cwnd * 2, ssthresh)
        else:
            cwnd += 1
    return trace

def main():
    traces = {}
    for label, reno in (("Reno", True), ("Tahoe", False)):
        tr = simulate({8, 14}, reno=reno); traces[label] = tr
        print(f"{label:<6}", " ".join(f"{w:2d}" for w in tr), f"| segments sent {sum(tr)}")
    print("Extra segments delivered by Reno:", sum(traces['Reno']) - sum(traces['Tahoe']))
    plt.figure(figsize=(9, 5))
    plt.plot(range(1, 21), traces['Reno'], marker='o', label='TCP Reno')
    plt.plot(range(1, 21), traces['Tahoe'], marker='s', label='TCP Tahoe')
    plt.xlabel('Round trip'); plt.ylabel('Congestion window (segments)'); plt.title('Tahoe vs Reno: losses at RTT 8 and 14')
    plt.grid(True, alpha=.3); plt.legend(); plt.tight_layout(); plt.savefig('../graphs/q2_tahoe_reno.png', dpi=160)

if __name__ == '__main__': main()
