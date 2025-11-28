# client.py
import socket
import logging
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

SERVER_IP = '100.71.64.11'
MAIN_PORT = 8200
MAX_RETRIES = 10
RETRY_DELAY = 2

def connect_with_retry(ip, port, max_retries=MAX_RETRIES):
    for attempt in range(1, max_retries + 1):
        try:
            logging.info(f"[ATTEMPT {attempt}/{max_retries}] Connecting to {ip}:{port}...")
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((ip, port))
            logging.info(f"[CONNECTED] {ip}:{port}")
            return sock
            
        except (socket.timeout, ConnectionRefusedError, OSError) as e:
            logging.warning(f"[ATTEMPT {attempt}] Failed: {e}")
            if attempt < max_retries:
                logging.info(f"Retrying in {RETRY_DELAY} seconds...")
                time.sleep(RETRY_DELAY)
            else:
                logging.error(f"Failed to connect after {max_retries} attempts")
                raise

def main():
    logging.info("CLIENT STARTED")
    
    try:
        sock = connect_with_retry(SERVER_IP, MAIN_PORT)
        logging.info(f"[STEP 1] Connected to main server {SERVER_IP}:{MAIN_PORT}")
        
        logging.info("[STEP 2] Receiving assigned port...")
        new_port_data = sock.recv(1024)
        
        if not new_port_data.isdigit():
            logging.error(f"Server error: {new_port_data.decode()}")
            sock.close()
            return
        
        new_port = int(new_port_data.decode())
        logging.info(f"[ASSIGNED PORT] {new_port}")
        sock.close()

        logging.info(f"[STEP 3] Connecting to worker port {new_port}...")
        worker_sock = connect_with_retry(SERVER_IP, new_port)
        logging.info(f"[CONNECTED] Ready for messaging")
        
        message_num = 0
        with worker_sock:
            while True:
                message = input("Message (exit to quit): ")
                if message.lower() == 'exit':
                    logging.info("Disconnecting...")
                    break
                
                if not message.strip():
                    print("Empty message. Try again.")
                    continue
                
                message_num += 1
                logging.info(f"[SEND #{message_num}] {message}")
                worker_sock.sendall(message.encode())
                
                data = worker_sock.recv(1024)
                response = data.decode()
                print(f"Response: {response}")
                logging.info(f"[RECV #{message_num}] {response}")
        
        logging.info("CLIENT DISCONNECTED")
        
    except Exception as e:
        logging.error(f"ERROR: {e}")

if __name__ == "__main__":
    main()
