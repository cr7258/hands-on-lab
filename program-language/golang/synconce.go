package main

import (
	"fmt"
	"sync"
)

/**
* @description sync.Once 是 Go 标准库提供的使函数只执行一次的实现，常应用于单例模式，例如初始化配置、保持数据库连接等
* @author chengzw
* @since 2024/10/24
 */

// Config 是一个模拟的配置结构体
type Config struct {
	Value string
}

// 定义一个全局的 Config 实例和 sync.Once 实例
var (
	config Config
	once   sync.Once
)

// 初始化配置的函数
func initConfig() {
	config = Config{Value: "Initialized Value"}
	fmt.Println("Config initialized.")
}

// 获取配置的函数，确保配置只初始化一次
func getConfig() Config {
	once.Do(initConfig) // 确保 initConfig 只被调用一次
	return config
}

func main() {
	var wg sync.WaitGroup

	// 启动多个 goroutine，尝试获取配置
	for i := 0; i < 5; i++ {
		wg.Add(1)
		go func(id int) {
			defer wg.Done()
			cfg := getConfig()
			fmt.Printf("Goroutine %d: %s\n", id, cfg.Value)
		}(i)
	}

	wg.Wait() // 等待所有 goroutine 完成
}
