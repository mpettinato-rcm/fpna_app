# build.sh
#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

# Tailwind v4 standalone CLI (no Node needed)
curl -sL https://github.com/tailwindlabs/tailwindcss/releases/latest/download/tailwindcss-linux-x64 -o tailwindcss
chmod +x tailwindcss
./tailwindcss -i fpna_app/assets/tailwind.css -o fpna_app/static/css/tailwind.css --minify

python manage.py collectstatic --no-input
python manage.py migrate
