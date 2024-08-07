# nr-data-catalogue

## What is the NRM Data Catalogue?

The NRM Data Catalogue is a service that helps users find and access relevant metadata for data assets within the Natural Resource Ministries (NRM). Relevant metadata includes information about lineage, storage, transformation logic, security classification, and availability of the data. The NRM Data Catalogue also generates data insights, column-level data profiling, and data quality reports, and links data assets to associated data models in the NRM Data Model library. Users are able to search for data based on specific criteria such as Ministry, business area, data custodian, schema/table/column names, keywords, or publication date.

Visit the DEV NRM Data Catalogue here (VPN connection required):
http://nr-data-catalogue-dev.apps.emerald.devops.gov.bc.ca/

Visit the TEST NRM Data Catalogue here (VPN connection required):
http://nr-data-catalogue-test.apps.emerald.devops.gov.bc.ca/

The NRM Data Catalogue leverages an open-source data catalogue tool called OpenMetadata. OpenMetadata is deployed in the Emerald cluster of the BCGov OpenShift Container Platform. Deployment details below.

## Deploying OpenMetadata to OpenShift
Prerequisites:
- OpenShift CLI
- Helm CLI

### 1. Apply all the network policies and pod label policies under 'oc' folder:
Navigate to the 'openshift' folder then:
```
oc apply -f .
```

### 2. Create required database and application secrets
```
oc create secret generic airflow-db-secrets --from-literal=airflow-db-password=airflow_pass
oc create secret generic db-secrets --from-literal=openmetadata-db-password=openmetadata_password
oc create secret generic airflow-secrets --from-literal=openmetadata-airflow-password=admin
```
Note: also need to create oidc-secrets and postgres-secrets
### 3. Deploy OpenMetadata dependencies to OpenShift
Source: https://github.com/open-metadata/openmetadata-helm-charts/tree/main/charts/deps

Navigate to the 'deps' chart folder then:
```
helm install openmetadata-dependencies .
```

### 4. Deploy OpenMetadata to OpenShift
Source: https://github.com/open-metadata/openmetadata-helm-charts/tree/main/charts/openmetadata

Once all the dependencies are running, navigate to the 'openmetadata' chart folder then:
```
helm install openmetadata .
```
Note: Sometimes old PVC and volumes will break new pods.

####  OpenSearch Dockerfile and Use of GHCR
OpenSearch and PostgreSQL require modified Dockerfiles to work within the OpenShift restricted security context. The Dockerfiles can be found under charts/. These images are built automatically and pushed to the GHCR any time there is a push or PR to the **main** branch.

Usage examples:
```sh
docker pull ghcr.io/bcgov/nr-openmetadata-opensearch:main
```
```sh
docker pull ghcr.io/bcgov/nr-openmetadata-postgresql:main
```

#### Helm chart modifications
To review all Helm chart modifications (i.e. differences between the OpenMetadata default config and the OpenShift restricted security context config), search this repo for "DF-NOTE:" annotations.
Each of these files has been customized to work in OpenShift Emerald environment:

![alt text](image.png)

To update the chart when changes are made:
```sh
helm upgrade openmetadata .
```

To add OpenMetadata to your local Helm repositories:
```sh
helm repo add open-metadata https://helm.open-metadata.org/
```
To get the latest version of OpenMetadata and it's dependencies:
```sh
helm repo update open-metadata
helm pull open-metadata/openmetadata-dependencies
helm pull open-metadata/openmetadata
```