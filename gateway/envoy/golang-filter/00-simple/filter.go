package main

import (
	"fmt"
	"strconv"

	"github.com/envoyproxy/envoy/contrib/golang/common/go/api"
)

var UpdateUpstreamBody = "upstream response body updated by the simple plugin"

// The callbacks in the filter, like `DecodeHeaders`, can be implemented on demand.
// Because api.PassThroughStreamFilter provides a default implementation.
type filter struct {
	api.PassThroughStreamFilter

	callbacks api.FilterCallbackHandler
	path      string
	config    *config
}

func (f *filter) sendLocalReplyInternal() api.StatusType {
	body := fmt.Sprintf("%s, path: %s\r\n", f.config.echoBody, f.path)
	f.callbacks.DecoderFilterCallbacks().SendLocalReply(200, body, nil, 0, "")
	// Remember to return LocalReply when the request is replied locally
	return api.LocalReply
}

// Callbacks which are called in request path
// The endStream is true if the request doesn't have body
func (f *filter) DecodeHeaders(header api.RequestHeaderMap, endStream bool) api.StatusType {
	f.path, _ = header.Get(":path")
	api.LogDebugf("get path %s", f.path)

	if f.path == "/localreply_by_config" {
		return f.sendLocalReplyInternal()
	}
	return api.Continue
	/*
		// If the code is time-consuming, to avoid blocking the Envoy,
		// we need to run the code in a background goroutine
		// and suspend & resume the filter
		go func() {
			defer f.callbacks.DecoderFilterCallbacks().RecoverPanic()
			// do time-consuming jobs

			// resume the filter
			f.callbacks.DecoderFilterCallbacks().Continue(status)
		}()

		// suspend the filter
		return api.Running
	*/
}

// Callbacks which are called in response path
// The endStream is true if the response doesn't have body
func (f *filter) EncodeHeaders(header api.ResponseHeaderMap, endStream bool) api.StatusType {
	if f.path == "/update_upstream_response" {
		header.Set("Content-Length", strconv.Itoa(len(UpdateUpstreamBody)))
	}
	header.Set("Rsp-Header-From-Go", "bar-test")
	// support suspending & resuming the filter in a background goroutine
	return api.Continue
}

// EncodeData might be called multiple times during handling the response body.
// The endStream is true when handling the last piece of the body.
func (f *filter) EncodeData(buffer api.BufferInstance, endStream bool) api.StatusType {
	if f.path == "/update_upstream_response" {
		if endStream {
			buffer.SetString(UpdateUpstreamBody)
		} else {
			buffer.Reset()
		}
	}
	// support suspending & resuming the filter in a background goroutine
	return api.Continue
}
