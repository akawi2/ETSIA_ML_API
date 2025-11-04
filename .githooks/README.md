# Git Hooks - Protection de `main`

## Installation

Pour activer les hooks Git qui empêchent les push directs sur `main` :

```bash
# Windows (PowerShell)
git config core.hooksPath .githooks

# Linux/Mac
git config core.hooksPath .githooks
chmod +x .githooks/pre-push
```

## Hooks Disponibles

### `pre-push`
Empêche les push directs sur la branche `main`.

Si vous essayez de push sur `main`, vous verrez :
```
🚫 ERREUR: Push direct sur 'main' interdit!

Workflow correct:
  1. Créer une branche: git checkout -b feat/ma-feature
  2. Pousser la branche: git push origin feat/ma-feature
  3. Créer une Pull Request sur GitHub
```

## Désactivation Temporaire

Si vous devez absolument bypass (déconseillé) :

```bash
git push --no-verify origin main
```

⚠️ **Attention** : Cela contourne la protection locale, mais GitHub bloquera quand même si les règles sont configurées.
