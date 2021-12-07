#!/usr/bin/env bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
YML_DIR=$(realpath "$SCRIPT_DIR/../docker-compose")

pushd ${YML_DIR}

app_id=$(date +%s)
docker-compose -f app.yml -p ${app_id} up --build --abort-on-container-exit --exit-code-from todo-app
exit_code=$?
docker-compose -f app.yml -p ${app_id} down --rmi local

popd

exit ${exit_code}
