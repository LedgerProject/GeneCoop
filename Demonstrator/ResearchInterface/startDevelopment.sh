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

superusername=$(cat .superuser|grep username| cut -d'=' -f2)
superuseremail=$(cat .superuser|grep email| cut -d'=' -f2)
superuserpassword=$(cat .superuser|grep password| cut -d'=' -f2)

researchername=$(cat .researcher|grep username| cut -d'=' -f2)
researcheremail=$(cat .researcher|grep email| cut -d'=' -f2)
researcherpassword=$(cat .researcher|grep password| cut -d'=' -f2)

templ='from django.contrib.auth import get_user_model; \nUser = get_user_model(); \nif not User.objects.filter(username="USERNAME").exists():\n\tUser.objects.OPERATION("USERNAME", "EMAIL", "PASSWORD")\n'

echo -e ${templ} | sed "s/USERNAME/${superusername}/g" | sed "s/OPERATION/create_superuser/g" | sed "s/PASSWORD/${superuserpassword}/g" |  sed "s/EMAIL/${superuseremail}/g" | python manage.py shell --settings=labspace.settingsD
echo -e ${templ} | sed "s/USERNAME/${researchername}/g" | sed "s/OPERATION/create_user/g" | sed "s/PASSWORD/${researcherpassword}/g" |  sed "s/EMAIL/${researcheremail}/g" | python manage.py shell --settings=labspace.settingsD


python manage.py runserver --settings=labspace.settingsD


