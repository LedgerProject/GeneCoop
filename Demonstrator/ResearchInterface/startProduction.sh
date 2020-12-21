#!/bin/bash
if [ -z "$STY" ]
then
    # we are not running in screen
    exec screen -dm -S screenName /bin/bash "$0";
else
    # we are running in screen, execute script
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

    source ~/miniconda3/etc/profile.d/conda.sh

    screen_name=Demonstrator
    conda activate ${screen_name}

    export SECRET_KEY=$(cat .secret_key); python manage.py runserver --settings=labspace.settingsP

fi


