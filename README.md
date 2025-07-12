# 🧠 Analyseur de Performance des Jobs

Une application web complète pour analyser les performances des jobs/tâches planifiées avec interface intuitive et génération de rapports automatisés.

## 📋 Table des Matières

- [Fonctionnalités](#-fonctionnalités)
- [Architecture](#-architecture)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Utilisation](#-utilisation)
- [API Endpoints](#-api-endpoints)
- [Structure de la Base de Données](#-structure-de-la-base-de-données)
- [Génération de Rapports](#-génération-de-rapports)
- [Envoi d'Emails](#-envoi-demails)
- [Troubleshooting](#-troubleshooting)

## 🚀 Fonctionnalités

### Connexion et Analyse de Données
- ✅ Connexion sécurisée à MySQL
- ✅ Sélection de période personnalisée
- ✅ Navigation hiérarchique des jobs
- ✅ Calcul automatique des statistiques de performance
- ✅ Visualisation graphique interactive avec Plotly.js

### Statistiques Avancées
- 📊 Durée moyenne d'exécution
- 📈 Durée maximum et minimum
- 📉 Nombre total d'exécutions
- 📋 Analyse par période et par job

### Génération de Rapports
- 📄 Export PDF pour un job spécifique
- 📁 Export PDF pour tous les jobs
- 📧 Envoi automatique par email
- 📊 Graphiques et statistiques détaillées

### Interface Utilisateur
- 🎨 Interface moderne et responsive
- 🧭 Navigation par breadcrumb
- 📱 Compatible mobile et desktop
- 🎯 Visualisations interactives

## 🏗️ Architecture

```
┌─────────────────┐    HTTP/JSON    ┌─────────────────┐    PyMySQL    ┌─────────────────┐
│                 │   ◄──────────►  │                 │  ◄─────────►  │                 │
│  Frontend HTML  │                 │  Backend Flask  │               │  MySQL Database │
│  + JavaScript   │                 │  + Python APIs │               │                 │
│                 │                 │                 │               │                 │
└─────────────────┘                 └─────────────────┘               └─────────────────┘
```

### Technologies Utilisées

**Frontend:**
- HTML5 / CSS3 / JavaScript (ES6+)
- Plotly.js pour les graphiques interactifs
- CSS Grid/Flexbox pour le responsive design

**Backend:**
- Python 3.7+
- Flask (API REST)
- PyMySQL (connexion MySQL)
- Pandas (traitement des données)
- Matplotlib + Seaborn (génération PDF)
- SMTP (envoi d'emails)

## 🛠️ Installation

### Prérequis
- Python 3.7+
- MySQL Server
- Navigateur web moderne

### 1. Cloner le Projet
```bash
git clone <votre-repo>
cd performance-analyzer
```

### 2. Installer les Dépendances Python
```bash
pip install flask flask-cors pymysql pandas matplotlib seaborn
```

### 3. Lancer le Serveur Backend
```bash
python flask_backend_server.py
```

### 4. Ouvrir l'Interface Web
Ouvrez `index.html` dans votre navigateur ou servez-le via un serveur HTTP local.

## ⚙️ Configuration

### Configuration Email
Modifiez les constantes dans `flask_backend_server.py` :

```python
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = "votre-email@gmail.com"
EMAIL_PASSWORD = "votre-mot-de-passe-app"  # Mot de passe d'application Gmail
```

### Configuration MySQL
L'application se connecte à MySQL avec les paramètres configurables via l'interface :
- **Host** : localhost (par défaut)
- **User** : root (par défaut)
- **Password** : azerty (par défaut)
- **Database** : scheduler_test (par défaut)
- **Port** : 3306

## 📖 Utilisation

### 1. Connexion à la Base de Données
1. Remplissez les paramètres MySQL dans l'interface
2. Sélectionnez la période d'analyse (dates de début et fin)
3. Cliquez sur "🔄 Charger les données"

### 2. Navigation des Jobs
- Utilisez la navigation hiérarchique pour explorer les jobs
- Cliquez sur les dossiers pour naviguer
- Utilisez le breadcrumb pour revenir en arrière

### 3. Analyse des Performances
- Cliquez sur un job pour voir son analyse détaillée
- Consultez les statistiques : moyenne, max, min, total
- Analysez le graphique d'évolution temporelle

### 4. Export et Partage
- **PDF Job** : Exporte l'analyse du job sélectionné
- **PDF Complet** : Exporte l'analyse de tous les jobs
- **Email** : Envoie le rapport par email automatiquement

## 🔗 API Endpoints

### POST `/api/connect`
Connexion à MySQL et récupération des données.

**Paramètres :**
```json
{
  "host": "localhost",
  "user": "root", 
  "password": "azerty",
  "database": "scheduler_test",
  "port": 3306,
  "startDate": "2025-05-01",
  "endDate": "2025-05-31"
}
```

### GET `/api/test`
Test de connexion au serveur Flask.

### POST `/api/generate-pdf`
Génération de rapports PDF.

**Paramètres :**
```json
{
  "type": "single|all",
  "jobName": "nom_du_job",
  "jobData": [...],
  "allJobsData": [...]
}
```

### POST `/api/send-email`
Envoi d'emails avec rapports PDF.

**Paramètres :**
```json
{
  "type": "single|all",
  "email": "destinataire@email.com",
  "subject": "Objet du message",
  "message": "Corps du message",
  "jobName": "nom_du_job",
  "jobData": [...],
  "allJobsData": [...]
}
```

## 🗄️ Structure de la Base de Données

### Table `stg_scheduler_history`
```sql
CREATE TABLE stg_scheduler_history (
  JOB_NAME VARCHAR(255) NOT NULL,
  START_TIME DATETIME NOT NULL,
  END_TIME DATETIME,
  -- autres colonnes...
);
```

**Colonnes requises :**
- `JOB_NAME` : Nom du job (format hiérarchique avec `/`)
- `START_TIME` : Date/heure de début d'exécution
- `END_TIME` : Date/heure de fin d'exécution

## 📊 Génération de Rapports

### Rapports PDF
Les rapports PDF incluent :
- **Page de statistiques** : Résumé des performances
- **Graphiques** : Évolution temporelle des durées
- **Détails** : Analyse par jour et par job

### Contenu des Rapports
- Durée moyenne, maximum, minimum
- Nombre total d'exécutions
- Période d'analyse
- Graphiques de tendance
- Lignes de référence (moyenne, max, min)

## 📧 Envoi d'Emails

### Configuration Gmail
1. Activez la validation en 2 étapes
2. Générez un mot de passe d'application
3. Utilisez ce mot de passe dans `EMAIL_PASSWORD`

### Fonctionnalités Email
- Envoi automatique de rapports PDF
- Personnalisation du sujet et du message
- Validation des adresses email
- Gestion des erreurs d'envoi

## 🔧 Troubleshooting

### Problèmes de Connexion MySQL
```
❌ Erreur de connexion MySQL: (2003, "Can't connect to MySQL server")
```
**Solutions :**
- Vérifiez que MySQL est démarré
- Contrôlez les paramètres de connexion
- Vérifiez les permissions utilisateur

### Problèmes d'Email
```
❌ Erreur lors de l'envoi: Authentication failed
```
**Solutions :**
- Vérifiez le mot de passe d'application Gmail
- Contrôlez les paramètres SMTP
- Vérifiez la validation en 2 étapes

### Serveur Flask Inaccessible
```
⚠️ Serveur Flask non détecté
```
**Solutions :**
- Vérifiez que le serveur Flask est démarré
- Contrôlez l'URL `http://localhost:5000`
- Vérifiez les logs du serveur Flask

### Problèmes de Génération PDF
```
❌ Erreur lors de la génération du PDF
```
**Solutions :**
- Vérifiez les dépendances matplotlib
- Contrôlez les permissions d'écriture
- Vérifiez l'espace disque disponible

## 📝 Logs et Debug

### Logs du Serveur Flask
```bash
python flask_backend_server.py
```
Les logs affichent :
- Connexions MySQL
- Requêtes SQL exécutées
- Erreurs de traitement
- Génération de fichiers

### Mode Debug
Pour activer le mode debug :
```python
app.run(debug=True, host='0.0.0.0', port=5000)
```

## 🔄 Évolutions Futures

### Fonctionnalités Prévues
- [ ] Authentification utilisateur
- [ ] Sauvegarde des configurations
- [ ] Alertes automatiques
- [ ] Export Excel
- [ ] API REST complète
- [ ] Dashboard temps réel

### Améliorations Techniques
- [ ] Cache Redis pour les performances
- [ ] Base de données de configuration
- [ ] Tests unitaires
- [ ] Conteneurisation Docker
- [ ] Monitoring et logs structurés

## 👥 Contribution

Pour contribuer au projet :
1. Forkez le repository
2. Créez une branche feature
3. Commitez vos modifications
4. Ouvrez une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 📞 Support

Pour toute question ou support :
- Créez une issue sur GitHub
- Contactez l'équipe de développement
- Consultez la documentation technique

---

**Développé avec ❤️ pour l'analyse de performance des jobs**