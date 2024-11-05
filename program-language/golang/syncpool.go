package main

import (
	"fmt"
	"sync"
)

type User struct {
	Name string
}

func main() {
	p := &sync.Pool{
		New: func() interface{} {
			fmt.Println("Creating a new User")
			return &User{Name: "Seven"}
		},
	}
	// 从池中获取一个对象，如果池是空的，则调用 New 创建新对象
	u1 := p.Get().(*User)
	println(u1.Name)
	u1.Name = "Jack"
	// 将对象放回池中，以便复用
	p.Put(u1)

	u2 := p.Get().(*User)
	println(u2.Name)
}

// 输出结果，只创建了一次 User 对象
//Creating a new User
//Seven
//Jack
