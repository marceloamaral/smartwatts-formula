#!/bin/bash
kubectl apply -f templates/smartwatts-deployment.yaml

sleep 10s
kubectl get pods
kubectl logs -l app.kubernetes.io/name=smartwatts-exporte
