package main

import (
	"k8s.io/client-go/tools/cache"
	"k8s.io/klog/v2"
)

type pod struct {
	Name  string
	Value float64
}

func newPod(name string, v float64) pod {
	return pod{
		Name:  name,
		Value: v,
	}
}

func podKeyFunc(obj interface{}) (string, error) {
	return obj.(pod).Name, nil
}

// 运行程序输出结果如下，只可以取到最新的对象 pod1，旧值需要去 Indexer 里取
// I1012 12:03:54.863048    1437 deltafifo.go:38] delta type: Added, delta object: {pod1 %!s(float64=1)}
// I1012 12:03:54.863415    1437 deltafifo.go:38] delta type: Updated, delta object: {pod1 %!s(float64=1.1)}
// I1012 12:03:54.863429    1437 deltafifo.go:38] delta type: Deleted, delta object: {pod1 %!s(float64=1.1)}

func main() {
	// 可以自定义 KeyFunc，默认使用 MetaNamespaceKeyFunc 生成的结果（<namespace>/<name>）作为 DeltaFIFO 的 key
	df := cache.NewDeltaFIFOWithOptions(cache.DeltaFIFOOptions{KeyFunction: podKeyFunc})
	pod1 := newPod("pod1", 1)
	pod2 := newPod("pod2", 2)
	pod3 := newPod("pod3", 3)
	df.Add(pod1)
	df.Add(pod2)
	df.Add(pod3)
	pod1.Value = 1.1
	df.Update(pod1)
	df.Delete(pod1)

	df.Pop(func(obj interface{}, isInInitialList bool) error {
		for _, delta := range obj.(cache.Deltas) {
			klog.Infof("delta type: %s, delta object: %s", delta.Type, delta.Object)
			//switch delta.Type {
			//case cache.Added:
			//	klog.Infof("pod created: %s", delta.Object.(pod).Name)
			//case cache.Updated:
			//	klog.Infof("pod updated: %s", delta.Object.(pod).Name)
			//case cache.Deleted:
			//	klog.Infof("pod deleted: %s", delta.Object.(pod).Name)
			//}
		}
		return nil
	})
}
