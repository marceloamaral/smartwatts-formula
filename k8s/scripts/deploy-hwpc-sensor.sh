#!/bin/bash
kubectl apply -f templates/hwpc-sensor-deployment.yaml
sleep 10s
kubectl get pods
kubectl logs -l app.kubernetes.io/name=hwpc-sensor-exporter
