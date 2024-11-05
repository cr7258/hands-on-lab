package main

import (
	"context"
	"fmt"
	"time"
)

func worker(ctx context.Context, id int) {
	select {
	case <-time.After(2 * time.Second): // 模拟工作
		fmt.Printf("Worker %d finished work\n", id)
	case <-ctx.Done(): // 监听取消信号
		fmt.Printf("Worker %d stopped\n", id)
	}
}

func main() {
	ctx, cancel := context.WithCancel(context.Background())

	for i := 0; i < 5; i++ {
		go worker(ctx, i)
	}

	// 如果小于 2s，worker 会来不及完成工作
	time.Sleep(time.Second * 1)
	// 取消上下文，所有监听 ctx.Done() 的 goroutine 将收到通知
	cancel()
	// 等待一段时间以查看结果
	time.Sleep(3 * time.Second)
}
