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

# 🚗 Accidents Routiers — Dashboard & Clustering

**Projet SI et Données (PSID) — 2025/2026**

[![React](https://img.shields.io/badge/React-19.2.4-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-8.0.4-646CFF?style=flat-square&logo=vite&logoColor=white)](https://vitejs.dev/)
[![Chakra UI](https://img.shields.io/badge/Chakra_UI-3.34.0-319795?style=flat-square&logo=chakraui&logoColor=white)](https://chakra-ui.com/)
[![Recharts](https://img.shields.io/badge/Recharts-3.8.1-22B5BF?style=flat-square)](https://recharts.org/)
[![Django](https://img.shields.io/badge/Django-5.1.4-092E20?style=flat-square&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.15.2-A30000?style=flat-square&logo=django&logoColor=white)](https://www.django-rest-framework.org/)
[![License](https://img.shields.io/badge/Licence-Open_Licence_2.0-blue?style=flat-square)](https://www.etalab.gouv.fr/wp-content/uploads/2014/05/Licence_Ouverte.pdf)

*Analyse et visualisation des accidents corporels de la circulation routière en France — données ONISR 2024*

🌐 **[Accéder à l'application](https://psid-accidents-routiers-front.onrender.com/)**

</div>

---

## 📖 À propos

Ce projet est réalisé dans le cadre du cours **Projet Systèmes d'Information et Données (PSID)**.

Il s'appuie sur les données officielles du fichier **BAAC (Bulletin d'Analyse des Accidents Corporels)**, publiées par le Ministère de l'Intérieur via [data.gouv.fr](https://www.data.gouv.fr/datasets/bases-de-donnees-annuelles-des-accidents-corporels-de-la-circulation-routiere-annees-de-2005-a-2024), couvrant l'ensemble des accidents corporels survenus en France en **2024**.

L'objectif est de transformer ces données brutes en **visualisations interactives** et en un **système de recommandation basé sur le clustering** pour répondre à trois grandes questions :

> **Qui** est le plus à risque ? **Quand et où** les accidents sont-ils les plus graves ? **Quelles conditions** aggravent la mortalité ?

---

## 🗂️ Structure du projet

```
PSID-Accidents-Routiers/
│
├── 📁 frontend/                          # Application web (React + Vite)
│   ├── public/
│   └── src/
│       ├── assets/
│       ├── components/
│       │   ├── Navbar.jsx
│       │   ├── Footer.jsx
│       │   └── charts/                   # Composants graphiques
│       │       ├── AgeGravityChart.jsx
│       │       ├── VehicleTypeChart.jsx
│       │       ├── HolidayChart.jsx
│       │       └── ...
│       ├── pages/
│       │   ├── Home.jsx                  # Page d'accueil
│       │   ├── Dashboard.jsx             # Dashboard statistiques + carte
│       │   ├── Itineraire.jsx            # Itinéraire, clustering & recommandation
│       │   └── Simulateur.jsx            # Simulateur de risque par conditions
│       ├── App.jsx
│       └── main.jsx
│
├── 📁 backend/                           # API Django REST
│   ├── api/
│   │   ├── models.py                     # Accident, Lieu, Vehicule, Usager, ClusterDepartement
│   │   ├── preprocessing.py              # Pipeline ColumnTransformer (OHE + StandardScaler)
│   │   ├── views.py                      # Endpoints statistiques, itinéraire, simulateur
│   │   ├── urls.py                       # Routage API
│   │   └── management/commands/
│   │       ├── import_csv.py             # Import & mapping des CSV BAAC
│   │       ├── train_clustering.py       # Entraînement K-Means, Bisecting, GMM (k=5)
│   │       ├── compute_risk_profiles.py  # Profils de gravité par cluster × département
│   │       └── compute_cluster_profiles.py # Caractérisation des clusters (mode des features)
│   ├── data/
│   │   ├── accidents_labelled.csv        # Labels de cluster par accident (54 402 lignes)
│   │   ├── departements.geojson          # Contours géographiques des départements
│   │   └── models/                       # Modèles sérialisés (.pkl)
│   ├── core/
│   │   └── urls.py
│   ├── manage.py
│   └── requirements.txt
│
└── README.md
```

---

## 📊 Dataset

Les données proviennent du fichier national **BAAC — Année 2024**, composé de **4 fichiers CSV** reliés par `Num_Acc` :

| Fichier | Contenu principal |
| :--- | :--- |
| `caracteristiques_2024.csv` | Date, heure, conditions météo, luminosité, département |
| `lieux_2024.csv` | Type de route, vitesse max, état de surface, tracé |
| `vehicules_2024.csv` | Catégorie de véhicule, manœuvre, obstacle heurté |
| `usagers_2024.csv` | Gravité, âge, sexe, type d'usager, trajet |

> Source : [data.gouv.fr — Ministère de l'Intérieur](https://www.data.gouv.fr/datasets/bases-de-donnees-annuelles-des-accidents-corporels-de-la-circulation-routiere-annees-de-2005-a-2024) — Licence Ouverte 2.0

Les codes numériques bruts du BAAC sont convertis en libellés lisibles à l'import via la commande `import_csv` (mapping complet des champs `grav`, `sexe`, `catv`, `catr`, `atm`, etc.).

---

## 📈 Axes d'analyse & fonctionnalités

### Axe 1 — Profil des victimes
- 📊 Accidents par **sexe et gravité** — disparités structurelles entre hommes et femmes
- 📊 **Pyramide des âges** par gravité — fréquence vs létalité selon la tranche d'âge

### Axe 2 — Temporalité & Géographie
- 📅 **Accidents par saison** — saisonnalité et effet volume de trafic
- 🗺️ **Carte interactive** des accidents avec clustering et détail au clic

### Axe 3 — Facteurs structurels
- 🚗 **Types de véhicules impliqués** — regroupés en 7 familles

### Axe 4 — Clustering & Recommandation (Machine Learning)
- 🤖 **Pipeline de clustering** : K-Means, Bisecting K-Means et Gaussian Mixture Model (k=5) appliqués sur les conditions d'accident (luminosité, météo, zone, type de voie, vitesse, véhicule)
- 🛣️ **Page Itinéraire** : calcul de trajet (OSRM), intersection spatiale avec les départements (Shapely), affichage des profils de risque par cluster et recommandation globale
- 🧪 **Simulateur de risque** : estimation des probabilités de blessure (indemne / léger / grave / tué) par soft assignment (pondération inverse des distances / predict_proba GMM) selon les conditions choisies

---

## 🛠️ Stack technique

| Couche | Technologie |
| :--- | :--- |
| **Framework JS** | [React 19.2.4](https://react.dev/) + [Vite 8.0.4](https://vitejs.dev/) |
| **UI Components** | [Chakra UI 3.34.0](https://chakra-ui.com/) |
| **Graphiques** | [Recharts 3.8.1](https://recharts.org/) |
| **Carte** | [React Leaflet](https://react-leaflet.js.org/) + react-leaflet-cluster |
| **Routing** | [React Router v7](https://reactrouter.com/) |
| **Backend** | [Django 5.1.4](https://www.djangoproject.com/) + [DRF 3.15.2](https://www.django-rest-framework.org/) |
| **Base de données** | SQLite |
| **Machine Learning** | [scikit-learn 1.5.2](https://scikit-learn.org/) — K-Means, Bisecting K-Means, GMM |
| **SIG / Routage** | [Shapely 2.1](https://shapely.readthedocs.io/) + OSRM + API Adresse (data.gouv.fr) |
| **Import données** | Commande Django `import_csv` + mapping BAAC |
| **Déploiement** | [Render](https://render.com/) |

---

## 🌐 Déploiement

L'application est déployée sur **Render** : [psid-accidents-routiers-front.onrender.com](https://psid-accidents-routiers-front.onrender.com/)

---

## 🚀 Installation & lancement (local)

### Prérequis

- [Node.js](https://nodejs.org/) ≥ 18 et npm ≥ 9
- Python ≥ 3.11
- Git

### 1. Cloner le projet

```bash
git clone https://github.com/Romain412/PSID-Accidents-Routiers.git
cd PSID-Accidents-Routiers
```

### 2. Lancer le backend Django

Des scripts tout-en-un gèrent automatiquement toutes les étapes (venv, dépendances, migrations, import, clustering) et ignorent les étapes déjà effectuées.

#### Windows
```bat
start_backend.bat
```

#### macOS / Linux
```bash
./start_backend.sh
```

L'API sera disponible sur **http://localhost:8000**

> ⚠️ Au premier lancement, `import_csv` et `train_clustering` prennent quelques minutes.

### 3. Lancer le frontend React

```bash
cd frontend
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

## 👥 Équipe

| Membre | Rôle |
| :--- | :--- |
| **Kevin SOARES** | Développement & Data |
| **Romain THOMAS** | Développement & Data |

Projet réalisé dans le cadre du cours **PSID** — Année 2025/2026

---

<div align="center">

Données publiques — [Licence Ouverte / Open Licence 2.0](https://www.etalab.gouv.fr/wp-content/uploads/2014/05/Licence_Ouverte.pdf) · Ministère de l'Intérieur · ONISR

</div>
