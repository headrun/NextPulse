
#!/bin/bash
echo "management_command running"


export DJANGO_SETTINGS_MODULE=backend.settings 

cd /var/www/html/NextPulse/backend
. venv/bin/activate


python manage.py send_report

python manage.py customer_login

