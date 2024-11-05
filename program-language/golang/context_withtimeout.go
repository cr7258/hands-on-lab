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
	// 设置超时时间
	ctx, cancel := context.WithTimeout(context.Background(), 1*time.Second)
	defer cancel() // 确保在 main 退出时调用 cancel

	for i := 0; i < 5; i++ {
		go worker(ctx, i)
	}

	// 等待一段时间以查看结果
	time.Sleep(3 * time.Second)
}
