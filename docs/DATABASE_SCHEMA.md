# Documentation du Schéma de Base de Données - ETSIA ML API

## Vue d'ensemble

Ce document décrit en détail le schéma de base de données PostgreSQL utilisé pour le monitoring et la gestion des métriques de l'API ML ETSIA. La base de données est conçue pour suivre les performances des modèles, détecter les anomalies, et fournir des insights sur l'utilisation du système.

## Extension PostgreSQL

### uuid-ossp
Extension PostgreSQL permettant la génération automatique d'identifiants UUID v4 pour les clés primaires.

---

## Tables Principales

### 1. model_predictions

**Description**: Stocke toutes les prédictions effectuées par les modèles de machine learning.

**Colonnes**:
- `id` (UUID, PK): Identifiant unique de la prédiction
- `created_at` (TIMESTAMP): Date et heure de création de la prédiction
- `model_name` (VARCHAR(100)): Nom du modèle utilisé (ex: "camembert-depression")
- `model_version` (VARCHAR(50)): Version du modèle
- `provider` (VARCHAR(50)): Fournisseur du modèle (huggingface, ollama, etc.)
- `endpoint` (VARCHAR(200)): Endpoint API appelé
- `request_id` (VARCHAR(100)): Identifiant unique de la requête
- `prediction` (VARCHAR(100)): Résultat de la prédiction (DÉPRESSION, NORMAL, etc.)
- `confidence` (DECIMAL(5,4)): Score de confiance entre 0 et 1
- `severity` (VARCHAR(50)): Niveau de sévérité (Aucune, Faible, Moyenne, Élevée, Critique)
- `latency_ms` (DECIMAL(10,2)): Temps de réponse en millisecondes
- `fallback_used` (BOOLEAN): Indique si un modèle de fallback a été utilisé
- `input_length` (INTEGER): Longueur de l'entrée (nombre de tokens/caractères)
- `batch_size` (INTEGER): Taille du batch traité

**Contraintes**:
- `chk_confidence`: Vérifie que la confiance est entre 0 et 1

**Index**:
- `idx_predictions_model`: Sur model_name
- `idx_predictions_created`: Sur created_at
- `idx_predictions_provider`: Sur provider
- `idx_predictions_endpoint`: Sur endpoint

**Cas d'usage**:
- Analyse des performances par modèle
- Calcul des métriques de latence
- Suivi des prédictions de dépression
- Audit des requêtes

---

### 2. model_errors

**Description**: Enregistre toutes les erreurs survenues lors de l'exécution des modèles.

**Colonnes**:
- `id` (UUID, PK): Identifiant unique de l'erreur
- `created_at` (TIMESTAMP): Date et heure de l'erreur
- `model_name` (VARCHAR(100)): Nom du modèle en erreur
- `provider` (VARCHAR(50)): Fournisseur du modèle
- `error_type` (VARCHAR(100)): Type d'erreur (timeout, memory, inference, etc.)
- `error_message` (TEXT): Message d'erreur détaillé
- `endpoint` (VARCHAR(200)): Endpoint où l'erreur s'est produite
- `request_id` (VARCHAR(100)): Identifiant de la requête en erreur
- `input_length` (INTEGER): Longueur de l'entrée
- `stack_trace` (TEXT): Trace complète de l'erreur

**Index**:
- `idx_errors_model`: Sur model_name
- `idx_errors_created`: Sur created_at
- `idx_errors_type`: Sur error_type

**Cas d'usage**:
- Debugging des problèmes de modèles
- Calcul du taux d'erreur
- Identification des patterns d'erreurs
- Alertes sur erreurs critiques

---

### 3. model_health_checks

**Description**: Historique des vérifications de santé des modèles.

