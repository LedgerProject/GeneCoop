#!/bin/bash
env_name=Demonstrator
settings=labspace.settingsP

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
    exec screen -dm -S ${env_name} -L -Logfile labspace_$(date '+%d_%m_%Y_%H_%M_%S').log /bin/bash "$0";
    
else
    # we are running in screen, provide commands to execute

    if [ "${CONDA_DEFAULT_ENV} " != "${env_name} " ]
    then
        source ${conda_shell}
        conda activate ${env_name}
    fi

    pip install -r ./pip_requirements.txt

    . ./util_functions.sh

    create_user_cmd superuser | python manage.py shell --settings=${settings}
    create_user_cmd researcher | python manage.py shell --settings=${settings}
    

    export SECRET_KEY=$(cat .secret_key); python manage.py makemigrations --settings=${settings}
    export SECRET_KEY=$(cat .secret_key); python manage.py migrate --settings=${settings}

    if ! check_restroom
    then
        exit 1
    fi


    export SECRET_KEY=$(cat .secret_key); python manage.py runserver --settings=${settings}

fi


