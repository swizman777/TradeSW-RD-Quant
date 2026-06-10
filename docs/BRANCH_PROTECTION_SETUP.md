# Branch Protection Setup — TradeSW-RD-Quant

Étape Phase 0.5 manuelle pour Chef (interface GitHub web), à exécuter UNE FOIS.

## 1. Activer branch protection sur `main`

URL : `https://github.com/swizman777/TradeSW-RD-Quant/settings/branches`

Cliquer **Add rule** (ou éditer la règle existante sur `main`).

### Branch name pattern
```
main
```

### Cocher les options suivantes
- [x] **Require a pull request before merging**
  - [x] Require approvals : **1**
  - [x] Dismiss stale pull request approvals when new commits are pushed
  - [x] Require review from Code Owners
- [x] **Require status checks to pass before merging**
  - [x] Require branches to be up to date before merging
  - Status checks required :
    - `scope-check (ubuntu-latest)`
    - `scope-check (windows-latest)`
- [x] **Require signed commits**
- [x] **Require linear history** (no merge commits)
- [x] **Do not allow bypassing the above settings**
- [x] **Restrict who can push to matching branches** : add user `swizman777` only
- [x] **Allow force pushes** : ❌ **Disabled**
- [x] **Allow deletions** : ❌ **Disabled**

## 2. Vérifier CODEOWNERS

Le fichier `.github/CODEOWNERS` doit pointer Chef `@swizman777` sur :
- `MANDATE_ECONOPHYSIQUE.md`
- `.github/`
- `scripts/hooks/`
- `config/mandate_scope.yml`
- `archive/hooks_legacy/`

Si une PR touche ces paths, la PR ne pourra pas merger sans review explicite de `@swizman777`.

## 3. Vérifier secrets GitHub (pour signed commits)

URL : `https://github.com/swizman777/TradeSW-RD-Quant/settings/keys`

Le Chef doit avoir ajouté sa clé GPG ou Sigstore signing-key dans son profil GitHub.
Sans cela, "Require signed commits" bloquera toutes les PRs (y compris les siennes).

## 4. Tester la protection

1. Créer une branche feature `test/scope-violation`
2. Commit un fichier hors scope : `touch src/broker/t212_test.py && git commit -m test`
3. Push : la CI `Mandate Scope Guard` doit FAIL
4. Ouvrir une PR : merge bloqué par status check
5. Cleanup : `git push origin --delete test/scope-violation`

## 5. Notes traçabilité

- Toute modification ultérieure de la protection doit être tracée dans `effort_log.md`.
- En cas d'urgence, le Chef peut temporairement désactiver "Restrict who can push", mais doit :
  - notifier T1 Claude + T2 Codex,
  - documenter dans `effort_log.md`,
  - réactiver dans les 24h.
