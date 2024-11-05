package main

import (
	"fmt"
	"sync"
	"time"
)

/**
* @description sync.Cond 经常用在多个 goroutine 等待，一个 goroutine 通知（事件发生）的场景。
* @author chengzw
* @since 2024/10/24
 */

func read(name string, c *sync.Cond) {
	// 每个 Cond 实例都会关联一个锁 L（互斥锁 *Mutex，或读写锁 *RWMutex），当修改条件或者调用 Wait 方法时，必须加锁。
	c.L.Lock()
	c.Wait()

	fmt.Println(name, "start reading")
	c.L.Unlock()
}

func write(name string, c *sync.Cond) {
	fmt.Println(name, "start writing")
	time.Sleep(time.Second * 1)
	fmt.Println("wakes all")
	c.Broadcast()
}

func main() {
	cond := sync.NewCond(&sync.Mutex{})

	go read("reader1", cond)
	go read("reader2", cond)
	go read("reader3", cond)
	write("writer", cond)

	time.Sleep(time.Second * 3)
}
