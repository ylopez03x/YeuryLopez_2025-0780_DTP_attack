# DTP VLAN Hopping - Double Tagging Attack
**Autor:** Yeury Lopez  
**Matrícula:** 2025-0780  
**Curso:** Networking Security  

---

## 📹 Video del Ataque
> [https://www.youtube.com/watch?v=I3TxOfy8NWo]

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
<img width="884" height="719" alt="image" src="https://github.com/user-attachments/assets/615d9efd-0a7e-40c0-acd7-c31c6f66d32b" />


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

show vlan brief en SW1
 <img width="889" height="313" alt="image" src="https://github.com/user-attachments/assets/addb9a92-f01f-4dfb-8257-be11f872c79b" />

show mac address-table antes del ataque
 <img width="605" height="222" alt="image" src="https://github.com/user-attachments/assets/5f5597ab-7960-4576-96b0-2f3f5ee3072f" />

Ubuntu sin recibir paquetes de Kali
 <img width="975" height="110" alt="image" src="https://github.com/user-attachments/assets/5eba5f68-3cb0-462a-89b0-d2d4df624abe" />
 
Script corriendo en Kali
 <img width="975" height="413" alt="image" src="https://github.com/user-attachments/assets/53f02af3-6a2d-494e-adbc-50c583e636e0" />
 
Ubuntu recibiendo paquetes ICMP de Kali
 <img width="975" height="434" alt="image" src="https://github.com/user-attachments/assets/307c0daf-a8ce-4845-b279-07fbe04dceb1" />

MAC de Kali aparece en VLAN 20
 <img width="639" height="280" alt="image" src="https://github.com/user-attachments/assets/40342e90-3e92-462d-953b-df70c82fef42" />

Configuracion de la contramedida en SW1
 <img width="626" height="373" alt="image" src="https://github.com/user-attachments/assets/ea23e61a-7f80-404f-943f-3923d2c3b65e" />

Ubuntu sin recibir paquetes despues de contramedida
 <img width="975" height="110" alt="image" src="https://github.com/user-attachments/assets/dcab1787-e577-4894-9b20-35dc956cd53f" />

MAC de Kali ya no aparece en VLAN 20
 <img width="578" height="248" alt="image" src="https://github.com/user-attachments/assets/a6b9d3c9-77e5-4f0a-9596-e1549ad51a02" />


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
