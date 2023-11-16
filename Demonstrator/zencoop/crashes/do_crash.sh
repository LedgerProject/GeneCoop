#!/bin/bash

zenroom="~/bin/zenroom-osx.command"

${zenroom} -z gener.zen | jq '.' 

${zenroom} -a verify_signature.data -k verify_signature.key -z verify_signature.zen | jq '.'
