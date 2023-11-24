## Compiling to Wasm
We will use TinyGo compiler with wasm target(wasi).

```bash
tinygo build -o ./hello.wasm -scheduler=none -target=wasi ./main.go
```

## Running Wasm plugin in envoy

```bash
docker-compose up
```

## Send a request to envoy

```bash
curl http://localhost:10000 -i

# output
curl http://localhost:10000  -i
HTTP/1.1 201 Created
test: seven
content-type: text/plain
hello: proxy
date: Fri, 24 Nov 2023 12:59:09 GMT
server: envoy
transfer-encoding: chunked

hello wasm
```

## Reference

- [Using Wasm in Envoy Proxy - Part 1](https://varunksaini.com/wasm-http-proxy-part-1/)