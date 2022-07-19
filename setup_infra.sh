#!/bin/bash
if [[ $# -eq 0 ]] ; then
    echo 'Please enter your bucket name as ./setup_infra.sh your-bucket'
    exit 0
fi