import json
from config import *
from metadata.ingestion.ometa.ometa_api import OpenMetadata
from metadata.generated.schema.entity.services.connections.metadata.openMetadataConnection import (
    OpenMetadataConnection,
    AuthProvider,
)

from metadata.generated.schema.security.client.openMetadataJWTClientConfig import (
    OpenMetadataJWTClientConfig,
)

from metadata.generated.schema.api.services.createDatabaseService import (
    CreateDatabaseServiceRequest,
)
from metadata.generated.schema.entity.services.databaseService import (
    DatabaseService,
    DatabaseServiceType,
    DatabaseConnection,
)

from metadata.generated.schema.type.tagLabel import (
    LabelType,
    State,
    TagLabel,
    TagSource,
)

from metadata.generated.schema.entity.services.connections.database.snowflakeConnection import (
    SnowflakeConnection,
)

from metadata.generated.schema.api.data.createDatabase import (
    CreateDatabaseRequest,
)
from metadata.generated.schema.type.entityReference import EntityReference

from metadata.generated.schema.api.data.createDatabaseSchema import (
    CreateDatabaseSchemaRequest,
)

from metadata.generated.schema.api.data.createTable import CreateTableRequest
from metadata.generated.schema.entity.data.table import (
    Column,
    DataType,
    Table,
)
from metadata.generated.schema.api.data.createPipeline import CreatePipelineRequest
from metadata.generated.schema.api.data.createTopic import CreateTopicRequest
from metadata.generated.schema.api.lineage.addLineage import AddLineageRequest
from metadata.generated.schema.api.services.createStorageService import (
    CreateStorageServiceRequest,
)
from metadata.generated.schema.api.services.createPipelineService import (
    CreatePipelineServiceRequest,
)

from metadata.generated.schema.api.services.createMessagingService import (
    CreateMessagingServiceRequest,
)

from metadata.generated.schema.entity.services.connections.pipeline.airflowConnection import (
    AirflowConnection,
)
from metadata.generated.schema.entity.data.dashboard import Dashboard
from metadata.generated.schema.entity.data.database import Database
from metadata.generated.schema.entity.data.databaseSchema import DatabaseSchema
from metadata.generated.schema.entity.data.pipeline import (
    Pipeline,
    PipelineStatus,
    Task,
)
from metadata.generated.schema.entity.services.dashboardService import DashboardService
from metadata.generated.schema.entity.services.databaseService import DatabaseService
from metadata.generated.schema.entity.services.messagingService import MessagingService
from metadata.generated.schema.entity.services.mlmodelService import MlModelService
from metadata.generated.schema.entity.services.pipelineService import PipelineService
from metadata.generated.schema.entity.services.storageService import StorageService

from metadata.generated.schema.api.lineage.addLineage import AddLineageRequest
from metadata.generated.schema.type.entityLineage import EntitiesEdge
from metadata.generated.schema.type import basic, entityReference, schema, tagLabel

from metadata.generated.schema.api.data.createContainer import CreateContainerRequest



# to connect to OpenMetadata Server
security_config = OpenMetadataJWTClientConfig(
    jwtToken=api_key 
)
server_config = OpenMetadataConnection(
    hostPort="http://localhost:8585/api",
    securityConfig=security_config,
    authProvider=AuthProvider.openmetadata,
)
metadata = OpenMetadata(server_config)
metadata.health_check()  # we are able to connect to OpenMetadata Server

# Create DatabaseService
#
#
create_service = CreateDatabaseServiceRequest(
    name="test-snowflake",
    serviceType=DatabaseServiceType.Snowflake,
    connection=DatabaseConnection(
        config=SnowflakeConnection(
            username="username",
            password="password",
            account="http://localhost:1234",
            warehouse="dw",
        )
    ),
)

service_entity = metadata.create_or_update(data=create_service)


# Create a Storage Service
#
create_storage_service_entity = CreateStorageServiceRequest(
    name="S3 Sample", serviceType="S3", description="S3 Object Store", connection={
        "config": {
            "type": "S3",
            "awsConfig": {"awsRegion": "us-west-1"}
        }
    }
)
storage_service_entity = metadata.create_or_update(data=create_storage_service_entity)


# Create Pipeline Service
#
pipeline_service_json = json.loads(
    """
{
	"serviceType": "Airflow",
	"name": "sample_airflow1",
	"connection": {
                "config": {
                "type": "Airflow",
                "hostPort": "http://localhost:8080",
                "connection": {
                   "type": "Backend"
                 }
           }
	}
}
"""
)
create_pipeline_service_entity = CreatePipelineServiceRequest(**pipeline_service_json)
pipeline_service_entity = metadata.create_or_update(create_pipeline_service_entity)

