"""Run each task program and save its stdout in results/."""
from pathlib import Path
import subprocess, sys
ROOT=Path(__file__).resolve().parent
TASKS=[('Task01','q1_sockets.py'),('Task02','q2_congestion.py'),('Task03','q3_http_performance.py'),('Task04','q4_dns_cache.py'),('Task05','q5_mm1_queue.py'),('Task06','q6_quic_tls.py'),('Task07','q7_telemedicine_demo.py')]
for folder,script in TASKS:
    print(f'Running {folder}/{script} ...')
    result=subprocess.run([sys.executable,script],cwd=ROOT/folder,text=True,capture_output=True)
    output=result.stdout + (('\nSTDERR:\n'+result.stderr) if result.stderr else '')
    (ROOT/'results'/f'{folder.lower()}_output.txt').write_text(output,encoding='utf-8')
    if result.returncode:
        print(output); raise SystemExit(result.returncode)
    print(output,end='')
print('All seven Python task programs completed successfully.')
