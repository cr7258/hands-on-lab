package main

import (
	"crypto/md5"
	"encoding/hex"

	"github.com/envoyproxy/envoy/contrib/golang/filters/http/source/go/pkg/api"
)

type filter struct {
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
		f.callbacks.SendLocalReply(403, msg, map[string]string{}, 0, "bad-request")
		return api.LocalReply
	}
	return api.Continue
}

func (f *filter) DecodeData(buffer api.BufferInstance, endStream bool) api.StatusType {
	return api.Continue
}

func (f *filter) DecodeTrailers(trailers api.RequestTrailerMap) api.StatusType {
	return api.Continue
}

func (f *filter) EncodeHeaders(header api.ResponseHeaderMap, endStream bool) api.StatusType {
	return api.Continue
}

func (f *filter) EncodeData(buffer api.BufferInstance, endStream bool) api.StatusType {
	return api.Continue
}

func (f *filter) EncodeTrailers(trailers api.ResponseTrailerMap) api.StatusType {
	return api.Continue
}

func (f *filter) OnDestroy(reason api.DestroyReason) {
}

func main() {
}
