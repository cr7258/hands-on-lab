package main

import (
	"fmt"
	"sync"
	"time"

	"k8s.io/client-go/util/workqueue"
)

// 演示 workqueue 的去重功能
func main() {
	// 创建一个新的 WorkQueue
	queue := workqueue.New()

	// 用于等待所有 worker 完成的 WaitGroup
	var wg sync.WaitGroup

	// 启动 3 个 worker goroutine 来处理任务
	for i := 1; i <= 3; i++ {
		wg.Add(1)
		go worker(i, queue, &wg)
	}

	// 添加一些任务到队列，包括重复的任务
	for i := 1; i <= 10; i++ {
		task := fmt.Sprintf("Task %d", (i-1)%5+1) // This will create tasks 1-5 twice
		fmt.Printf("Adding task: %s\n", task)
		queue.Add(task)
		// 短暂延迟，以便更清楚地观察添加过程
		time.Sleep(100 * time.Millisecond)
	}

	// 等待一段时间，确保所有任务都被添加到队列
	time.Sleep(5 * time.Second)

	// 关闭队列
	queue.ShutDown()

	// 等待所有 worker 完成
	wg.Wait()

	fmt.Println("All tasks have been processed")
}

func worker(id int, queue workqueue.Interface, wg *sync.WaitGroup) {
	defer wg.Done()
	for {
		// 从队列中获取一个任务
		item, shutdown := queue.Get()
		if shutdown {
			fmt.Printf("Worker %d: Shutting down\n", id)
			return
		}

		// 处理任务
		fmt.Printf("Worker %d: Processing item: %v\n", id, item)
		time.Sleep(time.Second) // 模拟处理时间

		// 标记任务已完成
		queue.Done(item)
	}
}

// 输出结果，虽然 Task 4 和 5 在处理之前被添加了两次，但只会被处理一次
//Adding task: Task 1
//Worker 1: Processing item: Task 1
//Adding task: Task 2
//Worker 2: Processing item: Task 2
//Adding task: Task 3
//Worker 3: Processing item: Task 3
//Adding task: Task 4
//Adding task: Task 5
//Adding task: Task 1
//Adding task: Task 2
//Adding task: Task 3
//Adding task: Task 4
//Adding task: Task 5
//Worker 1: Processing item: Task 4
//Worker 2: Processing item: Task 5
//Worker 3: Processing item: Task 1
//Worker 1: Processing item: Task 2
//Worker 2: Processing item: Task 3
//Worker 3: Shutting down
//Worker 1: Shutting down
//Worker 2: Shutting down
//All tasks have been processed
