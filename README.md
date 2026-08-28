<div align="center">

# 🛒 Price Comparator (Jumia vs Expat Dakar)

**Plateforme web d'extraction, d'agrégation et de comparaison de prix e-commerce au Sénégal.**

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-5.0-646CFF?style=for-the-badge&logo=vite&logoColor=white)](https://vitejs.dev/)
[![License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE)

</div>

---

## 📌 À propos du projet

**Price Comparator** est un outil conçu pour automatiser la recherche et la veille tarifaire en ligne. L'application extrait dynamiquement les offres de produits depuis **Jumia Sénégal** et **Expat Dakar**, agrège les données via une API REST sous **FastAPI**, et présente les résultats comparatifs côte à côte sur une interface réactive développée en **React**.

---

## ✨ Fonctionnalités Principales

- 🔍 **Scraping Multi-Sources :** Extraction automatique des titres, prix, images et URLs directes depuis Jumia et Expat Dakar.
- ⚡ **API REST Performante :** Backend sous FastAPI avec typage strict (Pydantic) et validation des données.
- ⚛️ **Interface React Dynamique :** Comparaison instantanée, tri par prix et filtrage par plateforme.
- 💾 **Stockage & Cache :** Sauvegarde des recherches dans une base de données pour optimiser les performances des requêtes fréquentes.
- 🏗️ **Architecture Modulaire :** Structuration propre séparant l'extraction (scrapers), le service web (API) et la vue (frontend).

---

## 📂 Architecture du Projet

```text
price_comparator/
├── backend/                  # 🐍 Backend Python (API REST & Web Scraping)
│   ├── app/
│   │   ├── api/              # Endpoints & Routes FastAPI
│   │   ├── scrapers/         # Scripts de scraping (Jumia, ExpatDakar)
│   │   ├── models/           # Modèles de base de données (SQLAlchemy)
│   │   └── main.py           # Point d'entrée de l'application FastAPI
│   ├── requirements.txt      # Dépendances Python
│   └── .env.example          # Variables d'environnement
│
├── frontend/                 # ⚛️ Application Frontend React
│   ├── src/
│   │   ├── components/       # Composants réutilisables (SearchBar, ProductCard, etc.)
│   │   ├── services/         # Appels API (Axios / Fetch)
│   │   ├── App.jsx           # Composant racine
│   │   └── main.jsx          # Point d'entrée React
│   ├── package.json          # Dépendances JavaScript
│   └── vite.config.js        # Configuration Vite
│
└── README.md