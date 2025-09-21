#!/usr/bin/env python3
"""
Docker ChromaDB Management Script
Provides easy commands to start, stop, and manage ChromaDB via Docker
"""

import subprocess
import sys
import time
import requests
from pathlib import Path

def run_command(cmd, check=True):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(cmd, shell=True, check=check, capture_output=True, text=True)
        return result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {cmd}")
        print(f"Error: {e.stderr}")
        return None, e.stderr

def is_chromadb_running():
    """Check if ChromaDB is running and accessible"""
    try:
        response = requests.get("http://localhost:8000/api/v1/heartbeat", timeout=5)
        return response.status_code == 200
    except:
        return False

def start_chromadb():
    """Start ChromaDB using docker-compose"""
    print("Starting ChromaDB...")
    stdout, stderr = run_command("docker-compose up -d")
    
    if stderr and "error" in stderr.lower():
        print(f"Error starting ChromaDB: {stderr}")
        return False
    
    print("Waiting for ChromaDB to be ready...")
    for i in range(30):  # Wait up to 30 seconds
        if is_chromadb_running():
            print("✅ ChromaDB is running and accessible at http://localhost:8000")
            return True
        time.sleep(1)
    
    print("❌ ChromaDB failed to start or is not accessible")
    return False

def stop_chromadb():
    """Stop ChromaDB"""
    print("Stopping ChromaDB...")
    stdout, stderr = run_command("docker-compose down")
    print("✅ ChromaDB stopped")

def restart_chromadb():
    """Restart ChromaDB"""
    stop_chromadb()
    time.sleep(2)
    start_chromadb()

def status_chromadb():
    """Check ChromaDB status"""
    if is_chromadb_running():
        print("✅ ChromaDB is running at http://localhost:8000")
    else:
        print("❌ ChromaDB is not running")
    
    # Also check Docker container status
    stdout, stderr = run_command("docker-compose ps")
    if stdout:
        print("\nDocker container status:")
        print(stdout)

def logs_chromadb():
    """Show ChromaDB logs"""
    print("ChromaDB logs:")
    stdout, stderr = run_command("docker-compose logs -f chromadb")
    if stdout:
        print(stdout)

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/docker_chroma.py [start|stop|restart|status|logs]")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "start":
        start_chromadb()
    elif command == "stop":
        stop_chromadb()
    elif command == "restart":
        restart_chromadb()
    elif command == "status":
        status_chromadb()
    elif command == "logs":
        logs_chromadb()
    else:
        print(f"Unknown command: {command}")
        print("Available commands: start, stop, restart, status, logs")
        sys.exit(1)

if __name__ == "__main__":
    main()
