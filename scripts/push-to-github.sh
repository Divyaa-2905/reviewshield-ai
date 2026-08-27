#!/usr/bin/env bash
set -euo pipefail

# Run this after authenticating with GitHub:
#   gh auth login

REPO_NAME="reviewshield-ai"
GITHUB_USER="shivanshehehe"

echo "Creating GitHub repository: ${GITHUB_USER}/${REPO_NAME}"

gh repo create "${REPO_NAME}" \
  --public \
  --source=. \
  --remote=origin \
  --description "Multi-Modal AI System for Online Review Fraud and Coordinated Manipulation Detection" \
  --push

echo ""
echo "Repository created and pushed:"
echo "https://github.com/${GITHUB_USER}/${REPO_NAME}"
