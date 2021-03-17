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

if [ -z "$STY" ]
then
    # we are not running in screen
    exec screen -dm -S ${env_name} -L -Logfile labspace_$(date '+%d_%m_%Y_%H_%M_%S').log /bin/bash "$0";
    
else
    # we are running in screen, provide commands to execute

    ./start.sh PROD

fi


