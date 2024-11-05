package main

import (
	"fmt"
	"sync"
)

/**
* @description 两个 goroutine 并发修改数字，使用 sync.Mutex
* @author chengzw
* @since 2024/10/24
 */

func main() {
	num := 0
	wg := sync.WaitGroup{}
	mu := sync.Mutex{}
	wg.Add(2)

	go func() {
		defer wg.Done()
		for i := 0; i < 1000; i++ {
			mu.Lock()
			num++
			mu.Unlock()
		}
	}()

	go func() {
		defer wg.Done()
		for j := 0; j < 1000; j++ {
			mu.Lock()
			num++
			mu.Unlock()
		}
	}()

	wg.Wait()
	fmt.Println(num)
}
