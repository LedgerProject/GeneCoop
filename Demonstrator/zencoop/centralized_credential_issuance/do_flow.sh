#!/bin/bash

zenroom='../../../../crypto/Zenroom_test/zenroom-osx.command'

${zenroom} -z centr_issuer.zen | jq '.' > create_proof.data

${zenroom} -a create_proof.data -z create_proof.zen | jq '.' > verify_proof.data

${zenroom} -a verify_proof.data -z verify_proof.zen | jq '.'
