# DAAssist - Quick Start Proxmox LXC

Guida rapida per creare e installare DAAssist su container LXC Proxmox.

## Comandi Rapidi

### 1. Verifica Template Disponibile

```bash
# Lista template disponibili
pveam available | grep ubuntu-22.04

# Se non presente, scarica il template
pveam download local ubuntu-22.04-standard_22.04-1_amd64.tar.zst
```

### 2. Identifica il tuo Storage

```bash
# Lista storage disponibili
pvesm status

# Output esempio:
# Name             Type     Status           Total            Used       Available        %
# local            dir      active       952689868       178055396       725791352   18.69%
# local-lvm        lvmthin  active       100663296        15728640        84934656   15.62%
# zfs              zfspool  active       500000000        50000000       450000000   10.00%
```

### 3. Crea Container LXC

**IMPORTANTE**: Sostituisci `<STORAGE>` con il nome del tuo storage (es. `local`, `local-lvm`, `zfs`)

#### Opzione A: Storage ZFS

```bash
pct create 615 local:vztmpl/ubuntu-22.04-standard_22.04-1_amd64.tar.zst \
  --hostname daassist \
  --memory 4096 \
  --cores 2 \
  --storage zfs \
  --rootfs zfs:20 \
  --net0 name=eth0,bridge=vmbr0,ip=dhcp \
  --features nesting=1 \
  --unprivileged 1
```

#### Opzione B: Storage Local-LVM (più comune)

```bash
pct create 615 local:vztmpl/ubuntu-22.04-standard_22.04-1_amd64.tar.zst \
  --hostname daassist \
  --memory 4096 \
  --cores 2 \
  --storage local-lvm \
  --rootfs local-lvm:20 \
  --net0 name=eth0,bridge=vmbr0,ip=dhcp \
  --features nesting=1 \
  --unprivileged 1
```

#### Opzione C: Storage Local (directory)

```bash
pct create 615 local:vztmpl/ubuntu-22.04-standard_22.04-1_amd64.tar.zst \
  --hostname daassist \
  --memory 4096 \
  --cores 2 \
  --storage local \
  --rootfs local:20 \
  --net0 name=eth0,bridge=vmbr0,ip=dhcp \
  --features nesting=1 \
  --unprivileged 1
```

**Parametri**:
- `615` = ID container (scegli un ID libero)
- `--memory 4096` = 4GB RAM (minimo consigliato)
- `--cores 2` = 2 CPU cores
- `--rootfs <storage>:20` = 20GB disco
- `--features nesting=1` = **OBBLIGATORIO** per Docker
- `--unprivileged 1` = Container non privilegiato (più sicuro)

### 4. Avvia Container

```bash
pct start 615
```

### 5. Verifica IP Assegnato (se DHCP)

```bash
pct exec 615 ip addr show eth0
```

### 6. Entra nel Container e Installa

```bash
pct enter 615

# Installa DAAssist (metodo automatico)
curl -fsSL https://raw.githubusercontent.com/grandir66/DAassist/main/deploy/lxc-install.sh | bash
```

### 7. Accesso all'Applicazione

Dopo l'installazione (circa 5-10 minuti):

```
Frontend: http://<IP_CONTAINER>:5173
Backend:  http://<IP_CONTAINER>:8000
API Docs: http://<IP_CONTAINER>:8000/docs

Credenziali:
  Username: admin
  Password: admin
```

## Installazione con Dominio Personalizzato

Se hai un dominio e vuoi SSL:

```bash
pct enter 615

# Con variabili d'ambiente
DOMAIN=daassist.example.com \
EMAIL=admin@example.com \
ENABLE_SSL=true \
bash <(curl -fsSL https://raw.githubusercontent.com/grandir66/DAassist/main/deploy/lxc-install.sh)
```

Questo configurerà automaticamente:
- Nginx reverse proxy
- Certificato SSL Let's Encrypt
- Redirect HTTP → HTTPS

## Configurazione IP Statico (Opzionale)

Se preferisci IP statico invece di DHCP:

```bash
# Modifica container (da Proxmox host)
pct set 615 -net0 name=eth0,bridge=vmbr0,ip=192.168.1.100/24,gw=192.168.1.1

# Riavvia container
pct restart 615
```

## Gestione Container

```bash
# Avvia container
pct start 615

# Ferma container
pct stop 615

# Riavvia container
pct restart 615

# Entra nel container
pct enter 615

# Visualizza configurazione
pct config 615

# Lista tutti i container
pct list
```

## Verifica Installazione

Una volta completata l'installazione, verifica che i servizi siano attivi:

```bash
pct enter 615

# Verifica servizi Docker
docker compose ps

# Output atteso:
# NAME                IMAGE                     STATUS
# daassist-backend    daassist-backend         Up
# daassist-frontend   daassist-frontend        Up
# daassist-db         postgres:16-alpine       Up

# Visualizza log
docker compose logs -f
```

## Risoluzione Problemi

### Errore "unable to parse volume name"

Se vedi questo errore durante `pct create`:
```
unable to parse zfs volume name 'vztmpl/...'
```

**Soluzione**: Lo storage template (`vztmpl`) deve essere separato dallo storage rootfs.

```bash
# Corretto:
pct create 615 local:vztmpl/ubuntu-22.04-standard_22.04-1_amd64.tar.zst \
  --storage zfs \
  --rootfs zfs:20

# Sbagliato:
pct create 615 zfs:vztmpl/ubuntu-22.04-standard_22.04-1_amd64.tar.zst
```

Il template viene SEMPRE letto da `local:vztmpl/`, ma il rootfs va sullo storage che preferisci.

### Container non si avvia

```bash
# Verifica log
pct status 615
journalctl -xe

# Se problemi con nesting:
pct set 615 -features nesting=1
pct restart 615
```

### Docker non funziona in LXC

Verifica che `nesting=1` sia abilitato:

```bash
pct config 615 | grep nesting

# Se non presente:
pct set 615 -features nesting=1
pct restart 615
```

### Non riesco a connettermi via IP

```bash
# Verifica IP container
pct exec 615 ip addr

# Verifica firewall
pct exec 615 ufw status

# Se necessario, disabilita temporaneamente
pct exec 615 ufw disable
```

## Configurazioni Avanzate

### Container con più RAM/CPU

```bash
# Modifica risorse
pct set 615 -memory 8192 -cores 4

# Riavvia per applicare
pct restart 615
```

### Backup Container

```bash
# Backup completo container (da Proxmox host)
vzdump 615 --compress zstd --mode snapshot

# I backup vengono salvati in /var/lib/vz/dump/
```

### Clone Container

```bash
# Clona container (ID destinazione 616)
pct clone 615 616 --hostname daassist-test
```

## Next Steps

Dopo l'installazione:

1. ✅ Accedi all'applicazione
2. ✅ Cambia password admin (importante!)
3. ✅ Configura dati iniziali (clienti, tecnici)
4. ✅ Testa creazione ticket e interventi
5. ✅ Configura backup automatici (già attivi)

## Monitoraggio Risorse

```bash
# Visualizza utilizzo risorse del container
pct exec 615 docker stats

# O da Proxmox web UI:
# Datacenter → <node> → Container 615 → Summary
```

## Supporto

Per problemi:
- GitHub Issues: https://github.com/grandir66/DAassist/issues
- Documentazione completa: `/deploy/PROXMOX_GUIDE.md`
