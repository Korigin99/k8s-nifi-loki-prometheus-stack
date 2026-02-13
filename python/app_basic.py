import os
from datetime import datetime

def main():
    pod_name = os.getenv("HOSTNAME", "unknown-pod")
    print(f"[{datetime.now().isoformat()}] [BASIC] Hello from FlowKube!")
    print(f"[{datetime.now().isoformat()}] [BASIC] Pod Name: {pod_name}")
    print(f"[{datetime.now().isoformat()}] [BASIC] Task completed successfully.")

if __name__ == "__main__":
    main()