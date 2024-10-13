package main

import (
	"fmt"
	"golang.org/x/time/rate"
	"k8s.io/client-go/util/workqueue"
	"sync"
	"time"
)

func main() {
	// 我们定义了一个复合的限速器，它结合了两种限速策略：
	// 1. 使用指数退避的限速器，用于限制每个任务的重试频率
	// 2. 使用令牌桶算法限制总体速率，这里设置为每秒 5 个请求。
	// MaxOfRateLimiter 会遍历所有的 RateLimiter 示例，使用 When() 计算等待间隔，然后选择最大的等待间隔。
	limiter := workqueue.NewMaxOfRateLimiter(
		workqueue.NewItemExponentialFailureRateLimiter(time.Millisecond, 1000*time.Millisecond),
		&workqueue.BucketRateLimiter{Limiter: rate.NewLimiter(rate.Limit(5), 5)},
	)

	// 创建一个新的 RateLimitingQueue
	queue := workqueue.NewRateLimitingQueue(limiter)

	// 用于等待所有 worker 完成的 WaitGroup
	var wg sync.WaitGroup

	// 启动 3 个 worker goroutine 来处理任务
	for i := 1; i <= 3; i++ {
		wg.Add(1)
		go worker(i, queue, &wg)
	}

	// 添加一些任务到队列
	for i := 1; i <= 20; i++ {
		task := fmt.Sprintf("Task %d", i)
		fmt.Printf("Adding task: %s\n", task)
		queue.Add(task)
	}

	// 等待足够长的时间，确保所有任务都被处理
	time.Sleep(30 * time.Second)

	// 关闭队列
	queue.ShutDown()

	// 等待所有 worker 完成
	wg.Wait()

	fmt.Println("All tasks have been processed")
}

func worker(id int, queue workqueue.RateLimitingInterface, wg *sync.WaitGroup) {
	defer wg.Done()
	for {
		// 从队列中获取一个任务
		item, shutdown := queue.Get()
		if shutdown {
			fmt.Printf("Worker %d: Shutting down\n", id)
			return
		}

		func() {
			defer queue.Done(item)

			// 处理任务
			fmt.Printf("Worker %d: Processing item: %v\n", id, item)

			// 模拟随机失败
			if time.Now().UnixNano()%2 == 0 {
				fmt.Printf("Worker %d: Failed processing item: %v\n", id, item)
				queue.AddRateLimited(item) // 重新加入队列，会被限速
				return
			}

			// 处理成功，忘记该 item 的限速历史
			queue.Forget(item)
		}()
	}
}
