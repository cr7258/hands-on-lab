## Create the clusters

After the clusters start, verify the names of each:

```bash
curl -XGET -u 'admin:Tg9!eXr2@LmQ58z#' -k 'https://localhost:9201'

# Response
{
  "cluster_name" : "leader-cluster",
  ...
}

curl -XGET -u 'admin:Tg9!eXr2@LmQ58z#' -k 'https://localhost:9200'

# Response
{
  "cluster_name" : "follower-cluster",
  ...
}
```

For this example, use port 9201 (replication-node1) as the leader and port 9200 (replication-node2) as the follower cluster.

To get the IP address for the leader cluster, first identify its container ID:

```bash
docker ps
CONTAINER ID   IMAGE                                COMMAND                  CREATED         STATUS         PORTS                                                                                                          NAMES
92059a83b5e5   opensearchproject/opensearch:3.1.0   "./opensearch-docker…"   2 minutes ago   Up 2 minutes   0.0.0.0:9200->9200/tcp, [::]:9200->9200/tcp, 9300/tcp, 0.0.0.0:9600->9600/tcp, [::]:9600->9600/tcp, 9650/tcp   replication-node2
acc03814e9d5   opensearchproject/opensearch:3.1.0   "./opensearch-docker…"   2 minutes ago   Up 2 minutes   9300/tcp, 9650/tcp, 0.0.0.0:9201->9200/tcp, [::]:9201->9200/tcp, 0.0.0.0:9700->9600/tcp, [::]:9700->9600/tcp   replication-node1
```

Then get that container’s IP address:

```bash
docker inspect --format='{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' acc03814e9d5

# Response
192.168.117.3
```

## Set up a cross-cluster connection

Cross-cluster replication follows a “pull” model, so most changes occur on the follower cluster, not the leader cluster.

Set the follower cluster to connect to the leader cluster:

```bash
curl -XPUT -k -H 'Content-Type: application/json' -u 'admin:Tg9!eXr2@LmQ58z#' 'https://localhost:9200/_cluster/settings?pretty' -d '
{
  "persistent": {
    "cluster": {
      "remote": {
        "my-connection-alias": {
          "seeds": ["192.168.117.3:9300"]
        }
      }
    }
  }
}'
```

## Get started with auto-follow

```bash
curl -XPOST -k -H 'Content-Type: application/json' -u 'admin:Tg9!eXr2@LmQ58z#' 'https://localhost:9200/_plugins/_replication/_autofollow?pretty' -d '
{
   "leader_alias" : "my-connection-alias",
   "name": "my-replication-rule",
   "pattern": "movies*",
   "use_roles":{
      "leader_cluster_role": "all_access",
      "follower_cluster_role": "all_access"
   }
}'
```

## Test the replication

To test the rule, create a matching index on the leader cluster:

```bash
curl -XPUT -k -H 'Content-Type: application/json' -u 'admin:Tg9!eXr2@LmQ58z#' 'https://localhost:9201/movies-0001?pretty'
```

And confirm its replica shows up on the follower cluster:

```bash
curl -XGET -u 'admin:Tg9!eXr2@LmQ58z#' -k 'https://localhost:9200/_cat/indices?v'
```

## Retrieve replication rules

```bash
curl -XGET -u 'admin:Tg9!eXr2@LmQ58z#' -k 'https://localhost:9200/_plugins/_replication/autofollow_stats'

# Response
{
  "num_success_start_replication" : 1,
  "num_failed_start_replication" : 0,
  "num_failed_leader_calls" : 0,
  "failed_indices" : [ ],
  "autofollow_stats" : [
    {
      "name" : "my-replication-rule",
      "pattern" : "movies*",
      "num_success_start_replication" : 1,
      "num_failed_start_replication" : 0,
      "num_failed_leader_calls" : 0,
      "failed_indices" : [ ],
      "last_execution_time" : 1751614455391
    }
  ]
}
```
