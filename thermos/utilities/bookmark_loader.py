import pymysql
from datetime import datetime


st = datetime.now()
commit_count=10000
count=0

with open('/var/www/thermos/utilities/majestic_test.csv') as f:
    next(f)
    conn = pymysql.connect(host='10.162.2.55', port=3306, user='thermos', passwd='thermos', db='thermos')
    cur = conn.cursor()
    for l in f:
        item = l.split(',')
        print '{} {}'.format(item[0],item[2].strip())
        cur.execute("INSERT INTO bookmark2 (url,date,user_id) VALUES (%s,%s,%s)",
                    ('http://{}'.format(item[2].strip()),datetime.now(),'1'))
        count += 1
        if count>commit_count:
            conn.commit()
conn.commit()

finish = datetime.now() - st
print finish