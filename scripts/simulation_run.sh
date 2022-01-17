#!/bin/sh

set -e

uwsgi --http :8000 --master --enable-threads --module Simulation.wsgi
