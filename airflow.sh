#!/bin/bash
export AMP_API_HOST="${1:-http://172.17.0.1:8082}"
export AMP_DB_HOST="${2:-172.17.0.1}"
export AMP_DB_NAME="${3:-amp}"
export AMP_DB_USER="${4:-postgres}"
export AMP_DB_PASSWORD="${5:-postgres}"
export AMP_DB_PORT="${6:-5432}"
export REDIS_HOST="${7:-localhost}"
CREATE_NETWORK="${8:-true}"
NETWORK_NAME="${9:-traefik_default}"
BACKEND_NETWORK_NAME="${10:-backend}"
export AIRFLOW_IMAGE=apache/airflow:slim-latest
export AIRFLOW_HOST=airflow.stg.ampsite.net

echo "AIRFLOW_HOST is set to: $AIRFLOW_HOST"
echo "AIRFLOW_IMAGE is set to: $AIRFLOW_IMAGE"
echo "AMP_API_HOST  is set to: $AMP_API_HOST"
echo "AMP_DB_HOST  is set to: $AMP_DB_HOST"
echo "AMP_DB_NAME  is set to: $AMP_DB_NAME"
echo "AMP_DB_USER  is set to: $AMP_DB_USER"
echo "AMP_DB_PASSWORD  is set to: $AMP_DB_PASSWORD"
echo "AMP_DB_PORT  is set to: $AMP_DB_PORT"
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