**Colonnes**:
- `id` (UUID, PK): Identifiant unique du health check
- `checked_at` (TIMESTAMP): Date et heure de la vérification
- `model_name` (VARCHAR(100)): Nom du modèle vérifié
- `provider` (VARCHAR(50)): Fournisseur du modèle
- `status` (VARCHAR(20)): État du modèle (healthy, unhealthy, degraded)
- `latency_ms` (DECIMAL(10,2)): Latence du health check
- `memory_mb` (DECIMAL(10,2)): Mémoire utilisée par le modèle
- `details` (JSONB): Détails additionnels en JSON

**Index**:
- `idx_health_model`: Sur model_name
- `idx_health_checked`: Sur checked_at
- `idx_health_status`: Sur status

**Cas d'usage**:
- Monitoring de la disponibilité des modèles
- Détection de dégradation de performance
- Historique de santé des services
- Alertes sur modèles unhealthy

---

### 4. latency_percentiles

**Description**: Stocke les percentiles de latence agrégés par période pour analyse de performance.

**Colonnes**:
- `id` (UUID, PK): Identifiant unique
- `calculated_at` (TIMESTAMP): Date de calcul des métriques
- `period_start` (TIMESTAMP): Début de la période analysée
- `period_end` (TIMESTAMP): Fin de la période analysée
- `model_name` (VARCHAR(100)): Nom du modèle
- `provider` (VARCHAR(50)): Fournisseur du modèle
- `p50_ms` (DECIMAL(10,2)): Médiane de latence (50e percentile)
- `p95_ms` (DECIMAL(10,2)): 95e percentile de latence
- `p99_ms` (DECIMAL(10,2)): 99e percentile de latence
- `avg_ms` (DECIMAL(10,2)): Latence moyenne
- `min_ms` (DECIMAL(10,2)): Latence minimale
- `max_ms` (DECIMAL(10,2)): Latence maximale
- `total_requests` (INTEGER): Nombre total de requêtes
- `error_count` (INTEGER): Nombre d'erreurs
- `fallback_count` (INTEGER): Nombre de fallbacks utilisés

**Contraintes**:
- UNIQUE sur (period_start, period_end, model_name)

**Index**:
- `idx_percentiles_model`: Sur model_name
- `idx_percentiles_period`: Sur (period_start, period_end)

**Cas d'usage**:
- Analyse de performance historique
- Comparaison de performance entre périodes
- SLA monitoring
- Rapports de performance

---

### 5. throughput_metrics

**Description**: Métriques de débit et de charge des modèles.

**Colonnes**:
- `id` (UUID, PK): Identifiant unique
- `recorded_at` (TIMESTAMP): Date d'enregistrement
- `model_name` (VARCHAR(100)): Nom du modèle
- `provider` (VARCHAR(50)): Fournisseur du modèle
- `requests_per_second` (DECIMAL(10,4)): Requêtes par seconde
- `requests_per_minute` (INTEGER): Requêtes par minute
- `concurrent_requests` (INTEGER): Nombre de requêtes concurrentes
- `window_seconds` (INTEGER): Fenêtre de mesure en secondes (défaut: 60)

**Index**:
- `idx_throughput_model`: Sur model_name
- `idx_throughput_recorded`: Sur recorded_at

**Cas d'usage**:
- Monitoring de la charge système
- Planification de capacité
- Détection de pics de trafic
- Optimisation des ressources

---

### 6. alerts

**Description**: Système d'alertes pour le monitoring des modèles et de l'infrastructure.

**Colonnes**:
- `id` (UUID, PK): Identifiant unique de l'alerte
- `created_at` (TIMESTAMP): Date de création de l'alerte
- `resolved_at` (TIMESTAMP): Date de résolution (NULL si active)
- `alert_type` (VARCHAR(100)): Type d'alerte (latency_high, error_rate_high, etc.)
- `severity` (VARCHAR(20)): Sévérité (info, warning, critical)
- `model_name` (VARCHAR(100)): Modèle concerné (optionnel)
- `provider` (VARCHAR(50)): Fournisseur concerné (optionnel)
- `message` (TEXT): Message descriptif de l'alerte
- `threshold_value` (DECIMAL(10,4)): Valeur seuil déclenchant l'alerte
- `actual_value` (DECIMAL(10,4)): Valeur réelle mesurée
- `status` (VARCHAR(20)): État (active, acknowledged, resolved)
- `acknowledged_by` (VARCHAR(100)): Personne ayant acquitté l'alerte
- `acknowledged_at` (TIMESTAMP): Date d'acquittement

