#!/bin/bash
if [ "${WAIT_FOR_CONTRACTS}" = "true" ]
then
  echo "Waiting for contracts to be ready...."
  while [ ! -f "/root/.ocean/ocean-contracts/artifacts/ready" ]; do
    sleep 2
  done
fi
cd /pdr-publisher/ocean.py/
echo "Starting app..."
python3 publish.py 2>&1 &
tail -f /dev/null

