unset WEB_EXT_API_KEY
unset WEB_EXT_API_SECRET

if [ "${1} " == "u " ]
then
    web-ext --verbose -s user_webext/ run
elif [ "${1} " == "r " ]
then
    web-ext --verbose -s researcher_webext/ run
else
    echo "Error: unknown option ${1}"
fi