**Index**:
- `idx_alerts_status`: Sur status
- `idx_alerts_severity`: Sur severity
- `idx_alerts_created`: Sur created_at
- `idx_alerts_model`: Sur model_name

**Cas d'usage**:
- Notification des problèmes
- Suivi des incidents
- Escalade des alertes critiques
- Historique des problèmes

---

### 7. api_requests

**Description**: Historique complet de toutes les requêtes API pour analyse et audit.

**Colonnes**:
- `id` (UUID, PK): Identifiant unique de la requête
- `created_at` (TIMESTAMP): Date de la requête
- `endpoint` (VARCHAR(200)): Endpoint appelé
- `method` (VARCHAR(10)): Méthode HTTP (GET, POST, PUT, DELETE)
- `status_code` (INTEGER): Code de statut HTTP
- `response_time_ms` (DECIMAL(10,2)): Temps de réponse en millisecondes
- `user_agent` (TEXT): User agent du client
- `ip_address` (INET): Adresse IP du client
- `request_id` (VARCHAR(100)): Identifiant unique de la requête
- `request_body` (JSONB): Corps de la requête (optionnel, pour debug)
- `response_body` (JSONB): Corps de la réponse (optionnel, pour debug)

**Index**:
- `idx_api_requests_endpoint`: Sur endpoint
- `idx_api_requests_created`: Sur created_at
- `idx_api_requests_status`: Sur status_code
- `idx_api_requests_method`: Sur method

**Cas d'usage**:
- Audit des accès API
- Analyse des patterns d'utilisation
- Debugging des problèmes clients
- Statistiques d'utilisation par endpoint

---

### 8. model_versions

**Description**: Gestion des versions de modèles déployés et leur cycle de vie.

**Colonnes**:
- `id` (UUID, PK): Identifiant unique
- `created_at` (TIMESTAMP): Date de création de l'enregistrement
- `model_name` (VARCHAR(100)): Nom du modèle
- `version` (VARCHAR(50)): Numéro de version
- `provider` (VARCHAR(50)): Fournisseur du modèle
- `description` (TEXT): Description de la version
- `deployed_at` (TIMESTAMP): Date de déploiement
- `deprecated_at` (TIMESTAMP): Date de dépréciation (NULL si active)
- `config` (JSONB): Configuration du modèle en JSON
- `is_active` (BOOLEAN): Indique si la version est active

**Contraintes**:
- UNIQUE sur (model_name, version)

**Index**:
- `idx_model_versions_name`: Sur model_name
- `idx_model_versions_active`: Sur is_active

**Cas d'usage**:
- Gestion du cycle de vie des modèles
- Rollback vers versions précédentes
- Suivi des déploiements
- Configuration des modèles

---

### 9. system_metrics

**Description**: Métriques système pour le monitoring de l'infrastructure (CPU, RAM, disque, réseau).

**Colonnes**:
- `id` (UUID, PK): Identifiant unique
- `recorded_at` (TIMESTAMP): Date d'enregistrement
- `cpu_percent` (DECIMAL(5,2)): Utilisation CPU en pourcentage
- `memory_percent` (DECIMAL(5,2)): Utilisation mémoire en pourcentage
- `memory_used_mb` (DECIMAL(10,2)): Mémoire utilisée en MB
- `memory_available_mb` (DECIMAL(10,2)): Mémoire disponible en MB
- `disk_usage_percent` (DECIMAL(5,2)): Utilisation disque en pourcentage
- `disk_used_gb` (DECIMAL(10,2)): Espace disque utilisé en GB
- `disk_available_gb` (DECIMAL(10,2)): Espace disque disponible en GB
- `network_sent_mb` (DECIMAL(10,2)): Données réseau envoyées en MB
- `network_recv_mb` (DECIMAL(10,2)): Données réseau reçues en MB
- `hostname` (VARCHAR(100)): Nom de l'hôte
- `process_name` (VARCHAR(100)): Nom du processus

