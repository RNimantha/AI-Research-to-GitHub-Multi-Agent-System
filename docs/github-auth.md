# GitHub Authentication

The system needs write access to your GitHub repository to publish research reports. This page explains how to set that up safely.

---

## What Kind of Token You Need

You need a **Fine-Grained Personal Access Token**. This is better than a classic token because:

- It only has access to one specific repository (not all your repos)
- You can set exactly which permissions it has
- You can see when it was last used
- If it leaks, the damage is limited to one repo

---

## How to Create One

1. Go to **GitHub.com** → click your profile photo → **Settings**
2. Scroll down to **Developer settings** (bottom of the left sidebar)
3. Click **Personal access tokens** → **Fine-grained tokens**
4. Click **Generate new token**
5. Fill in the details:
   - **Token name:** something like `trend2poc-publisher`
   - **Expiration:** choose a duration (or no expiration for convenience)
   - **Resource owner:** your GitHub account
   - **Repository access:** select **Only selected repositories** → pick your knowledge-base repo
6. Under **Permissions → Repository permissions**, set:
   - **Contents:** Read and write
   - **Metadata:** Read-only (this is required and set automatically)
7. Scroll down and click **Generate token**
8. **Copy the token immediately** — GitHub only shows it once

---

## Where to Put the Token

**Option 1 — Dashboard (recommended)**

Go to Settings → GitHub in the dashboard, paste the token, and click Save. The token is written to your `.env` file automatically.

**Option 2 — Edit `.env` directly**

```bash
GITHUB_TOKEN=github_pat_your_token_here
GITHUB_REPO_OWNER=your-github-username
GITHUB_REPO_NAME=trend2poc-knowledge-base
GITHUB_DEFAULT_BRANCH=main
```

---

## Testing the Connection

The Settings → GitHub page has a **Test connection** button. It:

1. Verifies the token is valid
2. Checks the repo exists and is accessible
3. Does a test write (creates and immediately deletes a small test file) to confirm write permission
4. Returns the repo name, default branch, and whether the token is fine-grained or classic

If the test fails, the error message will tell you exactly what is wrong.

---

## What the Publisher Does With the Token

Every time the system pushes to GitHub:

1. It scans every file for secret patterns before touching GitHub
2. It creates or updates files under `reports/{date}_{topic-slug}/`
3. It uses the token only for the configured repo — it cannot access anything else
4. The GitHub URL of the published folder is saved and shown in the dashboard

---

## Security Rules

**Never commit your token.** The `.env` file is in `.gitignore`. Never paste a real token into any code file, prompt, or documentation.

**Minimum permissions.** The token only needs Contents (read/write) and Metadata (read). Do not grant additional permissions.

**`AUTO_PUSH_TO_GITHUB` defaults to false.** Nothing is pushed to GitHub without your explicit approval click in the dashboard.

---

## For Production (Multiple Users)

A Personal Access Token belongs to one person. For a multi-user product, you should use a **GitHub App** instead.

Benefits of a GitHub App:
- Each user installs the App on their own repos
- The App gets per-installation tokens that expire automatically
- No long-lived personal tokens stored anywhere
- Better audit trail

Setting up a GitHub App is a future phase. For now, a fine-grained PAT is the recommended approach.
