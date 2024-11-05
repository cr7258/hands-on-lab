package main

import (
	"fmt"
	"sync"
	"time"
)

/**
* @description 交替打印数字字母
* @author chengzw
* @since 2024/10/24
 */

func main() {
	num := make(chan struct{})
	letter := make(chan struct{})
	wg := sync.WaitGroup{}
	wg.Add(1)

	go func() {
		i := 1
		for {
			select {
			case <-num:
				fmt.Print(i)
				i++
				time.Sleep(time.Millisecond * 200)
				letter <- struct{}{}
			}
		}
	}()

	go func() {
		j := 'a'
		for {
			select {
			case <-letter:
				fmt.Print(string(j))
				if j == 'z' {
					wg.Done()
				}
				j++
				time.Sleep(time.Millisecond * 200)
				num <- struct{}{}
			}
		}
	}()
	// 先打印数字
	num <- struct{}{}
	wg.Wait()
}
