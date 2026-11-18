"""Q4: Iterative DNS resolver with a TTL cache; completes supplied TODO."""
import time
SERVERS = {
    'root': {'in.': 'tld-in', 'com.': 'tld-com'},
    'tld-in': {'ac.in.': 'ns-ac'},
    'tld-com': {'example.com.': 'ns-example'},
    'ns-ac': {'simats.ac.in.': 'ns-simats'},
    'ns-simats': {'results.simats.ac.in.': '10.20.30.40'},
    'ns-example': {'www.example.com.': '93.184.216.34'},
}
cache = {}
TTL_SECONDS = 300

def resolve(name, now=None):
    now = time.monotonic() if now is None else now
    if name in cache and cache[name][1] > now: return cache[name][0], 0
    if name in cache: del cache[name]
    server, queries = 'root', 0
    while True:
        queries += 1
        matches = [(suffix, value) for suffix, value in SERVERS[server].items() if name.endswith(suffix)]
        if not matches: raise LookupError(f'No delegation/record for {name} at {server}')
        suffix, value = max(matches, key=lambda item: len(item[0]))
        if any(ch.isdigit() for ch in value):
            cache[name] = (value, now + TTL_SECONDS)
            return value, queries
        server = value

def main():
    for n in ('results.simats.ac.in.', 'www.example.com.', 'results.simats.ac.in.'):
        ip, q = resolve(n); print(f'{n:<24} {ip:<15} queries sent: {q}')
    print(f'Cache TTL: {TTL_SECONDS} seconds')

if __name__ == '__main__': main()