# Create Messaging Service , Kafka
#
messaging_service_json = json.loads(
    """
{
  "serviceType": "Kafka",
  "name": "sample_kafka1",
  "connection": {
    "config": {
      "type": "Kafka",
      "bootstrapServers": "localhost:9092"
    }
  }
}
"""
)
create_messaging_service_entity = CreateMessagingServiceRequest(
    **messaging_service_json
)
messaging_service_entity = metadata.create_or_update(create_messaging_service_entity)

# Create Database
#
create_db = CreateDatabaseRequest(
    name="test-db",
    service="test-snowflake",
)

db_entity = metadata.create_or_update(create_db)


create_schema = CreateDatabaseSchemaRequest(
    name="test-schema", database="test-snowflake.test-db"
)

schema_entity = metadata.create_or_update(data=create_schema)

create_table = CreateTableRequest(
    name="dim_orders",
    databaseSchema="test-snowflake.test-db.test-schema",
    columns=[Column(name="id", dataType=DataType.BIGINT)],
)

table_entity = metadata.create_or_update(create_table)

table_a = CreateTableRequest(
    name="tableA",
    databaseSchema="test-snowflake.test-db.test-schema",
    columns=[Column(name="id", dataType=DataType.BIGINT)],
)

table_b = CreateTableRequest(
    name="tableB",
    databaseSchema="test-snowflake.test-db.test-schema",
    columns=[Column(name="id", dataType=DataType.BIGINT)],
)

table_a_entity = metadata.create_or_update(data=table_a)
table_b_entity = metadata.create_or_update(data=table_b)

PII_TAG_LABEL = TagLabel(
    tagFQN="PII.Sensitive",
    labelType=LabelType.Automated,
    state=State.Suggested.value,
    source=TagSource.Classification,
)

# PATCH TAG EXAMPLE

from metadata.generated.schema.type.tagLabel import (
    LabelType,
    State,
    TagLabel,
    TagFQN,
    TagSource,
)
from metadata.ingestion.ometa.mixins.patch_mixin_utils import PatchOperation

metadata.patch_tags(
            entity=Table, source=table_entity, tag_labels=[TagLabel(tagFQN=TagFQN("Tier.Tier3"), source=TagSource.Classification, labelType=LabelType.Manual, state=State.Confirmed)], operation=PatchOperation.ADD
        )


from metadata.ingestion.models.table_metadata import ColumnTag

metadata.patch_column_tags(
    table=table_b_entity,
    column_tags=[ColumnTag(column_fqn="test-snowflake.test-db.test-schema.tableB.id", tag_label=PII_TAG_LABEL)]
)
metadata.patch_column_tags(
    table=table_b_entity,
    column_tags=[ColumnTag(column_fqn="test-snowflake.test-db.test-schema.tableB.id", tag_label=PII_TAG_LABEL)],
    operation=PatchOperation.REMOVE
)


# PATCH OPERATION TO UPDATE DESCRIPTION ( TABLE ENTITY )
from copy import deepcopy

from metadata.generated.schema.type.basic import Markdown
table_entity_modified = deepcopy(table_entity)
table_entity_modified.description = Markdown("Updated description")


metadata.patch(Table,table_entity, table_entity_modified)

# OWNERS ( TABLE ENTITY )

from metadata.generated.schema.type.entityReference import EntityReference
from metadata.generated.schema.type.entityReferenceList import EntityReferenceList

table_entity = metadata.get_by_name(entity=Table, fqn='table-fqn', fields=["owners"])
table_entity_modified = deepcopy(table_entity)


# PATCH OPERATION TO UPDATE USER OWNERS ( TABLE ENTITY )

table_entity_modified.owners = EntityReferenceList(root=[EntityReference(id="id-of-the-user", type="user")])
metadata.patch(Table,table_entity, table_entity_modified)


# PATCH OPERATION TO UPDATE TEAM OWNERS ( TABLE ENTITY )

table_entity_modified.owners = EntityReferenceList(root=[EntityReference(id="id-of-the-team", type="team")])
metadata.patch(Table,table_entity, table_entity_modified)

# PATCH OPERATION TO UPDATE TIER ( TABLE ENTITY )

table_entity.tags = EntityReferenceList(root=[EntityReference(id="id-of-the-team", type="team")])
metadata.patch(Table,table_entity, table_entity_modified)

# PATCH OPERATION ADD DOMAINS ( TABLE ENTITY )

from metadata.generated.schema.entity.domains.domain import Domain
#List Domains
fetch_domain = metadata.list_entities(Domain).entities[2] # fetch random domain for example

metadata.patch_domain(entity=table_entity, domain=fetch_domain)


