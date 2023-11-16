#!/bin/bash

zenroom="~/bin/zenroom-osx.command"

one=verify_hash.data

${zenroom} -a message.data -k signhash.key -z signhash.zen | jq '.' > ${one}

${zenroom} -a ${one} -k verify_signature_hash.key -z verify_signature_hash.zen | jq '.'