**Index**:
- `idx_system_metrics_recorded`: Sur recorded_at
- `idx_system_metrics_hostname`: Sur hostname

**Cas d'usage**:
- Monitoring de l'infrastructure
- Détection de saturation des ressources
- Planification de capacité
- Corrélation avec les performances des modèles

---

### 10. model_feedback

**Description**: Feedback utilisateur sur les prédictions pour améliorer les modèles.

**Colonnes**:
- `id` (UUID, PK): Identifiant unique
- `created_at` (TIMESTAMP): Date du feedback
- `prediction_id` (UUID, FK): Référence à la prédiction évaluée
- `is_correct` (BOOLEAN): Indique si la prédiction était correcte
- `user_rating` (INTEGER): Note de 1 à 5
- `comment` (TEXT): Commentaire de l'utilisateur
- `suggested_prediction` (VARCHAR(100)): Prédiction suggérée par l'utilisateur
- `user_id` (VARCHAR(100)): Identifiant de l'utilisateur
- `session_id` (VARCHAR(100)): Identifiant de session

**Contraintes**:
- CHECK sur user_rating (entre 1 et 5)
- FOREIGN KEY vers model_predictions(id)

**Index**:
- `idx_feedback_prediction`: Sur prediction_id
- `idx_feedback_created`: Sur created_at
- `idx_feedback_correct`: Sur is_correct

**Cas d'usage**:
- Évaluation de la qualité des modèles
- Collecte de données pour réentraînement
- Calcul de l'accuracy réelle
- Amélioration continue

---

### 11. ab_tests

**Description**: Configuration et résultats des tests A/B pour comparer les performances de différents modèles.

**Colonnes**:
- `id` (UUID, PK): Identifiant unique
- `created_at` (TIMESTAMP): Date de création du test
- `test_name` (VARCHAR(100), UNIQUE): Nom unique du test
- `description` (TEXT): Description du test
- `model_a` (VARCHAR(100)): Premier modèle à tester
- `model_b` (VARCHAR(100)): Second modèle à tester
- `traffic_split_percent` (INTEGER): Pourcentage de trafic pour model_a (0-100)
- `start_date` (TIMESTAMP): Date de début du test
- `end_date` (TIMESTAMP): Date de fin du test (NULL si en cours)
- `status` (VARCHAR(20)): État du test (active, paused, completed)
- `results` (JSONB): Résultats du test en JSON

**Contraintes**:
- CHECK sur traffic_split_percent (entre 0 et 100)
- UNIQUE sur test_name

**Index**:
- `idx_ab_tests_status`: Sur status
- `idx_ab_tests_dates`: Sur (start_date, end_date)

**Cas d'usage**:
- Comparaison de modèles en production
- Validation de nouvelles versions
- Optimisation des performances
- Décisions data-driven

---

### 12. model_drift

**Description**: Détection et suivi du drift (dérive) dans les performances des modèles.

**Colonnes**:
- `id` (UUID, PK): Identifiant unique
- `detected_at` (TIMESTAMP): Date de détection du drift
- `model_name` (VARCHAR(100)): Nom du modèle concerné
- `provider` (VARCHAR(50)): Fournisseur du modèle
- `drift_type` (VARCHAR(50)): Type de drift (data_drift, concept_drift, prediction_drift)
- `drift_score` (DECIMAL(5,4)): Score de drift (0-1)
- `baseline_metric` (DECIMAL(10,4)): Métrique de référence
- `current_metric` (DECIMAL(10,4)): Métrique actuelle
- `analysis_start` (TIMESTAMP): Début de la période d'analyse
- `analysis_end` (TIMESTAMP): Fin de la période d'analyse
- `details` (JSONB): Détails additionnels en JSON
- `action_taken` (VARCHAR(100)): Action corrective prise
- `resolved_at` (TIMESTAMP): Date de résolution

