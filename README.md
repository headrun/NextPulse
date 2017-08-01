# NextPulse


## NEXTPULSE PYTHON STAGING
* * * * * /usr/local/bin/lockrun --lockfile /tmp/np_staging.lock -- uwsgi --close-on-exec -s /tmp/uwsgi_np_staging.sock --chdir /var/www/html/nextpulse_staging/NextPulse/backend/backend/ --pp .. -w backend.wsgi_staging -C666 -p 32 -H /var/www/html/nextpulse_staging/NextPulse/backend/venv/ 1>> /tmp/np_log_staging 2>> /tmp/np_err_staging


## NEXTPULSE PYTHON PROD
* * * * * /usr/local/bin/lockrun --lockfile /tmp/np_prod.lock -- uwsgi --close-on-exec -s /tmp/uwsgi_np_prod.sock --chdir /var/www/html/NextPulse/backend/backend/ --pp .. -w backend.wsgi_prod -C666 -p 32 -H /var/www/html/NextPulse/backend/venv/ 1>> /tmp/np_log_prod 2>> /tmp/np_err_prod
