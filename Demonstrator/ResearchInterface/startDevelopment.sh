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

python manage.py runserver --settings=labspace.settingsD


