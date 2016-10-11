CMD1="fetch-crl -p 20"
echo $CMD1
$(echo $CMD1)

CMD2="voms-proxy-init -voms fedcloud.egi.eu --rfc"
echo $CMD2
$(echo $CMD2)

/bin/bash