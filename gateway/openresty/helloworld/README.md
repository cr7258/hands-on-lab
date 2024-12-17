## 启动 OpenResty

```bash
make run
```

## 请求 OpenResty

```bash
$ curl -i 127.0.0.1:8080
HTTP/1.1 200 OK
Server: openresty/1.13.6.2
Content-Type: text/plain
Transfer-Encoding: chunked
Connection: keep-alive

hello, world
```

## 停止 OpenResty

```bash
make stop
```