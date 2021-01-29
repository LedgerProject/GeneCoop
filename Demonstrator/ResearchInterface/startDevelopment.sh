#!/bin/bash
env_name=Demonstrator

if [ "$(uname)" == "Darwin" ]
then
    conda_shell=~/opt/miniconda3/etc/profile.d/conda.sh
else
    conda_shell=~/miniconda3/etc/profile.d/conda.sh
fi

if [ ! -f ./manage.py ]
then
    echo "Wrong directory, needs to be where manage.py is"
    exit 1
fi

if [ "${CONDA_DEFAULT_ENV} " != "${env_name} " ]
then
    source ${conda_shell}
    conda activate ${env_name}
fi

pip install -r ./pip_requirements.txt

python manage.py makemigrations --settings=labspace.settingsD
python manage.py migrate --settings=labspace.settingsD

echo -e 'from django.contrib.auth import get_user_model; \nUser = get_user_model(); \nif not User.objects.filter(username="labspace").exists():\n\tUser.objects.create_superuser("labspace", "admin@localhost", "genecoop")\n' | python manage.py shell --settings=labspace.settingsD

python manage.py runserver --settings=labspace.settingsD


