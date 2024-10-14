package main

import (
	"fmt"
	"sync"
	"time"
)

/**
* @description 通过带缓冲的 channel 来控制协程的并发数量
* @author chengzw
* @since 2024/10/14
 */

func main() {
	var wg sync.WaitGroup
	maxWorkers := 3
	sem := make(chan struct{}, maxWorkers) // 通过带缓冲的 channel 来控制协程的并发数量

	// 启动 10 个协程，但最多只会有 maxWorkers 个协程同时执行
	for i := 0; i < 10; i++ {
		wg.Add(1)
		go worker(i, &wg, sem)
	}

	// 等待所有协程完成
	wg.Wait()
}

func worker(id int, wg *sync.WaitGroup, sem chan struct{}) {
	defer wg.Done()
	sem <- struct{}{} // 获取信号

	defer func() {
		<-sem
	}() // 释放信号

	fmt.Printf("Worker %d is working\n", id)
	time.Sleep(2 * time.Second) // 模拟工作
	fmt.Printf("Worker %d done\n", id)
}

// 输出结果
//Worker 9 is working
//Worker 6 is working
//Worker 4 is working
//Worker 4 done
//Worker 5 is working
//Worker 9 done
//Worker 2 is working
//Worker 6 done
//Worker 0 is working
//Worker 0 done
//Worker 7 is working
//Worker 5 done
//Worker 8 is working
//Worker 2 done
//Worker 3 is working
//Worker 3 done
//Worker 1 is working
//Worker 7 done
//Worker 8 done
//Worker 1 done
