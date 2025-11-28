import socket
import threading
import logging
import subprocess
import platform


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class PortManager:
    def __init__(self, start, end):
        self.start = start
        self.end = end
        self.lock = threading.Lock()
        self.current = start
        self.used = set()

    def acquire_port(self):
        with self.lock:
            for _ in range(self.start, self.end + 1):
                port = self.current
                self.current += 1
                if self.current > self.end:
                    self.current = self.start
                if port not in self.used:
                    self.used.add(port)
                    logging.info(f"Port {port} acquired. Active ports: {len(self.used)}")
                    return port
            logging.warning("No free ports available")
            return None

    def release_port(self, port):
        with self.lock:
            self.used.discard(port)
            logging.info(f"Port {port} released. Active ports: {len(self.used)}")

def show_tcp_handshake(client_addr, port):
        logging.info(f"  Client IP: {client_addr[0]}")
        logging.info(f"  Client Port: {client_addr[1]}")
        logging.info(f"  Server Port: {port}")
        logging.info(f"  Status: ESTABLISHED")
        logging.info(f"▲▲▲▲▲▲▲▲▲ CONNECTION ESTABLISHED ▲▲▲▲▲▲▲▲▲")


def handle_client(conn, addr, port, port_manager):
    logging.info(f"═══════════════════════════════════════════════════════════")
    logging.info(f"[CONNECTED] Client {addr} connected to port {port}")
    logging.info(f"Socket peer name: {conn.getpeername()}")
    logging.info(f"Socket sock name: {conn.getsockname()}")
    logging.info(f"═══════════════════════════════════════════════════════════")

    message_count = 0
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                logging.info(f"[CONNECTION CLOSED] No data received from {addr} - connection closing")
                break

            message = data.decode().strip()
            message_count += 1

            if not message:
                response = f"[Port {port}] Empty message received. Please send some text."
                logging.info(f"[EMPTY MESSAGE] from {addr} on port {port}")
            else:
                response = f"Echo from port {port}: {message}"
                logging.info(f"[MESSAGE #{message_count}] from {addr} on port {port}: '{message}'")

            conn.sendall(response.encode())
            logging.info(f"[RESPONSE SENT] to {addr}: '{response}'")

    except Exception as e:
        logging.error(f"[ERROR] handling client {addr} on port {port}: {e}")
    finally:
        conn.close()
        logging.info(f"╔═══════════════════════════════════════════════════════════╗")
        logging.info(f"║ [DISCONNECTED] {addr} from port {port}                   ║")
        logging.info(f"║ Total messages received: {message_count}                    ║")
        logging.info(f"╚═══════════════════════════════════════════════════════════╝")
        port_manager.release_port(port)

def client_handler_main(port, port_manager):
    logging.info(f"┌─────────────────────────────────────────────────────────────┐")
    logging.info(f"│ [WORKER STARTED] Listening on port {port}")
    logging.info(f"└─────────────────────────────────────────────────────────────┘")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('0.0.0.0', port))
        s.listen(1)
        logging.info(f"[SOCKET READY] Worker process listening on 0.0.0.0:{port}")

        try:
            logging.info(f"[WAITING] Waiting for TCP handshake on port {port}...")
            client_conn, client_addr = s.accept()

            show_tcp_handshake(client_addr, port)

            handle_client(client_conn, client_addr, port, port_manager)
        except Exception as e:
            logging.error(f"[ERROR] in client handler on port {port}: {e}")
        finally:
            port_manager.release_port(port)