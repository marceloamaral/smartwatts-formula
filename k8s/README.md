## Deploy
`./deploy-all.sh`

## Inspect the results in DB
```
kubectl run --namespace default smartwatts-mongodb-client --rm --tty -i --restart='Never' --env="MONGODB_ROOT_PASSWORD=$MONGODB_ROOT_PASSWORD" --image docker.io/bitnami/mongodb:5.0.9-debian-10-r15 --command -- bash

mongosh admin --host "smartwatts-mongodb" --authenticationDatabase admin -u root -p $MONGODB_ROOT_PASSWORD

use db_out

db.prep.find()
```

## Undeploy
`./delete-all.sh`
