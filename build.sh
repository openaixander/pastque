#!/usr/bin/env bash
# Exit on error
set -o errexit

# Modify this line as needed for your package manager (pip, poetry, etc.)
pip install -r requirements.txt

# Clear existing collected static files
rm -rf staticfiles/

# Collect static files again
python manage.py collectstatic --noinput


# Apply any outstanding database migrations
python manage.py migrate

python manage.py createsuperuser_if_none_exists
