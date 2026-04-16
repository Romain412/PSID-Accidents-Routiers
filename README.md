<div align="center">
 
```
█████╗  ██████╗ ██████╗██╗██████╗ ███████╗███╗   ██╗████████╗███████╗
██╔══██╗██╔════╝██╔════╝██║██╔══██╗██╔════╝████╗  ██║╚══██╔══╝██╔════╝
███████║██║     ██║     ██║██║  ██║█████╗  ██╔██╗ ██║   ██║   ███████╗
██╔══██║██║     ██║     ██║██║  ██║██╔══╝  ██║╚██╗██║   ██║   ╚════██║
██║  ██║╚██████╗╚██████╗██║██████╔╝███████╗██║ ╚████║   ██║   ███████║
╚═╝  ╚═╝ ╚═════╝ ╚═════╝╚═╝╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝   ╚══════╝
  R O U T I E R S
```
  
🚗 Accidents Routiers — Dashboard & Dataviz
Projet SI et Données (PSID) — 2025/2026

[![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-5-646CFF?style=flat-square&logo=vite&logoColor=white)](https://vitejs.dev/)
[![Chakra UI](https://img.shields.io/badge/Chakra_UI-3-319795?style=flat-square&logo=chakraui&logoColor=white)](https://chakra-ui.com/)
[![Recharts](https://img.shields.io/badge/Recharts-2-22B5BF?style=flat-square)](https://recharts.org/)
[![License](https://img.shields.io/badge/Licence-Open_Licence_2.0-blue?style=flat-square)](https://www.etalab.gouv.fr/wp-content/uploads/2014/05/Licence_Ouverte.pdf)

Analyse et visualisation des accidents corporels de la circulation routière en France — données ONISR 2024
</div>

## 📖 À propos

Ce projet est réalisé dans le cadre du cours Projet Systèmes d'Information et Données (PSID).
Il s'appuie sur les données officielles du fichier BAAC (Bulletin d'Analyse des Accidents Corporels), publiées par le Ministère de l'Intérieur via data.gouv.fr, couvrant l'ensemble des accidents corporels survenus en France en 2024.

L'objectif est de transformer ces données brutes en visualisations interactives pour répondre à trois grandes questions :
*Qui est le plus à risque ? Quand et où les accidents sont-ils les plus graves ? Quelles conditions aggravent la mortalité ?*

## 🗂️ Structure du projet
 
```
PSID-Accidents-Routiers/
│
├── 📁 front/                        # Application web (React + Vite)
│   ├── public/
│   └── src/
│       ├── assets/
│       ├── components/
│       │   ├── Navbar.jsx
│       │   ├── Footer.jsx
│       │   └── charts/              # Composants graphiques
│       │       ├── GravityDonut.jsx
│       │       ├── AgeBarChart.jsx
│       │       ├── HeatmapHeure.jsx
│       │       └── ...
│       ├── pages/
│       │   ├── Home.jsx             # Page d'accueil
│       │   └── Dashboard.jsx        # Dashboard principal
│       ├── data/                    # CSV parsés / JSON précalculés
│       ├── App.jsx
│       └── main.jsx
│
├── 📁 back/                         # Backend (Partie 2 du projet)
│
└── README.md
```

## 📊 Dataset

Les données proviennent du fichier national BAAC — Année 2024, composé de 4 fichiers CSV reliés par `Num_Acc` :

| Fichier | Contenu principal |
| :--- | :--- |
| `caracteristiques_2024.csv` | Date, heure, conditions météo, luminosité, département |
| `lieux_2024.csv` | Type de route, vitesse max, état de surface, tracé |
| `vehicules_2024.csv` | Catégorie de véhicule, manœuvre, obstacle heurté |
| `usagers_2024.csv` | Gravité, âge, sexe, type d'usager, trajet |

*Source : data.gouv.fr — Ministère de l'Intérieur — Licence Ouverte 2.0*

## 📈 Axes d'analyse

- **Axe 1 — Profil des victimes :** Gravité, pyramide des âges, répartition par sexe.
- **Axe 2 — Temporalité & Géographie :** Évolution mensuelle, Heatmap horaire, cartographie par département.
- **Axe 3 — Facteurs aggravants :** Luminosité, météo, type de route et infrastructures.

## 🛠️ Stack technique

| Couche | Technologie |
| :--- | :--- |
| **Frontend** | React 18, Vite, Chakra UI |
| **Graphiques** | Recharts / D3.js |
| **Backend** | Django 5, Django Rest Framework (DRF) |
| **Base de données** | PostgreSQL (ou SQLite en dev) |
| **Parsing Data** | Pandas (Python) / PapaParse (JS) |

## 🚀 Installation & lancement

1. Cloner le projet
```bash
git clone [https://github.com/Romain412/PSID-Accidents-Routiers.git](https://github.com/Romain412/PSID-Accidents-Routiers.git)
cd PSID-Accidents-Routiers
```

### Lancer le back-end

#### Windows

```bash
cd backend
python -m venv venv
venv\Scripts\activate

pip install --upgrade pip
pip install -r requirements.txt

python manage.py import_csv
python manage.py migrate
python manage.py runserver
```

#### MacOS :

```bash
cd backend

python3.12 -m venv venv
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

python manage.py import_csv
python manage.py makemigrations
python manage.py migrate
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
