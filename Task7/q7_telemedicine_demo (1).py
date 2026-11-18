"""Q7: Local socket demo for reliable patient-file transfer and chat under an impairment model.
The impairment is simulated in the application layer so it runs without root/tc privileges.
"""
import socket, threading, time, random, hashlib, os
HOST='127.0.0.1'; PORT=0

def recv_exact(conn,n):
    data=b''
    while len(data)<n:
        part=conn.recv(n-len(data))
        if not part: raise ConnectionError('peer closed early')
        data+=part
    return data

def server(sock, ready, received):
    sock.listen(1); ready.set(); conn,_=sock.accept()
    with conn:
        header=recv_exact(conn,8); size=int.from_bytes(header,'big')
        payload=recv_exact(conn,size)
        received.append(payload)
        msglen=int.from_bytes(recv_exact(conn,4),'big')
        chat=recv_exact(conn,msglen).decode()
        conn.sendall(hashlib.sha256(payload).hexdigest().encode()+b'\n'+chat.upper().encode())

def main():
    payload=(b'Patient X-ray image data - simulated test file.\n'*20000)
    # Emulate 100 ms RTT as 50 ms one-way application delay. A seeded 5% loss is recorded;
    # reliable TCP socket transport retransmits below the application layer in a real network.
    rtt_ms=100; loss_pct=5; rng=random.Random(19)
    simulated_packets=100; lost=sum(1 for _ in range(simulated_packets) if rng.random()<loss_pct/100)
    srv=socket.socket(); srv.bind((HOST,0)); ready=threading.Event(); received=[]
    th=threading.Thread(target=server,args=(srv,ready,received)); th.start(); ready.wait()
    start=time.perf_counter(); time.sleep(rtt_ms/2000)
    cli=socket.create_connection(srv.getsockname()); cli.sendall(len(payload).to_bytes(8,'big')+payload)
    chat='Please confirm image received'; cli.sendall(len(chat.encode()).to_bytes(4,'big')+chat.encode())
    response=b''
    while True:
        chunk=cli.recv(4096)
        if not chunk: break
        response+=chunk
    cli.close(); th.join(); elapsed=time.perf_counter()-start; srv.close()
    digest, reply=response.split(b'\n',1)
    ok=digest.decode()==hashlib.sha256(payload).hexdigest() and received[0]==payload
    print(f'File bytes sent: {len(payload)}')
    print(f'Integrity verified (SHA-256): {ok}')
    print(f'Chat request: {chat}')
    print(f'Server chat response: {reply.decode()}')
    print(f'Local transfer elapsed: {elapsed*1000:.2f} ms (includes local processing; not a 4G benchmark)')
    print(f'Impairment model: RTT={rtt_ms} ms; assumed random loss={loss_pct}%; sampled lost datagrams in 100-trial model={lost}')
    print('Important: localhost TCP delivery itself was not subjected to tc netem; loss count is a separate seeded model, not a packet capture.')

if __name__=='__main__': main()
