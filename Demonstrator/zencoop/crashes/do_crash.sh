#!/bin/bash

zenroom='/Users/SB/Software/Ledger/crypto/Zenroom_test/zenroom-osx.command'

${zenroom} -z gener.zen | jq '.' 

${zenroom} -a verify_signature.data -k verify_signature.key -z verify_signature.zen | jq '.'