**Index**:
- `idx_drift_model`: Sur model_name
- `idx_drift_detected`: Sur detected_at
- `idx_drift_type`: Sur drift_type

**Cas d'usage**:
- Détection de dégradation des modèles
- Déclenchement de réentraînement
- Monitoring de la qualité
- Maintenance prédictive

---

## Vues SQL

### v_model_stats_24h

**Description**: Statistiques agrégées des dernières 24 heures par modèle.

**Colonnes retournées**:
- `model_name`: Nom du modèle
- `provider`: Fournisseur
- `total_requests`: Nombre total de requêtes
- `avg_latency_ms`: Latence moyenne
- `p50_latency_ms`: Médiane de latence
- `p95_latency_ms`: 95e percentile
- `p99_latency_ms`: 99e percentile
- `min_latency_ms`: Latence minimale
- `max_latency_ms`: Latence maximale
- `avg_confidence`: Confiance moyenne
- `fallback_count`: Nombre de fallbacks
- `depression_count`: Nombre de prédictions "DÉPRESSION"
- `normal_count`: Nombre de prédictions "NORMAL"

**Cas d'usage**: Dashboard de monitoring en temps réel

---

### v_error_rates_1h

**Description**: Taux d'erreur par modèle sur la dernière heure.

**Colonnes retournées**:
- `model_name`: Nom du modèle
- `provider`: Fournisseur
- `error_count`: Nombre d'erreurs
- `total_requests`: Nombre total de requêtes
- `error_rate_percent`: Taux d'erreur en pourcentage

**Cas d'usage**: Alertes sur taux d'erreur élevé

---

### v_active_alerts

**Description**: Liste des alertes actives triées par sévérité et date.

**Colonnes retournées**: Toutes les colonnes de la table `alerts`

**Tri**: Par sévérité (critical > warning > info) puis par date décroissante

**Cas d'usage**: Dashboard d'alertes, notifications

---

### v_api_stats_24h

**Description**: Statistiques des requêtes API par endpoint sur 24h.

**Colonnes retournées**:
- `endpoint`: Endpoint API
- `method`: Méthode HTTP
- `total_requests`: Nombre total de requêtes
- `avg_response_time_ms`: Temps de réponse moyen
- `p95_response_time_ms`: 95e percentile du temps de réponse
- `success_count`: Nombre de succès (2xx)
- `error_count`: Nombre d'erreurs (4xx, 5xx)
- `error_rate_percent`: Taux d'erreur en pourcentage

**Cas d'usage**: Monitoring des endpoints, identification des problèmes

---

### v_model_feedback_summary

**Description**: Résumé du feedback utilisateur par modèle.

**Colonnes retournées**:
- `model_name`: Nom du modèle
- `provider`: Fournisseur
- `total_feedback`: Nombre total de feedbacks
- `correct_count`: Nombre de prédictions correctes
- `incorrect_count`: Nombre de prédictions incorrectes
- `avg_rating`: Note moyenne
- `accuracy_percent`: Pourcentage d'accuracy

**Cas d'usage**: Évaluation de la qualité des modèles

---

### v_system_metrics_latest

**Description**: Dernières métriques système par hôte et processus.

**Colonnes retournées**:
- `hostname`: Nom de l'hôte
- `process_name`: Nom du processus
- `recorded_at`: Date d'enregistrement
- `cpu_percent`: Utilisation CPU
- `memory_percent`: Utilisation mémoire
- `memory_used_mb`: Mémoire utilisée
- `disk_usage_percent`: Utilisation disque

**Cas d'usage**: Dashboard système en temps réel

---

## Fonctions PL/pgSQL

### calculate_latency_percentiles()

**Signature**:
```sql
calculate_latency_percentiles(
    p_period_start TIMESTAMP WITH TIME ZONE,
    p_period_end TIMESTAMP WITH TIME ZONE
) RETURNS void
```

