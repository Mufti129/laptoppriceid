#!/bin/bash
# Script sinkronisasi Git otomatis untuk LaptopPrice ID
set -e

echo "=== Git Sync LaptopPrice ID ==="
git status

read -p "Lanjutkan commit dan push? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    git add .
    git commit -m "feat: sync laptop market intelligence system"
    git push origin main
    echo "[SUCCESS] Repository berhasil disinkronisasi!"
fi
