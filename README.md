The safest way to run the stack is to run docker compose:
```
docker-compose up -d --scale ts3-api=3
```

You also have to fill configuration.py file:
```
ip = "" #string - ip or hostname
port = 10011 #int - port
client_login_name = ''
client_login_password = ''
client_nickname = ''
sid = 1 #int - server id
api_user = ''
api_password = ''
```


To test the api:
```
$ curl -u api_user:api_password localhost:9652/channels
```

