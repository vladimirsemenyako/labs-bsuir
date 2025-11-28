from server import PortManager, client_handler_main
import socket 
import multiprocessing
import os
import signal
import sys
import logging
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - PID:%(process)d - %(levelname)s - %(message)s',
    stream=sys.stdout  
)

logger = logging.getLogger(__name__)

BASE_PORT = int(os.getenv("BASE_PORT", 8201))
MAIN_PORT = int(os.getenv("MAIN_PORT", 8200))
MAX_PORT = int(os.getenv("MAX_PORT", 8300))

processes = []
server_socket = None
should_exit = False


def shutdown_handler(sig, frame):
    global should_exit
    
    sig_name = {
        signal.SIGTERM: "SIGTERM",
        signal.SIGINT: "SIGINT",
        signal.SIGHUP: "SIGHUP"
    }.get(sig, f"SIG{sig}")
    
    logger.warning(f"╔════════════════════════════════════════════════════════════╗")
    logger.warning(f"║ Received {sig_name}. Starting graceful shutdown...")
    logger.warning(f"╚════════════════════════════════════════════════════════════╝")
    
    should_exit = True
    
    if server_socket:
        try:
            server_socket.close()
            logger.info("Server socket closed - no new connections accepted")
        except Exception as e:
            logger.error(f"Error closing socket: {e}")
    
    logger.info(f"Sending SIGTERM to {len(processes)} worker processes...")
    for i, process in enumerate(processes, 1):
        if process.is_alive():
            process.terminate()
            logger.info(f"  [{i}/{len(processes)}] SIGTERM → PID {process.pid}")
    

    logger.info("Waiting for processes to shutdown (5 second timeout)...")
    time.sleep(5)
    
    logger.info("Checking remaining processes...")
    killed_count = 0
    for process in processes:
        if process.is_alive():
            logger.warning(f"  Process PID {process.pid} still alive. Sending SIGKILL...")
            process.kill()
            killed_count += 1
        
        process.join(timeout=2)
    
    logger.info(f"Process cleanup complete: {len(processes) - killed_count} graceful, {killed_count} forced")
    
    logger.warning(f"╔════════════════════════════════════════════════════════════╗")
    logger.warning(f"║ Shutdown complete. Exit code: 0")
    logger.warning(f"╚════════════════════════════════════════════════════════════╝")
    
    sys.exit(0)


def cleanup_zombies():
    global processes
    alive = []
    
    for process in processes:
        if process.is_alive():
            alive.append(process)
        else:
            process.join(timeout=0)
    
    if len(alive) < len(processes):
        cleaned = len(processes) - len(alive)
        logger.debug(f"Cleaned up {cleaned} zombie processes")
    
    processes = alive


def main():
    global processes, server_socket, should_exit
    
    signal.signal(signal.SIGTERM, shutdown_handler) 
    signal.signal(signal.SIGINT, shutdown_handler)   
    signal.signal(signal.SIGHUP, shutdown_handler)   
    
    logger.info(f"╔════════════════════════════════════════════════════════════╗")
    logger.info(f"║ Server starting (PID: {os.getpid()})")
    logger.info(f"║ Main port: {MAIN_PORT}")
    logger.info(f"║ Worker ports: {BASE_PORT}-{MAX_PORT}")
    logger.info(f"║ Container mode: YES")
    logger.info(f"╚════════════════════════════════════════════════════════════╝")
    
    port_manager = PortManager(BASE_PORT, MAX_PORT)
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server_socket = server
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            
            server.bind(('0.0.0.0', MAIN_PORT))
            server.listen(10)
            
            logger.info(f"✓ Server listening on 0.0.0.0:{MAIN_PORT}")
            logger.info(f"✓ Waiting for clients... (Press Ctrl+C to stop)")
            
            connection_count = 0
            
            while not should_exit:
                try:
                    cleanup_zombies()
                    
                    server.settimeout(1)
                    
                    try:
                        conn, addr = server.accept()
                    except socket.timeout:
                        continue
                    
                    connection_count += 1
                    logger.info(f"[#{connection_count}] Connection from {addr[0]}:{addr[1]}")
                    
                    port = port_manager.acquire_port()
                    if port is None:
                        logger.warning(f"[#{connection_count}] No free ports available. Rejecting {addr[0]}")
                        conn.sendall(b"Server busy, try later")
                        conn.close()
                        continue
                    
                    logger.info(f"[#{connection_count}] Assigned port {port} to {addr[0]}")
                    conn.sendall(str(port).encode())
                    conn.close()

                    process = multiprocessing.Process(
                        target=client_handler_main,
                        args=(port, port_manager),
                        name=f"Worker-Port-{port}"
                    )
                    process.daemon = True
                    process.start()
                    processes.append(process)
                    
                    logger.info(f"[#{connection_count}] Started worker process PID {process.pid} for port {port}")
                    logger.debug(f"Active processes: {len(processes)}")
                    
                except KeyboardInterrupt:
                    logger.info("KeyboardInterrupt received")
                    shutdown_handler(signal.SIGINT, None)
                except Exception as e:
                    if not should_exit:
                        logger.error(f"Error handling connection: {e}")
    
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
