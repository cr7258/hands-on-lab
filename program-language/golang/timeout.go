package main

import (
	"context"
	"fmt"
	"time"
)

/**
* @description 控制函数超时时间
* @author chengzw
* @since 2024/10/14
 */
// 模拟一个长时间运行的任务
func longRunningTask(resultChan chan<- string) {
	fmt.Println("Task is running")
	time.Sleep(1 * time.Second)
	resultChan <- "Task is completed"
}

func main() {
	resultChan := make(chan string, 1)

	// 设置超时为2秒
	ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
	defer cancel() // 保证资源被释放

	// 启动一个 goroutine 执行任务
	go longRunningTask(resultChan)

	// 使用 select 等待任务完成或超时
	select {
	case result := <-resultChan:
		fmt.Println(result)
	case <-ctx.Done():
		fmt.Println("Timeout: Task took too long")
	}
}
