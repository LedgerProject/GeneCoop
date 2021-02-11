#!/bin/bash

create_user_cmd() {
    local templ='from django.contrib.auth import get_user_model; \nUser = get_user_model(); \nif not User.objects.filter(username="USERNAME").exists():\n\tUser.objects.OPERATION("USERNAME", "EMAIL", "PASSWORD")\n'

    if [ "${1} " == "superuser " ]; then
        local username=$(cat .superuser.json | jq '.username')
        local email=$(cat .superuser.json | jq '.email')
        local password=$(cat .superuser.json | jq '.password')
        local operation=create_superuser
    elif [ "${1} " == "researcher " ]; then
        local username=$(cat .researcher.json | jq '.username')
        local email=$(cat .researcher.json | jq '.email')
        local password=$(cat .researcher.json | jq '.password')
        local operation=create_user
    else
        echo "ERROR: ${1} not understood"
        return 1
    fi

    echo -e ${templ} | sed "s/\"USERNAME\"/${username}/g" | sed "s/OPERATION/${operation}/g" | sed "s/\"PASSWORD\"/${password}/g" | sed "s/\"EMAIL\"/${email}/g"

}

check_restroom() {
    local apiroom_url=$(grep ^APIROOM_URL labspace/constants.py | tr -d ' ' | cut -d'=' -f2 | sed "s/'//g")

    local response=$(curl -X POST "${apiroom_url}/api/zencoop/keypair" -H "accept: application/json" -H "Content-Type: application/json" -d "{\"data\":{},\"keys\":{}}" 2>/dev/null)

    local check=$(echo ${response} | jq '.Researcher.keypair.private_key')

    if [ "${check} " == " " ]; then
        echo "Restroom does not seem to reply on ${apiroom_url}/api/zencoop/!!!"
        return 1
    else
        echo "Restroom replying on ${apiroom_url}/api/zencoop/"
    fi

}
