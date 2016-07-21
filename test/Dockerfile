# Dockerfile for snf-occi-manual-ci
# contains functional testing scripts

FROM egifedcloud/fedcloud-userinterface:latest
MAINTAINER Stavros Sachtouris <saxtouri@grnet.gr>
RUN fetch-crl -p 20 | echo "Failed to fetch-crl -p 20"

COPY run_functional_tests.sh /data/
CMD /bin/bash
