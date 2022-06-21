#!/bin/bash

USER="root"
PWD="admin"

helm repo add bitnami https://charts.bitnami.com/bitnami

helm install smartwatts \
    --set auth.usernames[0]=${USER},auth.databases[0]="mongodb" \
    --set auth.rootPassword=${PWD},auth.username=${USER},auth.password=${PWD} \
    bitnami/mongodb
