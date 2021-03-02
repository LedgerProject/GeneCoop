#!/bin/bash

zenroom='../../../../crypto/Zenroom_test/zenroom-osx.command'

${zenroom} -z challenge.zen | jq '.' > sign.data

${zenroom} -a sign.data -k sign.key -z sign.zen | jq '.' > verify_signature.data

${zenroom} -a verify_signature.data -k verify_signature.key -z verify_signature.zen | jq '.'
