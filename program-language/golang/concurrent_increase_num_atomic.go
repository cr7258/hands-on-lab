package main

import (
	"fmt"
	"sync"
	"sync/atomic"
)

/**
* @description 两个 goroutine 并发修改数字，使用 sync/atomic
* @author chengzw
* @since 2024/10/24
 */

func main() {
	var num int64
	wg := sync.WaitGroup{}
	wg.Add(2)

	go func() {
		defer wg.Done()
		for i := 0; i < 1000; i++ {
			atomic.AddInt64(&num, 1) // 原子操作
		}
	}()

	go func() {
		defer wg.Done()
		for i := 0; i < 1000; i++ {
			atomic.AddInt64(&num, 1)
		}
	}()

	wg.Wait()
	fmt.Println(num)
}
