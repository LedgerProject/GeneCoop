#!/bin/bash
env_name=Demonstrator
settings=labspace.settingsD

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

python manage.py makemigrations --settings=${settings}
python manage.py migrate --settings=${settings}

. ./util_functions.sh


create_user_cmd superuser | python manage.py shell --settings=${settings}
create_user_cmd user | python manage.py shell --settings=${settings}
create_researcher_cmd | python manage.py shell --settings=${settings}

# if ! check_restroom
# then
#     exit 1
# fi

python manage.py runserver -v2 --settings=${settings}


