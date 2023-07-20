##
## Copyright 2023 Ocean Protocol Foundation
## SPDX-License-Identifier: Apache-2.0
##
FROM ubuntu:20.04
LABEL maintainer="Ocean Protocol <devops@oceanprotocol.com>"
RUN apt-get update && \
   apt-get install --no-install-recommends -y \
   gcc \
   python3.8 \
   python3-pip \
   python3.8-dev \
   gettext-base \
   autoconf \
   automake \
   build-essential \
   libffi-dev \
   libtool \
   pkg-config \
   git


COPY . /pdr-publisher
WORKDIR /pdr-publisher
RUN git clone https://github.com/oceanprotocol/ocean.py
WORKDIR /pdr-publisher/ocean.py
RUN git checkout predictoor-with-barge
RUN cp /pdr-publisher/publish.py /pdr-publisher/ocean.py/
RUN pip install -r requirements_dev.txt
RUN mkdir -p /root/.brownie/
RUN cp /pdr-publisher/network-config.yaml /root/.brownie/
ENV ADDRESS_FILE="${HOME}/.ocean/ocean-contracts/artifacts/address.json"
ENV WAIT_FOR_CONTRACTS=false
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["/pdr-publisher/docker-entrypoint.sh"]
