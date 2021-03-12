#!/bin/bash

zenroom='/Users/SB/Software/Ledger/crypto/Zenroom_test/zenroom-osx.command'

${zenroom} -a signhash.data -k sign.key -z signhash.zen | jq '.' > verify_signature.data

${zenroom} -a verify_signature.data -k verify_signature.key -z verify_signature.zen | jq '.'
