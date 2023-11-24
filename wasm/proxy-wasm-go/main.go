package main

import (
	"github.com/tetratelabs/proxy-wasm-go-sdk/proxywasm"
	"github.com/tetratelabs/proxy-wasm-go-sdk/proxywasm/types"
)

type vmContext struct {
	types.DefaultVMContext
}

type httpContext struct {
	types.DefaultHttpContext
}

func (*vmContext) NewPluginContext(contextID uint32) types.PluginContext {
	return &pluginContext{}
}

type pluginContext struct {
	types.DefaultPluginContext
}

func (ctx *pluginContext) NewHttpContext(contextID uint32) types.HttpContext {
	return &httpContext{}
}

func main() {
	proxywasm.SetVMContext(&vmContext{})
}

func (ctx *httpContext) OnHttpRequestHeaders(numHeaders int, endOfStream bool) types.Action {
	headers := [][2]string{
		{"test", "seven"},
	}
	proxywasm.SendHttpResponse(201, headers, []byte(" "), -1)
	return types.ActionContinue
}

func (ctx *httpContext) OnHttpResponseHeaders(_ int, _ bool) types.Action {
	proxywasm.LogInfof("OnHttpResponseHeaders")
	// important: Remove Content-Length in order to prevent severs from crashing if we set different body.
	proxywasm.RemoveHttpResponseHeader("content-length")
	proxywasm.AddHttpResponseHeader("hello", "proxy")
	return types.ActionContinue
}

func (ctx *httpContext) OnHttpResponseBody(bodySize int, endOfStream bool) types.Action {
	proxywasm.LogInfo("OnHttpResponseBody")
	proxywasm.ReplaceHttpResponseBody([]byte("hello wasm"))

	return types.ActionContinue
}
