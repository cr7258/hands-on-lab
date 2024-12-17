## 启动 OpenResty

```bash
make run
```

## 请求 OpenResty

```bash
echo "set k1 0 900 d1" | nc localhost 11212
echo "get k1" | nc localhost 11212
```

## 停止 OpenResty

```bash
make stop
```