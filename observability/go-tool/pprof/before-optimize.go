package main

import (
	"bytes"
	"log"
	"math/rand"
	"net/http"
	_ "net/http/pprof" // 开启 pprof
	"time"
)

// 换成一个随机字符串并返回对应的缓冲区
func genRandomBytes() *bytes.Buffer {
	var buff bytes.Buffer
	for i := 1; i < 10000; i++ {
		buff.Write([]byte{'0' + byte(rand.Intn(10))})
	}
	return &buff
}

func main() {
	go func() {
		for {
			// 循环调用生成字符串方法，模拟 CPU 负载
			for i := 0; i < 1000; i++ {
				_ = genRandomBytes()
			}
			time.Sleep(time.Second)
		}
	}()

	// 程序绑定到 6060 端口
	// pprof 结果也必须通过该接口获取
	log.Fatal(http.ListenAndServe("127.0.0.1:6060", nil))
}
