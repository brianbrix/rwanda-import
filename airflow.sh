#!/bin/bash
CREATE_NETWORK="${1:-true}"
NETWORK_NAME="${2:-traefik_default}"
BACKEND_NETWORK_NAME="${3:-backend}"
export AIRFLOW_IMAGE=airflow:custom
export AIRFLOW_HOST=airflow.stg.ampsite.net


echo "REDIS_HOST  is set to: $REDIS_HOST"
echo "CREATE_NETWORK  is set to: $CREATE_NETWORK"

# ✅ Prepare host log directory
echo "Creating /var/logs/airflow if not exists and setting permissions..."
sudo mkdir -p /var/logs/airflow/{scheduler,webserver}
sudo chown -R 50000:0 /var/logs/airflow
sudo chmod -R 755 /var/logs/airflow

# ✅ Ensure Docker networks exist
if [[  $CREATE_NETWORK == "true" ]]; then
    if ! docker network inspect "$NETWORK_NAME" >/dev/null 2>&1; then
        echo "Creating network: $NETWORK_NAME"
        docker network create "$NETWORK_NAME"
    else
        echo "Network $NETWORK_NAME already exists"
    fi
else
    echo "Skipping network creation as CREATE_NETWORK is not set to true"
fi

# ✅ Ensure DB container is connected to backend network
if docker inspect "$AMP_DB_HOST" | grep -q "\"$BACKEND_NETWORK_NAME\":"; then
  echo "Container '$AMP_DB_HOST' is already connected to the '$BACKEND_NETWORK_NAME' network."
else
  echo "Connecting '$AMP_DB_HOST' to '$BACKEND_NETWORK_NAME'..."
  docker network connect "$BACKEND_NETWORK_NAME" "$AMP_DB_HOST"
  echo "Done."
fi

# ✅ Build Airflow image
echo "Building airflow image"
docker build -t ${AIRFLOW_IMAGE} --no-cache .

# ✅ Create .env file from template
cat env_template | sed "s|#IMAGE|${AIRFLOW_IMAGE}|g" \
                 | sed "s|#AIRFLOWHOST|${AIRFLOW_HOST}|g" \
                 | sed "s|#AMPAPIHOST|${AMP_API_HOST}|g" \
                 | sed "s|#AMPDBHOST|${AMP_DB_HOST}|g" \
                 | sed "s|#AMPDBNAME|${AMP_DB_NAME}|g" \
                 | sed "s|#AMPDBUSER|${AMP_DB_USER}|g" \
                 | sed "s|#AMPDBPASSWORD|${AMP_DB_PASSWORD}|g" \
                 | sed "s|#AMPDBPORT|${AMP_DB_PORT}|g" \
                 | sed "s|#REDISHOST|${REDIS_HOST}|g" > .env

# ✅ Start containers
echo "Running docker-compose"
docker-compose up -d

echo "Finished docker-compose"
