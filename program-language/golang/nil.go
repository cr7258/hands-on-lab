package main

import "fmt"

/**
* @description 明明是 nil 却 != nil 的问题
* @author chengzw
* @since 2024/10/14
 */

func main() {
	var a *struct{}
	var b interface{} = a

	if b == nil {
		fmt.Println("b is nil")
	} else {
		fmt.Println("b is not nil")
	}
}

// 打印结果
//b is not nil
