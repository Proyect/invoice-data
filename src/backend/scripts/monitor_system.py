#!/usr/bin/env python3
'''
Script de monitoreo del sistema
'''

import psutil
import time
import json
from datetime import datetime

def monitor_system():
    '''Monitorea el rendimiento del sistema'''
    
    print("📊 MONITOREO DEL SISTEMA")
    print("=" * 30)
    
    while True:
        # Información del sistema
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Información de procesos
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                if proc.info['cpu_percent'] > 5.0:  # Procesos que usan > 5% CPU
                    processes.append(proc.info)
            except:
                pass
        
        # Mostrar información
        print(f"\n⏰ {datetime.now().strftime('%H:%M:%S')}")
        print(f"CPU: {cpu_percent}%")
        print(f"RAM: {memory.percent}% ({memory.used / 1024**3:.1f} GB / {memory.total / 1024**3:.1f} GB)")
        print(f"Disco: {disk.percent}% ({disk.used / 1024**3:.1f} GB / {disk.total / 1024**3:.1f} GB)")
        
        if processes:
            print("🔥 Procesos activos:")
            for proc in processes[:5]:  # Top 5
                print(f"   {proc['name']}: {proc['cpu_percent']:.1f}% CPU, {proc['memory_percent']:.1f}% RAM")
        
        time.sleep(30)  # Monitorear cada 30 segundos

if __name__ == "__main__":
    try:
        monitor_system()
    except KeyboardInterrupt:
        print("\n👋 Monitoreo detenido")
