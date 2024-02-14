# #!/usr/bin/env bash
# # Exit on error
# set -o errexit

# # Install dependencies
# pip install -r requirements.txt

# # Run necessary Django commands
# python manage.py collectstatic --no-input
# python manage.py migrate
# python manage.py populate_data


#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Run necessary Django commands
python manage.py collectstatic --no-input
python manage.py migrate

# Check if superuser already exists
# if [ ! -f "superuser_created.txt" ]; then
#     python manage.py createsuperuser --noinput --username admin --email admin@example.com --password Dipec12345@
#     touch superuser_created.txt
# fi

# Check if data already populated
if [ ! -f "data_populated.txt" ]; then
    python manage.py populate_data
    touch data_populated.txt
fi
