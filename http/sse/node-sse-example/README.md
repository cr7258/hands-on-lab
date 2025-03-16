Fix: 请求的端口应该是 3000，而不是 3001。

https://www.digitalocean.com/community/tutorials/nodejs-server-sent-events-build-realtime-app


## 启动 SSE 服务器

```bash
node sse-server/server.js
```

## 启动 SSE 客户端

```bash
cd sse-client
npm start
```

## 添加消息

```bash
curl -X POST \
 -H "Content-Type: application/json" \
 -d '{"info": "Shark teeth are embedded in the gums rather than directly affixed to the jaw, and are constantly replaced throughout life.", "source": "https://en.wikipedia.org/wiki/Shark"}'\
 -s http://localhost:3000/fact
```

浏览器打开 http://localhost:3002，你应该能看到新添加的消息。

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/202503161111912.png)