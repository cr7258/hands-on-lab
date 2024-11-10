package design_pattern

import "sync"

/**
* @description 单例模式
* @author chengzw
* @since 2024/11/5
 */

type Singleton struct {
}

var singleton *Singleton
var once sync.Once

func GetInstance() *Singleton {
	once.Do(func() {
		singleton = &Singleton{}
	})
	return singleton
}
