#!/bin/bash

zenroom='zenroom'

${zenroom} -a message.data -k sign.key -z signhash.zen | jq '.' > verify_hash.data

${zenroom} -a verify_hash.data -k verify_signature.key -z verify_signed_hash.zen | jq '.'
