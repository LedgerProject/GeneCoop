#!/bin/bash
conda_env=Demonstrator
env_type=${1}

if [ "${env_type} " == "PROD " ]
then
    settings=labspace.settingsP
elif [ "${env_type} " == "DEV " ]
then
    settings=labspace.settingsD
else
    echo -e "Environment unknown: {1}"
fi

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

if [ "${CONDA_DEFAULT_ENV} " != "${conda_env} " ]
then
    source ${conda_shell}
    conda activate ${conda_env}
fi

pip install -r ./pip_requirements.txt

if [ "${env_type} " == "PROD " ]
then
    SECRET_KEY=$(cat .secret_key) python manage.py makemigrations --settings=${settings}
    SECRET_KEY=$(cat .secret_key) python manage.py migrate --settings=${settings}
else
    python manage.py makemigrations --settings=${settings}
    python manage.py migrate --settings=${settings}
fi


. ./util_functions.sh


create_user_cmd superuser | python manage.py shell --settings=${settings}
create_user_cmd user | python manage.py shell --settings=${settings}
create_researcher_cmd | python manage.py shell --settings=${settings}


# if ! check_restroom
# then
#    exit 1
# fi

if [ "${env_type} " == "PROD " ]
then
    SECRET_KEY=$(cat .secret_key) python manage.py runserver --settings=${settings}
else
    python manage.py runserver -v2 --settings=${settings}
fi



