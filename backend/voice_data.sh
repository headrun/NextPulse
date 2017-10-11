
#!/bin/bash
echo "management_command running"


export DJANGO_SETTINGS_MODULE=backend.settings 

cd /var/www/html/NextPulse/backend
. venv/bin/activate


python manage.py generate_people_data --settings=backend.prod_settings

python manage.py ppl_accuracy_generation --settings=backend.prod_settings

python manage.py target_values_new --settings=backend.prod_settings

python manage.py headcount_data_modify --settings=backend.prod_settings

python manage.py peoples_dashboard --settings=backend.prod_settings

