"""Q6: Connection setup RTT accounting and migration comparison."""
RTT_MS=100

def main():
    cases=[('TCP + TLS 1.2 full handshake',3),('TCP + TLS 1.3 full handshake',2),('QUIC first visit (1-RTT handshake)',1),('QUIC 0-RTT resumption (early request data)',0)]
    print(f'RTT = {RTT_MS} ms; time until request data can be sent:')
    for name,rtts in cases: print(f'{name:<45} {rtts} RTT = {rtts*RTT_MS} ms')
    print('\nWi-Fi to 5G during transfer (illustrative handshake accounting):')
    print('TCP + TLS 1.3: old 4-tuple path breaks; reconnect + TCP/TLS setup typically costs about 2 RTT = 200 ms, excluding detection.')
    print('QUIC: connection ID can identify the connection on the new path; path validation may cost about 0-1 RTT = 0-100 ms, without a full new TLS handshake.')
    print('0-RTT replay warning: early data can be replayed. Do not send money transfers or other non-idempotent state-changing operations as 0-RTT.')
    print('QUIC uses UDP; if blocked by a firewall, the client should fall back to TCP-based HTTPS (HTTP/2) where supported.')

if __name__ == '__main__': main()
