#!/bin/bash
env_name=Demonstrator

if [ ! -f ./manage.py ]
    then
        echo "Wrong directory, needs to be where manage.py is"
        exit 1
    fi

if [ ! -f ./.secret_key ]
then
    echo "File .secret_key is missing"
    exit 1
fi

if [ "$(uname)" == "Darwin" ]
then
    conda_shell=~/opt/miniconda3/etc/profile.d/conda.sh
else
    conda_shell=~/miniconda3/etc/profile.d/conda.sh
fi

if [ -z "$STY" ]
then
    # we are not running in screen
    exec screen -dm -S ${env_name} /bin/bash "$0";
else
    # we are running in screen, provide commands to execute

    if [ "${CONDA_DEFAULT_ENV} " != "${env_name} " ]
    then
        source ${conda_shell}
        conda activate ${env_name}
    fi


    export SECRET_KEY=$(cat .secret_key); python manage.py makemigrations --settings=labspace.settingsP
    export SECRET_KEY=$(cat .secret_key); python manage.py migrate --settings=labspace.settingsP
    export SECRET_KEY=$(cat .secret_key); python manage.py runserver --settings=labspace.settingsP

fi


