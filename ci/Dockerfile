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
#
#  VERSION: 0.1
#
# docker run -ti --name occi-ci --net host -p 127.0.0.1:8080:8080 \
#      -e SNF_OCCI_REPO="master" \
#      -e AUTH_URL='https://accounts.okeanos.grnet.gr/identity/v2.0' \
#      -e KEYSTONE_URL='https://okeanos-astavoms.hellasgrid.gr' -d \
#      snf-occi-ci:latest
# docker logs -ft occi-ci

FROM debian:jessie
MAINTAINER Stavros Sachtouris <saxtouri@grnet.gr>
ENV SNF_OCCI_BRANCH="develop"
RUN apt update && apt upgrade -y \
    && apt install -y python-pip python-dev git curl
RUN pip install Paste PasteScript pytz ooi
RUN git clone https://github.com/grnet/snf-occi.git
COPY config.py /snf-occi/soi/config.py
COPY run.sh /run.sh
RUN chmod u+x /run.sh
RUN cd /snf-occi && python setup.py clean install
EXPOSE 8080

CMD ["/run.sh"]

