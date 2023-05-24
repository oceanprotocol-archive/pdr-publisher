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
ENV OPF_DEPLOYER_PRIVATE_KEY="0xc594c6e5def4bab63ac29eed19a134c130388f74f019bc74b8f4389df2837a58"
ENV PREDICTOOR_PRIVATE_KEY="0xef4b441145c1d0f3b4bc6d61d29f5c6e502359481152f869247c7a4244d45209"
ENV TRADER_PRIVATE_KEY="0x8467415bb2ba7c91084d932276214b11a3dd9bdb2930fefa194b666dd8020b99"
ENV WAIT_FOR_CONTRACTS=false
ENTRYPOINT ["/pdr-publisher/docker-entrypoint.sh"]