# Create pipeline
#
task = Task(name="ingest", sourceUrl="http://localhost:8080/table_etl/ingest")
pipeline_request = CreatePipelineRequest(
    name="table_etl",
    displayName="Table ETL",
    description="Table ETL",
    sourceUrl="http://localhost:8080/table_etl",
    tasks=[task],
    service=pipeline_service_entity.fullyQualifiedName
)
pipeline = metadata.create_or_update(pipeline_request)

# PATCH PIPELINE DESCRIPTION
dest_pipeline = deepcopy(pipeline)
dest_pipeline.description = Markdown("Update description using PATCH")
metadata.patch(Pipeline, pipeline, dest_pipeline)

## Create Topic
topic_request = CreateTopicRequest(
    name="customer_events",
    description="Kafka topic to capture the customer events such as location updates or profile updates",
    partitions=56,
    retentionSize=455858109,
    messageSchema=schema.Topic(
        schemaType="Avro",
        schemaText='{"namespace":"org.open-metadata.kafka","name":"Customer","type":"record","fields":[{"name":"id","type":"string"},{"name":"first_name","type":"string"},{"name":"last_name","type":"string"},{"name":"email","type":"string"},{"name":"address_line_1","type":"string"},{"name":"address_line_2","type":"string"},{"name":"post_code","type":"string"},{"name":"country","type":"string"}]}',
    ),
    service=messaging_service_entity.fullyQualifiedName,
)
topic = metadata.create_or_update(topic_request)


## Create Lineage between table and pipeline as edge

add_lineage_request = AddLineageRequest(
    edge=EntitiesEdge(
        fromEntity=EntityReference(id=table_a_entity.id, type="table"),
        toEntity=EntityReference(id=pipeline.id, type="pipeline"),
    ),
)

created_lineage = metadata.add_lineage(data=add_lineage_request)

add_lineage_request = AddLineageRequest(
    edge=EntitiesEdge(
        fromEntity=EntityReference(id=pipeline.id, type="pipeline"),
        toEntity=EntityReference(id=table_b_entity.id, type="table"),
    ),
)

created_lineage = metadata.add_lineage(data=add_lineage_request)



## Create Storage Containers
container_request_json = json.loads("""
  {
    "name": "transactions2",
    "displayName": "Company Transactions",
    "description": "Bucket containing all the company's transactions",
    "parent": null,
    "prefix": "/transactions/",
    "dataModel": {
      "isPartitioned": true,
      "columns": [
        {
          "name": "date",
          "dataType": "NUMERIC",
          "dataTypeDisplay": "numeric",
          "description": "The ID of the executed transaction. This column is the primary key for this table.",
          "tags": [],
          "constraint": "PRIMARY_KEY",
          "ordinalPosition": 1,
          "children": [
          { 
          "name": "country",
           "dataType": "NUMERIC",
           "dataTypeDisplay": "numeric",
            "description": "Nested",
            "tags": [],
            "children": [
              {
               "name": "state",
                "dataType": "NUMERIC",
                "dataTypeDisplay": "numeric",
            "description": "Nested",
            "tags": []
              
              }
            ]
          }
          ]
        },
        {
          "name": "merchant",
          "dataType": "VARCHAR",
          "dataLength": 100,
          "dataTypeDisplay": "varchar",
          "description": "The merchant for this transaction.",
          "tags": [],
          "ordinalPosition": 2
        },
        {
          "name": "transaction_time",
          "dataType": "TIMESTAMP",
          "dataTypeDisplay": "timestamp",
          "description": "The time the transaction took place.",
          "tags": [],
          "ordinalPosition": 3
        }
      ]
    },
    "numberOfObjects": "50",
    "size": "102400",
    "fileFormats": [
      "parquet"
    ]
  }
""")
container_request_json['service'] = storage_service_entity.fullyQualifiedName
container_request = CreateContainerRequest(**container_request_json)
container_entity = metadata.create_or_update(container_request)

child_container_request_json = json.loads("""
{
    "name": "departments",
    "displayName": "Company departments",
    "description": "Bucket containing company department information",
    "prefix": "/departments/",
    "dataModel": null,
    "numberOfObjects": "2",
    "size": "2048",
    "fileFormats": [
      "csv"
    ]
  }
""")
child_container_request_json['parent'] = EntityReference(id=container_entity.id, type='container')
child_container_request_json['service'] = storage_service_entity.fullyQualifiedName
child_container_request = CreateContainerRequest(**child_container_request_json)
child_container_entity = metadata.create_or_update(child_container_request)

## Fetching Users

from metadata.generated.schema.entity.teams.user import User

# The name is whatever comes before the @ in their email. For example, admin@openmetadata.org you can fetch via:
user = metadata.get_by_name(entity=User, fqn="admin")

## List ALL Tables
from metadata.generated.schema.entity.data.table import Table

all_entities = metadata.list_all_entities(
    entity=Table, fields=["tags"]
)

for table in all_entities:
    # Do something
    ...

