#!/bin/bash

zenroom="~/bin/zenroom-osx.command"

one=sign.data
two=verify_signature.data

${zenroom} -z challenge.zen | jq '.' > ${one}

${zenroom} -a ${one} -k sign.key -z sign.zen | jq '.' > ${two}

${zenroom} -a ${two} -k verify_signature.key -z verify_signature.zen | jq '.'
