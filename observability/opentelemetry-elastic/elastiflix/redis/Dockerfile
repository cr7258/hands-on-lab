# dockerfile for redis with a background process to change the behavior of the redis server
FROM redis:6.2.5-alpine


COPY . .

# use entrypoint.sh to run a background process to change the behavior of the redis server
ENTRYPOINT ["sh", "./entrypoint.sh"]
