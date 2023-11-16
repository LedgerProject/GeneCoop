#!/bin/bash

zenroom="~/bin/zenroom-osx.command"

vc='./signed_vc.data'

${zenroom} -k vc_sign.keys -a vc_sign.data -z vc_sign.zen | jq '.' > ${vc}

${zenroom} -k vc_verify.keys -a ${vc} -z vc_verify.zen | jq '.'


