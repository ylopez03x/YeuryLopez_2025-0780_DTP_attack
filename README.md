# DTP VLAN Hopping - Double Tagging Attack
**Autor:** Yeury Lopez  
**Matrícula:** 2025-0780  
**Curso:** Networking Security  

---

## 📹 Video del Ataque
> [Insertar enlace del video aquí]

---

## 🎯 Objetivo del Laboratorio

Demostrar cómo un atacante puede saltar entre VLANs sin pasar por un router, explotando la VLAN nativa de un puerto trunk mediante la técnica de Double Tagging (doble etiquetado 802.1Q), logrando acceso no autorizado a segmentos de red restringidos.

---

## 🎯 Objetivo del Script

El script `dtp_attack.py` envía paquetes con doble etiqueta 802.1Q. La primera etiqueta corresponde a la VLAN nativa del trunk (VLAN 1), que el switch elimina al procesar el frame. La segunda etiqueta corresponde a la VLAN víctima (VLAN 20), haciendo que el switch reenvíe el paquete a esa VLAN sin autorización.

### Parámetros usados

| Parámetro | Valor | Descripción |
|---|---|---|
| `IFACE` | `eth0` | Interfaz de red del atacante |
| `SRC_MAC` | Auto-detectada | MAC address de la interfaz |
| `DST_MAC` | `ff:ff:ff:ff:ff:ff` | Broadcast |
| `VLAN_OUTER` | `1` | VLAN nativa del trunk (outer tag) |
| `VLAN_INNER` | `20` | VLAN víctima (inner tag) |
| `SRC_IP` | `172.20.25.100` | IP del atacante |
| `DST_IP` | `172.7.80.100` | IP de la víctima |

### Requisitos para utilizar la herramienta

```bash
# Sistema operativo
Kali Linux

# Dependencias
pip3 install scapy

# Permisos
sudo (root)

# Red
Puerto del atacante configurado como trunk con VLAN nativa 1
Switch con VLAN nativa sin protección
```

---

## 📋 Documentación del funcionamiento del script

El ataque Double Tagging funciona así:

```
Kali envía: [Ether][Dot1Q vlan=1][Dot1Q vlan=20][IP][ICMP]
                        ↓
SW1 recibe el frame en puerto trunk con native VLAN 1
SW1 quita el outer tag (VLAN 1) porque es la VLAN nativa
SW1 reenvía el frame con inner tag (VLAN 20) hacia Ubuntu
                        ↓
Ubuntu recibe el paquete como si viniera de VLAN 20
```

1. El script construye paquetes ICMP con doble etiqueta 802.1Q
2. Envía un paquete por segundo continuamente
3. El switch quita el outer tag (VLAN 1 = nativa) y procesa el inner tag (VLAN 20)
4. Ubuntu en VLAN 20 recibe los paquetes aunque Kali está en VLAN 10

**Evidencia del ataque en el switch:**
```
show mac address-table
→ MAC de Kali aparece en VLAN 20 (siendo que su puerto es VLAN 10)
```

---

## 🌐 Documentación de la Red

### Topología

```
┌─────────────┐    eth0/e0/0     ┌──────────────┐    e0/1/e0    ┌─────────────┐
│ Kali Linux  │──────────────────│     SW1       │───────────────│   Ubuntu    │
│  Atacante   │   TRUNK          │   IOL L2      │   ACCESS      │   Víctima   │
│172.20.25.100│   native VLAN 1  │               │   VLAN 20     │172.7.80.100 │
│  VLAN 10    │                  └───────────────┘               │  VLAN 20    │
└─────────────┘                                                  └─────────────┘
```

### VLANs

| VLAN ID | Nombre | Dispositivo |
|---|---|---|
| 1 | default | VLAN nativa (explotada) |
| 10 | ATACANTE | Kali Linux |
| 20 | VICTIMA | Ubuntu |

### Direccionamiento IP

| Dispositivo | Interfaz | IP | VLAN |
|---|---|---|---|
| Kali Linux | eth0 | 172.20.25.100/24 | 10 |
| Ubuntu | ens3 | 172.7.80.100/24 | 20 |

### Configuración SW1 (vulnerable)

```
interface e0/0
 switchport trunk encapsulation dot1q
 switchport mode trunk
 switchport trunk native vlan 1
 switchport trunk allowed vlan 1,10,20
```

---

## 📸 Capturas de pantalla requeridas

> **Instrucciones:** Toma estas capturas durante la demostración y agrégalas aquí.

1. `01_topologia_eve.png` — Topología completa en EVE-NG con nombre y matrícula visible
2. `02_vlan_brief_inicial.png` — `show vlan brief` en SW1 (Kali en VLAN 10, Ubuntu en VLAN 20)
3. `03_mac_table_inicial.png` — `show mac address-table` antes del ataque
4. `04_tcpdump_sin_ataque.png` — Ubuntu sin recibir paquetes de Kali
5. `05_script_ejecutando.png` — Script corriendo en Kali
6. `06_tcpdump_con_ataque.png` — Ubuntu recibiendo paquetes ICMP de Kali (VLAN hopping exitoso)
7. `07_mac_table_ataque.png` — MAC de Kali aparece en VLAN 20
8. `08_contramedida_config.png` — Configuración de la contramedida en SW1
9. `09_tcpdump_contramedida.png` — Ubuntu sin recibir paquetes después de la contramedida
10. `10_mac_table_contramedida.png` — MAC de Kali ya no aparece en VLAN 20

---

## 🛡️ Contramedidas

### Contramedida 1 — Deshabilitar DTP y modo access explícito

```
SW1# configure terminal
SW1(config)# interface e0/0
SW1(config-if)# switchport mode access
SW1(config-if)# switchport access vlan 10
SW1(config-if)# switchport nonegotiate
SW1(config-if)# no shutdown
SW1(config-if)# end
```

**Por qué funciona:** Al poner el puerto en modo access explícito y deshabilitar DTP, el switch no acepta frames con etiquetas 802.1Q. Los paquetes double-tagged son descartados.

### Contramedida 2 — Cambiar VLAN nativa a una VLAN sin uso

```
SW1# configure terminal
SW1(config)# vlan 999
SW1(config-vlan)# name NO-USAR
SW1(config-vlan)# exit
SW1(config)# interface e0/0
SW1(config-if)# switchport trunk native vlan 999
SW1(config-if)# end
```

**Por qué funciona:** Si la VLAN nativa es una VLAN que no se usa en la red, el outer tag del ataque no corresponderá a ninguna VLAN válida y el paquete será descartado.

### Contramedida 3 — Habilitar VLAN nativa tagging

```
SW1# configure terminal
SW1(config)# vlan dot1q tag native
SW1(config)# end
```

**Por qué funciona:** Fuerza el etiquetado de todos los frames incluyendo los de la VLAN nativa, eliminando la asimetría que el Double Tagging explota.

---

## 🔧 Cómo ejecutar

```bash
# 1. Clonar el repositorio
git clone https://github.com/[usuario]/dtp-vlan-hopping

# 2. Instalar dependencias
pip3 install scapy

# 3. Configurar SW1 en modo trunk con native VLAN 1
# interface e0/0
#  switchport trunk encapsulation dot1q
#  switchport mode trunk
#  switchport trunk native vlan 1

# 4. Ejecutar
sudo python3 dtp_attack.py
```

---

## ⚠️ Disclaimer

Este script es únicamente para fines educativos y de laboratorio. El uso de esta herramienta en redes sin autorización expresa es ilegal y está penado por la ley.
