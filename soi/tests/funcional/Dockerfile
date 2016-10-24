# Copyright (C) 2016 GRNET S.A.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

# Dockerfile for snf-occi-manual-ci
# contains functional testing scripts
#
# VERSION   0.3.2

FROM egifedcloud/fedcloud-userinterface:latest
MAINTAINER Stavros Sachtouris <saxtouri@grnet.gr>
RUN apt update && apt install ca-policy-egi-core curl openssh-client -y

COPY run_functional_tests.sh /data/
COPY run_curl_tests.sh /data/
COPY run.sh /data/
CMD ["/bin/bash", "/data/run.sh"]
