package main

import (
	"github.com/envoyproxy/envoy/contrib/golang/common/go/api"
	"github.com/envoyproxy/envoy/contrib/golang/filters/http/source/go/pkg/http"
)

func init() {
	http.RegisterHttpFilterFactoryAndConfigParser("golang-filter-example", filterFactory, http.NullParser)
}

func filterFactory(c interface{}, callbacks api.FilterCallbackHandler) api.StreamFilter {
	return &filter{
		callbacks: callbacks,
	}
}

func main() {}
