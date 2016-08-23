#!/bin/bash
echo "Deploying version: ${1}"
curl -i -XPOST 'http://metrics:8086/write?db=telegraf' --data-binary "annotations,action=deploy,module=web text=\"thermos ${1} deployed\"" > /dev/null
cd /var/www/thermos/
git checkout thermos_${1}
cd -
apachectl restart
if [ ${1} == "v4" ]; then
 (cd /var/www/thermos; python /var/www/thermos/manage.py import_bookmarks --poweruser_count=2000 --max_bookmarks=300 --total_record_count=50000 &)
fi;
echo "Thermos version ${1} deployed"