# NAS_TP - Network Automation System

## Vue d'ensemble

**NAS_TP** est un système d'automatisation de réseau qui génère et configure automatiquement des réseaux MPLS/VPN complexes dans l'émulateur GNS3. Le projet extrait la topologie réseau d'un projet GNS3, applique une stratégie de conception complète (adressage IP, protocoles de routage, VRF/BGP multi-client), génère les configurations des routeurs et les injecte automatiquement dans le simulateur.

## Objectifs

- **Automatiser** la configuration de réseaux MPLS/VPN multi-clients
- **Générer** les configurations Cisco IOS à partir d'une topologie GNS3
- **Supporter** des scénarios de VPN client avec isolation via VRF et route targets
- **Éliminer** les configurations manuelles répétitives

## Architecture globale

```
┌─────────────────────────────────────────────────────────┐
│          GNS3 Project File (NAS_TP1.gns3)               │
│         [Topologie avec nodes et links]                  │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│        Automation Pipeline (automation/main.py)          │
│                                                          │
│  1. Extract Topology  ──────► topology.json             │
│  2. IPv4 Planning     ──────► Assign addresses          │
│  3. Map Clients       ──────► Assign VPN customers      │
│  4. OSPF Protocol     ──────► Core IGP routing          │
│  5. MPLS Setup        ──────► Label switching           │
│  6. VRF Config        ──────► Customer isolation        │
│  7. BGP CE-PE         ──────► Customer access peering   │
│  8. MP-BGP PE-PE      ──────► Inter-PE routing          │
│  9. Render Configs    ──────► Generate .cfg files       │
│ 10. Inject Configs    ──────► Deploy to GNS3            │
└─────────────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│        GNS3 Dynamips Routers                             │
│     [Routers configured automatiquement]                 │
└─────────────────────────────────────────────────────────┘
```

## Structure du projet

```
NAS_PROJECT-main/
├── NAS_TP1.gns3                    # Projet GNS3
├── automation/                      # Pipeline d'automatisation
│   ├── main.py                      # Point d'entrée principal
│   ├── utils.py                     # Utilitaires partagés
│   ├── addressing/                  # Planification IP
│   ├── configs/                     # Configurations générées
│   ├── data/                        # Données d'entrée/sortie
│   ├── inject/                      # Injection dans GNS3
│   ├── protocols/                   # Configuration des protocoles
│   ├── rendering/                   # Génération de configurations
│   ├── templates/                   # Templates Jinja2
│   └── topology/                    # Extraction de topologie
└── project-files/                   # Fichiers GNS3
    └── dynamips/                    # Disques et logs des routeurs
```

## Utilisation

### Prérequis
- GNS3 avec Dynamips
- Python 3.x
- Jinja2 (pour les templates)

### Exécution

```bash
cd automation
python main.py
```

Le script exécutera automatiquement les 10 étapes de configuration et injectera les configurations dans GNS3.

##Conception réseau

### Architecture MPLS/VPN

Le système configure une architecture **MPLS/VPN multi-client** typique :

- **Core Network (P & PE routers)**
  - OSPF pour le routage IGP interne
  - MPLS/LDP pour le switching de labels
  - ASN 65000

- **Customer Networks (CE routers)**
  - ASN 65001+ (un par client)
  - Peering eBGP vers PE

- **Inter-PE Routing (MP-BGP)**
  - VPNv4 iBGP entre tous les PE
  - Route targets pour isolation des clients
  - Support de multiples VRFs

### Adressage

- **Loopbacks** : 1.0.0.0/8 (séquentiels)
- **Links P-P/PE** : 10.0.0.0/16 en subnets /30
- **Links CE** : Utilisent la topologie GNS3

### Classification des routeurs

| Type | Rôle |
|------|------|
| **P** | Provider - routeur core sans client |
| **PE** | Provider Edge - connexion clients |
| **CE** | Customer Edge - accès client |

## Flux de données

1. **Topology Extraction** → Analyse GNS3, détecte topologie et types de routeurs
2. **IP Planning** → Assigne adresses loopback et subnets /30
3. **Client Mapping** → Associe CEs à des clients (VPNs)
4. **Protocol Configuration** → Calcule configurations OSPF, MPLS, VRF, BGP
5. **Rendering** → Utilise Jinja2 pour générer configs Cisco IOS
6. **Injection** → Copie configs dans répertoires Dynamips de GNS3

## Fichiers de données

### Inputs
- **topology.json** : Topologie extraite de GNS3 (auto-généré)
- **clients_map.json** : Mapping CE → Client/VPN

### Outputs
- **configs/*.cfg** : Fichiers de configuration Cisco IOS générés
- **project-files/dynamips/[uuid]/** : Configs injectées dans GNS3

## Détails techniques

### Protocoles supportés

| Protocole | Utilisation |
|-----------|------------|
| **OSPF** | IGP pour le réseau core |
| **MPLS/LDP** | Label switching sur core |
| **BGP eBGP** | Peering clients ↔ PE |
| **BGP MP-BGP** | Peering PE ↔ PE (vpnv4) |
| **VRF** | Isolation client |

### Template Jinja2

Le template [router_ios.j2](automation/templates/router_ios.j2) génère les configurations complètes avec :
- Interfaces et adressage
- OSPF
- MPLS
- VRF et route targets
- BGP

## Documentation additionnelle

Pour plus de détails sur l'architecture du dossier automation, voir [ARCHITECTURE.md](ARCHITECTURE.md).
