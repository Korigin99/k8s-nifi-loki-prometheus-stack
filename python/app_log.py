import time
import random
import logging
import sys

# 표준 출력(stdout)으로 로그가 나가야 Fluent Bit이 수집 가능합니다.
logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

messages = [
    "User session initialized",
    "Database query took 500ms",
    "API Connection reset by peer",
    "Unauthorized access attempt detected",
    "Cache synchronization complete"
]

def generate_logs():
    print("--- LOG GENERATOR START ---")
    for i in range(15):
        level = random.choice(['INFO', 'WARN', 'ERROR'])
        msg = random.choice(messages)
        
        if level == 'INFO':
            logging.info(f"Task-{i}: {msg}")
        elif level == 'WARN':
            logging.warning(f"Task-{i}: {msg}")
        else:
            logging.error(f"Task-{i}: {msg}")
            
        time.sleep(0.8)
    print("--- LOG GENERATOR END ---")

if __name__ == "__main__":
    generate_logs()