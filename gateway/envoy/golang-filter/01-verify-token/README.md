```bash
$ curl 'http://localhost:10000/'
missing token

$ curl -s 'http://localhost:10000/' -H 'token: c64319d06364528120a9f96af62ea83d' -I
HTTP/1.1 200 OK
```