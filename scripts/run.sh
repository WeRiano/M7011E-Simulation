#!/bin/sh

set -e

uwsgi --socket :9000 --workers 4 --master --enable-threads --module backend.wsgi