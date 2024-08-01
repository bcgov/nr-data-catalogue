# This script uses the "openmetadata-ingestion~=0.13.0" library to interact with the OpenMetadata API

from metadata.generated.schema.entity.services.connections.metadata.openMetadataConnection import (OpenMetadataConnection,)
from metadata.generated.schema.security.client.openMetadataJWTClientConfig import (OpenMetadataJWTClientConfig,)
from metadata.ingestion.ometa.ometa_api import OpenMetadata

server_config = OpenMetadataConnection(
    hostPort="https://nr-data-catalogue-test.apps.emerald.devops.gov.bc.ca/api", # Dev environment
    authProvider="openmetadata",
    securityConfig=OpenMetadataJWTClientConfig(
        jwtToken="" # JWT is acquired from ingestion bot in the UI
    ),
)
metadata = OpenMetadata(server_config)

assert metadata.health_check()  # Will fail if it cannot reach the server

# Example of how to update the data class tag on a table

from metadata.generated.schema.entity.data.table import Table

metadata.patch_tag(
    entity=Table,
    entity_id="04c7576c-fe5e-4dad-8d0c-23d4453038c5",
    tag_fqn="Data Security Classification.Public",
)