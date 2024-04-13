import signal
import sys
import time
import subprocess

def sigterm_handler(signum, frame):
    print("SIGTERM received. Stopping the Docker Compose services.")
    try:
        subprocess.run(["sudo", "docker-compose", "-f", "docker-compose.prod.yml", "down", "-v"], check=True)
        print("Docker Compose services stopped.")
    except subprocess.CalledProcessError as e:
        print(f"Error stopping Docker Compose services: {e}")
    
    print("Restarting the Docker Compose services.")
    try:
        subprocess.run(["sudo", "docker-compose", "-f", "docker-compose.prod.yml", "up", "-d", "--build"], check=True)
        print("Docker Compose services restarted.")
    except subprocess.CalledProcessError as e:
        print(f"Error restarting Docker Compose services: {e}")

def main():
    # Register SIGTERM signal handler
    signal.signal(signal.SIGTERM, sigterm_handler)

    print("Application is running...")
    # Your application code goes here
    try:
        while True:
            time.sleep(20)
    except KeyboardInterrupt:
        print("KeyboardInterrupt received. Exiting.")
        sys.exit(0)

if __name__ == "__main__":
    main()
