#exit on error
set -o errexit

#Install dependencies
pip install -r config/requirements.txt

#Collect static files
python manage.py collectstatic --noinput

#Run database migrations
python manage.py migrate

#Run server
python manage.py runserver