**Description**: Calcule et stocke les percentiles de latence pour une période donnée.

**Paramètres**:
- `p_period_start`: Début de la période à analyser
- `p_period_end`: Fin de la période à analyser

**Comportement**:
1. Agrège les données de `model_predictions` pour la période
2. Calcule les percentiles (p50, p95, p99)
3. Calcule les statistiques (avg, min, max)
4. Compte les erreurs et fallbacks
5. Insère ou met à jour dans `latency_percentiles`

**Cas d'usage**:
- Exécution périodique (cron job)
- Génération de rapports
- Analyse historique

**Exemple d'utilisation**:
```sql
-- Calculer les métriques pour la dernière heure
SELECT calculate_latency_percentiles(
    NOW() - INTERVAL '1 hour',
    NOW()
);
```

---

## Données Initiales

### Health Checks Initiaux

Trois enregistrements sont créés dans `model_health_checks` avec le statut "unknown":
- camembert-depression (huggingface)
- qwen-depression (ollama)
- llama-generation (ollama)

### Versions de Modèles Initiales

Trois versions de modèles sont insérées dans `model_versions`:
- camembert-depression v1.0.0
- qwen-depression v1.0.0
- llama-generation v1.0.0

---

## Stratégie d'Indexation

### Index sur les Timestamps
Tous les champs `created_at`, `recorded_at`, `checked_at` sont indexés pour optimiser les requêtes temporelles.

### Index sur les Clés Étrangères
Les colonnes référençant d'autres tables sont indexées (ex: `prediction_id` dans `model_feedback`).

### Index Composites
Des index composites sont créés pour les requêtes fréquentes (ex: `period_start, period_end` dans `latency_percentiles`).

### Index sur les Filtres Fréquents
Les colonnes utilisées dans les clauses WHERE sont indexées (ex: `status`, `severity`, `model_name`).

---

## Bonnes Pratiques d'Utilisation

### 1. Rétention des Données
- Implémenter une politique de purge pour les anciennes données
- Archiver les données historiques si nécessaire
- Utiliser des partitions pour les grandes tables

### 2. Monitoring
- Surveiller la taille des tables
- Analyser les requêtes lentes
- Maintenir les statistiques PostgreSQL à jour

### 3. Sécurité
- Ne pas stocker de données sensibles dans `request_body` et `response_body`
- Anonymiser les adresses IP si nécessaire
- Limiter l'accès aux tables selon les rôles

### 4. Performance
- Exécuter `VACUUM` et `ANALYZE` régulièrement
- Utiliser les vues pour les requêtes complexes fréquentes
- Optimiser les requêtes avec EXPLAIN ANALYZE

---

## Évolutions Futures Possibles

1. **Partitionnement**: Partitionner les grandes tables par date
2. **Matérialized Views**: Créer des vues matérialisées pour les agrégations coûteuses
3. **Time-Series**: Migrer vers TimescaleDB pour les métriques temporelles
4. **Réplication**: Configurer une réplication pour la haute disponibilité
5. **Sharding**: Distribuer les données sur plusieurs serveurs si nécessaire

---

## Diagramme Entité-Association

```
model_predictions (1) ----< (N) model_feedback
       |
       | (référence implicite)
       |
model_errors
model_health_checks
latency_percentiles
throughput_metrics
alerts
api_requests
model_versions
system_metrics
ab_tests
model_drift
```

---

## Conclusion

Ce schéma de base de données fournit une infrastructure complète pour le monitoring, l'analyse et l'amélioration continue des modèles de machine learning. Il permet de:

- Suivre les performances en temps réel
- Détecter et diagnostiquer les problèmes
- Collecter du feedback utilisateur
- Optimiser les modèles via A/B testing
- Maintenir la qualité via la détection de drift
- Auditer toutes les opérations

La structure est extensible et peut être adaptée aux besoins spécifiques du projet ETSIA ML API.
