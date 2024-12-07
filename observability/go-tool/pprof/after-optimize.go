package main

import (
	"log"
	"net/http"
	_ "net/http/pprof" // 开启 pprof
	"time"
)

func main() {
	go func() {
		for {
			time.Sleep(time.Second)
		}
	}()

	// 程序绑定到 6060 端口
	// pprof 结果也必须通过该接口获取
	log.Fatal(http.ListenAndServe("127.0.0.1:6060", nil))
}
