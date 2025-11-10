# 🔒 Workflow Git - Protection de `main`

## Règles de Protection

La branche `main` est **protégée** et ne peut pas recevoir de push direct.

### ✅ Workflow Obligatoire

1. **Créer une branche de feature**
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feat/nom-de-votre-feature
   ```

2. **Développer et commiter**
   ```bash
   git add .
   git commit -m "feat: description de votre feature"
   ```

3. **Pousser votre branche**
   ```bash
   git push origin feat/nom-de-votre-feature
   ```

4. **Créer une Pull Request**
   - Aller sur GitHub
   - Créer une PR de `feat/nom-de-votre-feature` → `develop`
   - Demander une review
   - Attendre l'approbation

5. **Merge vers `main`**
   - Seul un mainteneur peut merger `develop` → `main`
   - Via une PR avec review obligatoire

## 🌳 Structure des Branches

```
main (production, protégée)
  ↑
develop (intégration, semi-protégée)
  ↑
feat/*, fix/*, docs/* (branches de travail)
```

## 📝 Convention de Nommage

### Branches
- `feat/nom-feature` - Nouvelles fonctionnalités
- `fix/nom-bug` - Corrections de bugs
- `docs/nom-doc` - Documentation
- `refactor/nom` - Refactoring
- `test/nom` - Ajout de tests

### Commits (Convention Conventional Commits)
- `feat:` - Nouvelle fonctionnalité
- `fix:` - Correction de bug
- `docs:` - Documentation
- `style:` - Formatage, pas de changement de code
- `refactor:` - Refactoring
- `test:` - Ajout de tests
- `chore:` - Maintenance

**Exemples :**
```bash
git commit -m "feat: ajout du modèle d'analyse d'images"
git commit -m "fix: correction du bug de prédiction batch"
git commit -m "docs: mise à jour du README avec les nouvelles features"
```

## ⚠️ Interdictions

❌ **JAMAIS** de push direct sur `main`
```bash
# ❌ INTERDIT
git push origin main
```

❌ **JAMAIS** de force push
```bash
# ❌ INTERDIT
git push --force
```

❌ **JAMAIS** de merge sans review
```bash
# ❌ INTERDIT
git checkout main
git merge develop
```

## 🚀 Workflow Complet - Exemple

### Ajouter un nouveau modèle

```bash
# 1. Partir de develop
git checkout develop
git pull origin develop

# 2. Créer votre branche
git checkout -b feat/mon-nouveau-modele

# 3. Développer
# ... créer app/services/mon_modele/
# ... implémenter le modèle

# 4. Commiter régulièrement
git add app/services/mon_modele/
git commit -m "feat: ajout du modèle de détection XYZ"

git add tests/test_mon_modele.py
git commit -m "test: ajout des tests pour le modèle XYZ"

git add docs/ADD_YOUR_MODEL.md
git commit -m "docs: mise à jour du guide avec le modèle XYZ"

# 5. Pousser
git push origin feat/mon-nouveau-modele

# 6. Créer une PR sur GitHub
# feat/mon-nouveau-modele → develop

# 7. Après review et merge, supprimer la branche locale
git checkout develop
git pull origin develop
git branch -d feat/mon-nouveau-modele
```

## 🔍 Vérifier l'état

```bash
# Voir les branches
git branch -a

# Voir l'historique
git log --oneline --graph --all

# Voir les différences
git diff develop
```

## 🆘 En Cas de Problème

### J'ai commité sur `main` par erreur

```bash
# 1. Créer une branche avec vos changements
git branch feat/mes-changements

# 2. Revenir à l'état précédent de main
git reset --hard origin/main

# 3. Aller sur votre branche
git checkout feat/mes-changements

# 4. Pousser et créer une PR
git push origin feat/mes-changements
```

### Conflit lors du merge

```bash
# 1. Mettre à jour develop
git checkout develop
git pull origin develop

# 2. Rebaser votre branche
git checkout feat/ma-feature
git rebase develop

# 3. Résoudre les conflits
# ... éditer les fichiers en conflit

# 4. Continuer le rebase
git add .
git rebase --continue

# 5. Force push (uniquement sur votre branche de feature)
git push origin feat/ma-feature --force
```

## 👥 Rôles et Responsabilités

### Développeurs
- Créer des branches de feature
- Commiter régulièrement
- Créer des PR vers `develop`
- Répondre aux commentaires de review

### Reviewers
- Vérifier le code
- Tester les fonctionnalités
- Approuver ou demander des changements

### Mainteneurs
- Merger les PR vers `develop`
- Créer les releases de `develop` vers `main`
- Gérer les conflits complexes

## 📚 Ressources

- [Git Flow](https://nvie.com/posts/a-successful-git-branching-model/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [GitHub Flow](https://guides.github.com/introduction/flow/)

---

**Dernière mise à jour** : Janvier 2025
