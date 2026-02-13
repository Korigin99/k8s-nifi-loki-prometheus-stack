import math
import time
import os

def heavy_calculation(n):
    print(f"[CPU] Starting intensive calculation up to {n}...")
    start = time.time()
    primes = []
    for i in range(2, n):
        is_prime = True
        for j in range(2, int(math.sqrt(i)) + 1):
            if i % j == 0:
                is_prime = False
                break
        if is_prime:
            primes.append(i)
    end = time.time()
    return len(primes), end - start

if __name__ == "__main__":
    count, duration = heavy_calculation(80000)
    print(f"[CPU] Found {count} prime numbers.")
    print(f"[CPU] Execution Time: {duration:.2f} seconds.")
    print("[CPU] Load test finished.")