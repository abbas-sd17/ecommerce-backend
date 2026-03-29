#!/usr/bin/env bash
# Create github.com/abbas-sd17/ecommerce-backend via API (needs token), then push main.
#
# Usage:
#   export GITHUB_TOKEN=ghp_xxxxxxxx   # classic PAT with "repo" scope
#   bash scripts/github_create_and_push.sh
#
# Or create the repo manually (empty, no README): https://github.com/new?name=ecommerce-backend
# Then: git remote add origin https://github.com/abbas-sd17/ecommerce-backend.git && git push -u origin main

set -euo pipefail
REPO_OWNER="abbas-sd17"
REPO_NAME="ecommerce-backend"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if ! git rev-parse --git-dir >/dev/null 2>&1; then
  echo "Not a git repository: $ROOT"
  exit 1
fi

if [[ -n "${GITHUB_TOKEN:-}" ]]; then
  echo "Creating https://github.com/${REPO_OWNER}/${REPO_NAME} ..."
  HTTP_CODE=$(curl -s -o /tmp/gh_create_repo.json -w "%{http_code}" \
    -X POST "https://api.github.com/user/repos" \
    -H "Accept: application/vnd.github+json" \
    -H "Authorization: Bearer ${GITHUB_TOKEN}" \
    -d "{\"name\":\"${REPO_NAME}\",\"private\":false,\"description\":\"Scaler Neovarsity — Django e-commerce backend (DRF, payments, AWS)\"}")
  if [[ "$HTTP_CODE" == "201" ]]; then
    echo "Repository created."
  elif [[ "$HTTP_CODE" == "422" ]]; then
    echo "Repo may already exist (422). Continuing with remote/push..."
    cat /tmp/gh_create_repo.json 2>/dev/null || true
  else
    echo "GitHub API HTTP $HTTP_CODE"
    cat /tmp/gh_create_repo.json 2>/dev/null || true
    exit 1
  fi
else
  echo "GITHUB_TOKEN not set — skipping API create."
  echo "Create an empty repo at: https://github.com/new?name=${REPO_NAME}"
fi

git remote remove origin 2>/dev/null || true
git remote add origin "https://github.com/${REPO_OWNER}/${REPO_NAME}.git"
echo "Pushing main → origin ..."
git push -u origin main
echo "Done: https://github.com/${REPO_OWNER}/${REPO_NAME}"
