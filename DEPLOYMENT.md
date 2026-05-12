# 🚀 CI/CD Deployment Guide

## Overview

Your XAU/USD Trading System now has **automated CI/CD** via GitHub Actions. Every push to `main` branch will:

1. ✅ Type-check TypeScript
2. ✅ Run 18+ unit tests
3. ✅ Build production bundle
4. ✅ Deploy to your server (configured)

---

## 📋 Pipeline Stages

```
Push to GitHub
    │
    ├──► Lint & Type Check (TypeScript compilation)
    │
    ├──► Python Tests (pytest)
    │
    ├──► JavaScript Tests (Jest - 18 tests)
    │
    ├──► Build (Compile TypeScript → dist/)
    │
    └──► Deploy (SCP/FTP/GitHub Pages)
```

---

## 🔧 Configuration

### Step 1: Add GitHub Secrets

Go to **GitHub Repo → Settings → Secrets and variables → Actions**

Add these secrets based on your deployment method:

#### Option A: SSH/SCP Deployment (Recommended for VPS)
```
SSH_PRIVATE_KEY    =  -----BEGIN OPENSSH PRIVATE KEY-----
                       (Your server private key)
                       -----END OPENSSH PRIVATE KEY-----

SERVER_IP          =  203.0.113.45  (Your server IP)
SERVER_USER        =  deploy        (SSH username)
```

#### Option B: FTP Deployment (Shared Hosting)
```
FTP_SERVER         =  ftp.yourhost.com
FTP_USERNAME       =  your_username
FTP_PASSWORD       =  your_password
```

#### Option C: GitHub Pages (Free, Static Only)
No secrets needed! Just enable Pages in repo settings.

---

### Step 2: Test Locally

```bash
# Run the same commands as CI
npm run ci

# This runs:
# 1. TypeScript type check
# 2. Jest tests
# 3. Build compilation
```

---

### Step 3: Push to Trigger Deployment

```bash
# Add your changes
git add .

# Commit
git commit -m "feat: add new trading signal"

# Push to main (triggers CI/CD)
git push origin main
```

---

## 📊 Monitoring Deployments

### GitHub Actions Dashboard
- Go to **GitHub Repo → Actions tab**
- See real-time progress of each job
- Green check = Success
- Red X = Failed (click for logs)

### Job Statuses

| Job | Purpose | Duration |
|-----|---------|----------|
| `lint` | TypeScript type checking | ~30s |
| `test-python` | Python module tests | ~45s |
| `test-js` | Jest unit tests (18 tests) | ~60s |
| `build` | Compile TypeScript | ~20s |
| `deploy` | Upload to server | ~30s |
| `security` | npm audit, CodeQL | ~2min |

---

## 🔄 Rollback

If deployment breaks:

```bash
# Revert to previous commit
git revert HEAD

# Push (triggers new deployment with old code)
git push origin main
```

Or manually in GitHub:
1. Go to **Actions tab**
2. Find last successful workflow run
3. Click **Re-run jobs**

---

## 🛠️ Local Development Workflow

```bash
# 1. Make changes to TypeScript
edit src/utils/statistics.ts

# 2. Test locally
npm test

# 3. Type check
npm run typecheck

# 4. Build
npm run build

# 5. Commit & push (triggers full CI/CD)
git add . && git commit -m "feat: improve PnL calculation" && git push

# 6. Monitor at: https://github.com/YOUR_USERNAME/POOCHES/actions
```

---

## 🔐 Security Features

- **No hardcoded credentials** - All secrets in GitHub Secrets
- **SSH key authentication** - No passwords in CI logs
- **npm audit** - Checks for vulnerable dependencies
- **CodeQL analysis** - GitHub's security scanner
- **Artifact retention** - Build logs kept for 90 days

---

## 🚨 Troubleshooting

### "Tests failing"
```bash
# Run locally to debug
npm test
# Fix issues, then push again
```

### "TypeScript errors"
```bash
# Check types locally
npm run typecheck
# Fix errors in .ts files
```

### "Deployment failing"
1. Check GitHub Secrets are set correctly
2. Verify server credentials work manually:
```bash
ssh -i ~/.ssh/deploy_key deploy@YOUR_SERVER_IP
```

### "Build artifacts not found"
Ensure `dist/` is not in `.gitignore` (it shouldn't be)

---

## 📈 Deployment Targets

The pipeline supports **multiple deployment methods** (configured in workflow):

1. **VPS/Cloud Server** (SCP/SSH) - Full control
2. **Shared Hosting** (FTP) - Budget option
3. **GitHub Pages** - Free, fast, but public

**Priority:** SCP → FTP → GitHub Pages (first available method wins)

---

## ✅ Pre-Deployment Checklist

Before your first push:

- [ ] GitHub Secrets configured (SERVER_IP, SSH_PRIVATE_KEY)
- [ ] Tests pass locally (`npm test`)
- [ ] TypeScript compiles (`npm run build`)
- [ ] Server ready to receive files
- [ ] Backup of current production files

---

## 🎯 Next Steps

1. **Configure secrets** (5 minutes)
2. **Test with small change** (push README edit)
3. **Monitor first deployment** (GitHub Actions tab)
4. **Celebrate** 🎉 - You now have professional CI/CD!

---

**Questions?** Check the Actions tab for detailed logs on any failures.
