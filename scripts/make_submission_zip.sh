#!/usr/bin/env bash
# Build ecommerce-backend-submission.zip next to the ecommerce_backend folder.
# Excludes venv, .git, __pycache__, .pyc, local SQLite DB.
#
# Run from anywhere:
#   bash ecommerce_backend/scripts/make_submission_zip.sh

set -euo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"
PARENT="$(cd "$REPO/.." && pwd)"
NAME="$(basename "$REPO")"
OUT="$PARENT/ecommerce-backend-submission.zip"

cd "$PARENT"
rm -f "$OUT"
zip -r "$OUT" "$NAME" \
  -x "${NAME}/venv/*" \
  -x "${NAME}/.git/*" \
  -x "*__pycache__*" \
  -x "*.pyc" \
  -x "*.DS_Store" \
  -x "${NAME}/db.sqlite3" \
  -x "${NAME}/db.sqlite3-journal"

echo "Created: $OUT"
ls -lh "$OUT"
