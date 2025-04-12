package main

import (
	"crypto/md5"
	"encoding/hex"

	"github.com/envoyproxy/envoy/contrib/golang/common/go/api"
)

type filter struct {
	api.PassThroughStreamFilter
	callbacks api.FilterCallbackHandler
}

const secretKey = "secret"

func verify(header api.RequestHeaderMap) (bool, string) {
	token, ok := header.Get("token")
	if !ok {
		return false, "missing token"
	}

	path, _ := header.Get(":path")
	hash := md5.Sum([]byte(path + secretKey))
	if hex.EncodeToString(hash[:]) != token {
		return false, "invalid token"
	}
	return true, ""
}

func (f *filter) DecodeHeaders(header api.RequestHeaderMap, endStream bool) api.StatusType {
	if ok, msg := verify(header); !ok {
		f.callbacks.DecoderFilterCallbacks().SendLocalReply(403, msg, nil, 0, "")
		return api.LocalReply
	}
	return api.Continue
}
