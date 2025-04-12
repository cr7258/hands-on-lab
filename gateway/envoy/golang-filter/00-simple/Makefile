.PHONY: build run
build:
	docker run --rm -v `pwd`:/go/src/go-filter -w /go/src/go-filter \
		golang:1.20 \
		go build -v -o libgolang.so -buildmode=c-shared .

run:
	docker run --rm -v `pwd`/envoy.yaml:/etc/envoy/envoy.yaml \
		-v `pwd`/libgolang.so:/etc/envoy/libgolang.so \
		-p 10000:10000 \
		envoyproxy/envoy:contrib-dev \
		envoy -c /etc/envoy/envoy.yaml