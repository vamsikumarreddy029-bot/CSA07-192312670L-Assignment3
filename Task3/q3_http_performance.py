"""Q3: HTTP load-time model using assignment RTT and object counts."""
RTT_MS = 50
OBJECTS = 80

def main():
    rtt = RTT_MS
    models = {
        'Non-persistent, one at a time': 2 * (1 + OBJECTS),
        'Persistent HTTP/1.1, no pipelining': 2 + OBJECTS,
        'Persistent HTTP/1.1, pipelining': 3,
        '6 parallel non-persistent connections': 2 + 2 * ((OBJECTS + 5) // 6),
    }
    print('Assumptions: one RTT for TCP setup, one RTT for each request/response; negligible transmission time.')
    for name, trips in models.items(): print(f'{name:<44} {trips:3d} RTT = {trips*rtt:5.0f} ms')
    bundled = {'Non-persistent, 8 bundles + HTML': 2 * 9, 'Persistent no-pipelining, 8 bundles + HTML': 1 + 9}
    print('\nWith 80 objects combined into 8 bundles (9 total resources including HTML):')
    for name, trips in bundled.items(): print(f'{name:<44} {trips:3d} RTT = {trips*rtt:5.0f} ms')
    print('\nSecond visit: fresh max-age cache can avoid object requests; ETag revalidation still requires request/response RTTs.')
    for extra in (0, 50, 200): print(f'Added one-way-independent RTT delay {extra} ms: effective RTT {rtt+extra} ms; pipelined baseline {3*(rtt+extra)} ms')

if __name__ == '__main__': main()
