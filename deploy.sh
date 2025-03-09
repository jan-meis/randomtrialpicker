#!/bin/bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

ln -s $SCRIPT_DIR/nginx/randomtrialpicker.conf /etc/nginx/conf.d/randomtrialpicker.conf
ln -ns $SCRIPT_DIR/www /var/www/randomtrialpicker
