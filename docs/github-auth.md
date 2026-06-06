# GitHub Authentication

## MVP: Fine-Grained Personal Access Token

1. Go to GitHub → Settings → Developer settings → Personal access tokens → Fine-grained tokens
2. Create new token with:
   - Resource owner: your account
   - Repository access: Only selected repositories → `trend2poc-knowledge-base`
   - Permissions:
     - Contents: Read and Write
     - Metadata: Read
3. Copy the token to `.env` as `GITHUB_TOKEN`

## Production: GitHub App

For multi-user production, replace PAT with a GitHub App:
- Per-user installation
- Scoped repository access
- No long-lived user tokens
- Better auditability

See GitHub documentation for App creation and installation token flow.

## Security Rules

- Never commit `GITHUB_TOKEN` to any file
- Never log token values
- Use least-privilege: only selected repo access
- `AUTO_PUSH_TO_GITHUB=false` is the required default
