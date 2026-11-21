import mysql.connector
from flask import current_app
def conn():
 c=current_app.config
 return mysql.connector.connect(host=c["MYSQL_HOST"],port=c["MYSQL_PORT"],user=c["MYSQL_USER"],password=c["MYSQL_PASSWORD"],database=c["MYSQL_DATABASE"])
def run(sql,params=(),many=False):
 db=conn(); cur=db.cursor(dictionary=True); cur.execute(sql,params)
 result=cur.fetchall() if many else cur.fetchone()
 db.commit(); cur.close(); db.close()
 return result
