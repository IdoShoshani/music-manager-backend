# music-app-backend Helm Chart

## Introduction

This Helm Chart allows you to deploy the Music App Backend in a Kubernetes environment.

## Prerequisites

- Kubernetes 1.12+
- Helm 3+

## Installation

To install the Chart with the release name `backend-release`:

```bash
helm install backend-release https://gitlab.com/sela-tracks/1109/students/idosh/final_project/application/music-manager-backend.git/music-app-backend
```

## Uninstallation

To remove/delete the `backend-release` deployment:

```bash
helm uninstall backend-release
```

## Configuration

The table below lists the configurable parameters and their default values:

| Parameter                            | Description                          | Default                                                                               |
| ------------------------------------ | ------------------------------------ | ------------------------------------------------------------------------------------- |
| fullnameOverride                     | Customized full name for resources   | "music-app-backend"                                                                   |
| replicaCount                         | Number of replicas                   | 1                                                                                     |
| image.repository                     | Image repository                     | idoshoshani123/music-app-backend                                                      |
| image.tag                            | Image tag                            | "1.0"                                                                                 |
| image.pullPolicy                     | Image pull policy                    | IfNotPresent                                                                          |
| service.type                         | Kubernetes service type              | ClusterIP                                                                             |
| service.port                         | Service port                         | 5000                                                                                  |
| env.MONGO_URI                        | Environment variable for MongoDB URI | "mongodb://user:$(MONGODB_PASSWORD)@mongodb.mongodb.svc.cluster.local:27017/music_db" |
| resources                            | Resource settings                    | {}                                                                                    |
| probes.liveness.initialDelaySeconds  | Delay before liveness probe starts   | 10                                                                                    |
| probes.liveness.periodSeconds        | Frequency of liveness probe checks   | 5                                                                                     |
| probes.readiness.initialDelaySeconds | Delay before readiness probe starts  | 5                                                                                     |
| probes.readiness.periodSeconds       | Frequency of readiness probe checks  | 5                                                                                     |

Values can be modified using the `--set` flag or by editing the `values.yaml` file.

## Example Usage

To install with a different `MONGO_URI`:

```bash
helm install backend-release ./music-app-backend --set env.MONGO_URI="mongodb://custom-mongo:27017/music_db"
```

## **Additional Explanations:**

- **Fixed Service Name:** The `fullnameOverride: "music-app-backend"` in `values.yaml` ensures that the Service name is always `music-app-backend`, allowing the frontend to communicate with the backend using this consistent name.

- **Probes for Health Checks:**

  - The `livenessProbe` ensures that Kubernetes can detect if the application is unhealthy and restart it if necessary.
  - The `readinessProbe` ensures that the application is ready to serve traffic before sending requests to it.

- **Configurable Settings:** All critical parameters, including the health probes, are defined in `values.yaml`, enabling easy customization.

- **Helm Chart Structure:** The structure aligns with the frontend to maintain consistency and simplify maintenance.

## **Notes on Communication with the Frontend:**

- **The frontend expects the backend to be available at `music-app-backend:5000`:** Setting `fullnameOverride` ensures that the backend Service is named exactly as the frontend references it via `BACKEND_URL`.

## **How to Ensure Everything Works Properly:**

1. **Install the backend:**

   ```bash
   helm install backend-release ./music-app-backend
   ```

2. **Install the frontend:**

   Make sure the `BACKEND_URL` in the `values.yaml` of the frontend matches the backend Service name (already set as default).

   ```bash
   helm install frontend-release ./music-app-frontend
   ```

3. **Check communication:**
   - Ensure the frontend and backend Pods are running successfully.
   - Use the `kubectl logs` command to check for errors.
   - Verify that the frontend can communicate with the backend and make API calls.

## **Summary:**

- **Consistent Naming:** Using `fullnameOverride` prevents naming conflicts and ensures smooth communication between the frontend and backend.
- **Health and Readiness Monitoring:** Liveness and readiness probes are configured to ensure the application remains healthy and ready to serve traffic at all times.
- **Ease of Use and Customization:** Configuration can be easily modified through `values.yaml` or `--set` flags.
