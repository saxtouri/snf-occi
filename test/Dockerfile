# Dockerfile for snf-occi-manual-ci
# contains functional testing scripts
#
# VERSION   0.2

FROM egifedcloud/fedcloud-userinterface:latest
MAINTAINER Stavros Sachtouris <saxtouri@grnet.gr>
RUN apt update && apt install ca-policy-egi-core -y

COPY run_functional_tests.sh /data/
COPY run.sh /data/
CMD ["/bin/bash", "/data/run.sh"]
