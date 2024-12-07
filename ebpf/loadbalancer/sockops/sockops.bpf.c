//go:build ignore

#include "common.h"
#include "sockops.h"

SEC("sockops")
int bpf_sockmap(struct bpf_sock_ops *skops)
{
	/* skip if the packet is not ipv4 */
	if (skops->family != AF_INET) {
		return BPF_OK;
	}

	/* skip if it is not established op */
	if (skops->op != BPF_SOCK_OPS_PASSIVE_ESTABLISHED_CB
	    && skops->op != BPF_SOCK_OPS_ACTIVE_ESTABLISHED_CB) {
		return BPF_OK;
	}

	struct sock_key key = {
		.dip = skops->remote_ip4,
		.sip = skops->local_ip4,
		/* convert to network byte order */
		.sport = bpf_htonl(skops->local_port),
		.dport = skops->remote_port,
		.family = skops->family,
	};

	bpf_sock_hash_update(skops, &sock_ops_map, &key, BPF_NOEXIST);
	return BPF_OK;
}

SEC("sk_msg")
int bpf_redir(struct sk_msg_md *msg)
{
	struct sock_key key = {
		.sip = msg->remote_ip4,
		.dip = msg->local_ip4,
		.dport = bpf_htonl(msg->local_port),	// convert to network byte order
		.sport = msg->remote_port,
		.family = msg->family,
	};

	bpf_msg_redirect_hash(msg, &sock_ops_map, &key, BPF_F_INGRESS);
	return SK_PASS;
}

char LICENSE[] SEC("license") = "Dual BSD/GPL";
