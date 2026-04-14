<div align="center">
 
```
██████╗ ███████╗██╗██████╗      █████╗  ██████╗ ██████╗██╗██████╗ ███████╗███╗   ██╗████████╗███████╗
██╔══██╗██╔════╝██║██╔══██╗    ██╔══██╗██╔════╝██╔════╝██║██╔══██╗██╔════╝████╗  ██║╚══██╔══╝██╔════╝
██████╔╝███████╗██║██║  ██║    ███████║██║     ██║     ██║██║  ██║█████╗  ██╔██╗ ██║   ██║   ███████╗
██╔═══╝ ╚════██║██║██║  ██║    ██╔══██║██║     ██║     ██║██║  ██║██╔══╝  ██║╚██╗██║   ██║   ╚════██║
██║     ███████║██║██████╔╝    ██║  ██║╚██████╗╚██████╗██║██████╔╝███████╗██║ ╚████║   ██║   ███████║
╚═╝     ╚══════╝╚═╝╚═════╝     ╚═╝  ╚═╝ ╚═════╝ ╚═════╝╚═╝╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝   ╚══════╝
                          R O U T I E R S
```
  
🚗 Accidents Routiers — Dashboard & Dataviz
Projet SI et Données (PSID) — 2024/2025

Analyse et visualisation des accidents corporels de la circulation routière en France — données ONISR 2024
</div>

📖 À propos
Ce projet est réalisé dans le cadre du cours Projet Systèmes d'Information et Données (PSID).
Il s'appuie sur les données officielles du fichier BAAC (Bulletin d'Analyse des Accidents Corporels), publiées par le Ministère de l'Intérieur via data.gouv.fr, couvrant l'ensemble des accidents corporels survenus en France en 2024.

L'objectif est de transformer ces données brutes en visualisations interactives pour répondre à trois grandes questions :
*Qui est le plus à risque ? Quand et où les accidents sont-ils les plus graves ? Quelles conditions aggravent la mortalité ?*

🗂️ Structure du projet
PSID-Accidents-Routiers/
│
├── 📁 front/                        # Application web (React + Vite)
│   ├── src/
│   │   ├── components/              # Composants UI et graphiques (Recharts)
│   │   ├── pages/                   # Home et Dashboard
│   │   └── services/                # Appels API vers le backend
│
├── 📁 back/                         # API REST (Django + Django Rest Framework)
│   ├── core/                        # Configuration projet Django
│   ├── accidents/                   # Application principale (Modèles & Vues)
│   ├── data/                        # Scripts d'import et fichiers CSV sources
│   └── manage.py
│
└── README.md

📊 Dataset
Les données proviennent du fichier national BAAC — Année 2024, composé de 4 fichiers CSV reliés par `Num_Acc` :

| Fichier | Contenu principal |
| :--- | :--- |
| `caracteristiques_2024.csv` | Date, heure, conditions météo, luminosité, département |
| `lieux_2024.csv` | Type de route, vitesse max, état de surface, tracé |
| `vehicules_2024.csv` | Catégorie de véhicule, manœuvre, obstacle heurté |
| `usagers_2024.csv` | Gravité, âge, sexe, type d'usager, trajet |

*Source : data.gouv.fr — Ministère de l'Intérieur — Licence Ouverte 2.0*

📈 Axes d'analyse
- **Axe 1 — Profil des victimes :** Gravité, pyramide des âges, répartition par sexe.
- **Axe 2 — Temporalité & Géographie :** Évolution mensuelle, Heatmap horaire, cartographie par département.
- **Axe 3 — Facteurs aggravants :** Luminosité, météo, type de route et infrastructures.

🛠️ Stack technique
| Couche | Technologie |
| :--- | :--- |
| **Frontend** | React 18, Vite, Chakra UI |
| **Graphiques** | Recharts / D3.js |
| **Backend** | Django 5, Django Rest Framework (DRF) |
| **Base de données** | PostgreSQL (ou SQLite en dev) |
| **Parsing Data** | Pandas (Python) / PapaParse (JS) |

🚀 Installation & lancement

1. Cloner le projet
```bash
git clone [https://github.com/Romain412/PSID-Accidents-Routiers.git](https://github.com/Romain412/PSID-Accidents-Routiers.git)
cd PSID-Accidents-Routiers
```

### Lancer le back-end

```bash
cd back
python -m venv venv
source venv/bin/activate  # (ou venv\Scripts\activate sur Windows)
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

L'API sera disponible sur http://localhost:8000

### Lancer le front-end

```bash
cd front
npm install
npm run dev
```

L'application sera disponible sur **http://localhost:5173**

### Build de production

```bash
npm run build
npm run preview
```

---

## 📦 Livrables

- [ ] Rapport écrit
- [ ] Vidéo de présentation
- [ ] Slides PPTX
- [ ] Archive du code front-end
- [ ] 🔗 Lien vers la solution web déployée

---

## 👥 Équipe

> Projet réalisé dans le cadre du cours **PSID** — Année 2025/2026

---

<div align="center">

Données publiques — [Licence Ouverte / Open Licence 2.0](https://www.etalab.gouv.fr/wp-content/uploads/2014/05/Licence_Ouverte.pdf) · Ministère de l'Intérieur · ONISR

</div>
