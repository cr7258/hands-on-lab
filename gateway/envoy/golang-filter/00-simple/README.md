# Make a request handled by the Go plugin

The output from the `curl` command below should include the header added by the simple Go plugin.

```bash
$ curl -v localhost:10000 2>&1 | grep rsp-header-from-go
< rsp-header-from-go: bar-test
```

# Make a request handled upstream and updated by the Go plugin

The output from the `curl` command below should include the body that has been updated by the simple Go plugin.

```bash
$ curl localhost:10000/update_upstream_response 2>&1 | grep "updated"
upstream response body updated by the simple plugin
```

# Make a request handled by the Go plugin using custom configuration

The output from the `curl` command below should include the body that contains value of
`prefix_localreply_body` by the simple Go plugin.

```bash
$ curl localhost:10000/localreply_by_config  2>&1 | grep "localreply"
Configured local reply from go, path: /localreply_by_config
```