## List ALL Glossaries and its terms
from metadata.generated.schema.entity.data.glossary import Glossary
from metadata.generated.schema.entity.data.glossaryTerm import GlossaryTerm

all_glossaries = metadata.list_all_entities(
    entity=Glossary, fields=["tags"]
)
for glossary in all_glossaries:
    print(f"Glossary {glossary.name.__root__}")
    children = metadata.list_all_entities(
        entity=GlossaryTerm,
        params={"glossary": str(glossary.id.__root__)},
        fields=["children", "owner", "parent"],
    )
    for child in children:
        print(f"Term {child.fullyQualifiedName.__root__}")



## Creating API collections and endpoints
# Import necessary classes for creating API collections and endpoints
from metadata.generated.schema.api.data.createAPICollection import (
    CreateAPICollectionRequest,
)
from metadata.generated.schema.api.data.createAPIEndpoint import (
    CreateAPIEndpointRequest,
)

# Example usage

# Create a request to define a new API collection
collection_request = CreateAPICollectionRequest(
        name="pet",  # Name of the API collection
        service="sample_api_service",  # Name of the service this collection belongs to
        endpointURL="https://petstore3.swagger.io/#/pet",  # Base URL for the API collection
)
# Send the request to create or update the API collection
metadata.create_or_update(data=collection_request)

# Reference: https://docs.open-metadata.org/swagger.json

# Create a request to define a new API endpoint within the collection
endpoint_request = CreateAPIEndpointRequest(
    **{
        "name": "updatePet",  # Name of the endpoint
        "displayName": "Update Pet",  # Display name for the endpoint
        "description": "Update an existing pet",  # Description of what the endpoint does
        "endpointURL": "https://petstore3.swagger.io/#/pet/updatePet",  # URL for the endpoint
        "apiCollection": "sample_api_service.pet",  # Fully qualified name of the API collection
        "requestMethod": "PUT",  # HTTP method used by the endpoint
        "requestSchema": {
            "schemaType": "JSON",  # Type of the request schema
            "schemaFields": [
                {
                    "name": "id",  # Field name
                    "dataType": "INT",  # Data type of the field
                    "description": "ID of pet that needs to be updated",  # Description of the field
                },
                {
                    "name": "name",  # Field name
                    "dataType": "STRING",  # Data type of the field
                    "description": "Name of pet",  # Description of the field
                },
                {
                    "name": "category",  # Field name
                    "dataType": "RECORD",  # Data type of the field
                    "description": "Category of pet",  # Description of the field
                    "children": [  # Nested fields for the category
                        {
                            "name": "id",  # Field name
                            "dataType": "INT",  # Data type of the field
                            "description": "ID of category",  # Description of the field
                        },
                        {
                            "name": "name",  # Field name
                            "dataType": "STRING",  # Data type of the field
                            "description": "Name of category",  # Description of the field
                        },
                    ],
                },
            ],
        },
        "responseSchema": {
            "schemaType": "JSON",  # Type of the response schema
            "schemaFields": [
                {
                    "name": "id",  # Field name
                    "dataType": "INT",  # Data type of the field
                    "description": "ID of pet that needs to be updated",  # Description of the field
                },
                {
                    "name": "name",  # Field name
                    "dataType": "STRING",  # Data type of the field
                    "description": "Name of pet",  # Description of the field
                },
                {
                    "name": "category",  # Field name
                    "dataType": "RECORD",  # Data type of the field
                    "description": "Category of pet",  # Description of the field
                    "children": [  # Nested fields for the category
                        {
                            "name": "id",  # Field name
                            "dataType": "INT",  # Data type of the field
                            "description": "ID of category",  # Description of the field
                        },
                        {
                            "name": "name",  # Field name
                            "dataType": "STRING",  # Data type of the field
                            "description": "Name of category",  # Description of the field
                        },
                    ],
                },
            ],
        },
    }
)
# Send the request to create or update the API endpoint
metadata.create_or_update(data=endpoint_request)



# GROUP PATCH CALLS EXAMPLE

from copy import deepcopy

from metadata.generated.schema.type.basic import Markdown
from metadata.generated.schema.type.tagLabel import (
    LabelType,
    State,
    TagLabel,
    TagFQN,
    TagSource,
)
table_entity = metadata.get_by_name(Table, 'redshift_dbt.dev.public.customers_clean', fields=["tags"])
table_entity_modified: Table = deepcopy(table_entity)
table_entity_modified.description = Markdown("Updated description")
table_entity_modified.displayName = "Updated display name"
table_entity_modified.tags = [TagLabel(tagFQN=TagFQN("Tier.Tier3"), source=TagSource.Classification, labelType=LabelType.Manual, state=State.Confirmed)]

metadata.patch(Table,table_entity, table_entity_modified)