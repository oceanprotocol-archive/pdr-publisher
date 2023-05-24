#!/bin/bash
if [ "${WAIT_FOR_CONTRACTS}" = "true" ]
then
  echo "Waiting for contracts to be ready...."
  while [ ! -f "/root/.ocean/ocean-contracts/artifacts/ready" ]; do
    sleep 2
  done
fi
sleep 10
cd /pdr-publisher/ocean.py/
echo "Starting app..."
python3 -u publish.py
tail -f /dev/null

