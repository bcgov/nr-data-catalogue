FROM bitnami/postgresql:15.6.0
USER postgres
WORKDIR /docker-entrypoint-initdb.d
COPY postgres-script.sql .
# RUN chmod -R 777 /var/lib/postgresql/data
# docker run -e POSTGRESQL_PASSWORD=password -u 999999:0 custom-postgresql:v1