#!/bin/bash

create_user_cmd(){
    templ='from django.contrib.auth import get_user_model; \nUser = get_user_model(); \nif not User.objects.filter(username="USERNAME").exists():\n\tUser.objects.OPERATION("USERNAME", "EMAIL", "PASSWORD")\n'
    
    if [ "${1} " == "superuser " ]
    then
        username=$(cat .superuser.json | jq '.username')
        email=$(cat .superuser.json | jq '.email' )
        password=$(cat .superuser.json | jq '.password' )
        operation=create_superuser
    elif [ "${1} " == "researcher " ]
    then
        username=$(cat .researcher.json | jq '.username')
        email=$(cat .researcher.json | jq '.email' )
        password=$(cat .researcher.json | jq '.password' )
        operation=create_user
    else
        echo "ERROR: ${1} not understood";
        return 1;
    fi

    echo -e ${templ} | sed "s/\"USERNAME\"/${username}/g" | sed "s/OPERATION/${operation}/g" | sed "s/\"PASSWORD\"/${password}/g" |  sed "s/\"EMAIL\"/${email}/g"


}



