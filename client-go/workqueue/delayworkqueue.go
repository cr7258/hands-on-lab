package main

import (
	"fmt"
	"sync"
	"time"

	"k8s.io/client-go/util/workqueue"
)

func main() {
	// 创建一个新的 DelayingQueue
	queue := workqueue.NewDelayingQueue()

	// 用于等待所有 worker 完成的 WaitGroup
	var wg sync.WaitGroup

	// 启动 3 个 worker goroutine 来处理任务
	for i := 1; i <= 3; i++ {
		wg.Add(1)
		go worker(i, queue, &wg)
	}

	// 添加一些任务到队列，有些是立即执行，有些是延迟执行
	for i := 1; i <= 15; i++ {
		task := fmt.Sprintf("Task %d", i)
		if i%3 == 0 {
			// 每 3 个任务，添加一个延迟 5 秒的任务
			fmt.Printf("Adding delayed task: %s\n", task)
			queue.AddAfter(task, 5*time.Second)
		} else {
			fmt.Printf("Adding immediate task: %s\n", task)
			queue.Add(task)
		}
	}

	// 等待足够长的时间，确保所有任务（包括延迟任务）都被处理
	time.Sleep(10 * time.Second)

	// 关闭队列
	queue.ShutDown()

	// 等待所有 worker 完成
	wg.Wait()

	fmt.Println("All tasks have been processed")
}

func worker(id int, queue workqueue.DelayingInterface, wg *sync.WaitGroup) {
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

// 输出结果，3 的倍数的 task 是延迟执行的
//Adding immediate task: Task 1
//Adding immediate task: Task 2
//Adding delayed task: Task 3
//Adding immediate task: Task 4
//Adding immediate task: Task 5
//Adding delayed task: Task 6
//Adding immediate task: Task 7
//Adding immediate task: Task 8
//Adding delayed task: Task 9
//Adding immediate task: Task 10
//Adding immediate task: Task 11
//Adding delayed task: Task 12
//Adding immediate task: Task 13
//Adding immediate task: Task 14
//Adding delayed task: Task 15
//Worker 3: Processing item: Task 2
//Worker 1: Processing item: Task 1
//Worker 2: Processing item: Task 4
//Worker 2: Processing item: Task 5
//Worker 3: Processing item: Task 7
//Worker 1: Processing item: Task 8
//Worker 3: Processing item: Task 10
//Worker 1: Processing item: Task 11
//Worker 2: Processing item: Task 13
//Worker 3: Processing item: Task 14
//Worker 2: Processing item: Task 3
//Worker 1: Processing item: Task 6
//Worker 3: Processing item: Task 9
//Worker 3: Processing item: Task 12
//Worker 2: Processing item: Task 15
//Worker 2: Shutting down
//Worker 3: Shutting down
//Worker 1: Shutting down
//All tasks have been processed
