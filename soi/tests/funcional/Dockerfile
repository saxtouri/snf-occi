# Dockerfile for snf-occi-manual-ci
# contains functional testing scripts
#
# VERSION   0.3.1

FROM egifedcloud/fedcloud-userinterface:latest
MAINTAINER Stavros Sachtouris <saxtouri@grnet.gr>
RUN apt update && apt install ca-policy-egi-core curl -y

COPY run_functional_tests.sh /data/
COPY run_curl_tests.sh /data/
COPY run.sh /data/
CMD ["/bin/bash", "/data/run.sh"]
