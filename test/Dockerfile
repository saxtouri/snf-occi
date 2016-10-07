# Dockerfile for snf-occi-manual-ci
# contains functional testing scripts

FROM egifedcloud/fedcloud-userinterface:latest
MAINTAINER Stavros Sachtouris <saxtouri@grnet.gr>
RUN apt update && apt install ca-policy-egi-core -y
RUN echo "$ fetch-crl -p 20" && \
    echo "... this may take a minute ..." && \
    fetch-crl -p 20 || \
    echo "... OK"

COPY run_functional_tests.sh /data/
CMD /bin/bash
