import redis
conn = redis.Redis(host="localhost", port=6379, db=0)
key_list = conn.keys()
for key in key_list :
    key_delete = conn.delete(key)
    print key_delete
