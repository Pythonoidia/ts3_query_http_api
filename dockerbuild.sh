docker stop ts3-api
docker rm ts3-api
docker build -t ts3-api .
docker run -p 5000:7600 --name ts3-api -d ts3-api
