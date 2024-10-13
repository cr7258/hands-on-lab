package main

import (
	"path/filepath"
	"time"

	v1 "k8s.io/api/core/v1"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/apimachinery/pkg/fields"
	"k8s.io/client-go/kubernetes"
	"k8s.io/client-go/tools/cache"
	"k8s.io/client-go/tools/clientcmd"
	"k8s.io/client-go/util/homedir"
	"k8s.io/klog/v2"
)

func main() {
	homedir := homedir.HomeDir()
	config, err := clientcmd.BuildConfigFromFlags("", filepath.Join(homedir, ".kube", "config"))
	if err != nil {
		panic(err)
	}

	clientset, err := kubernetes.NewForConfig(config)
	if err != nil {
		klog.Fatal(err)
	}

	stopCh := make(chan struct{})
	defer close(stopCh)

	// 创建 Pod SharedInformer
	podListWatcher := cache.NewListWatchFromClient(
		clientset.CoreV1().RESTClient(),
		"pods",
		metav1.NamespaceAll,
		fields.Everything(),
	)
	podInformer := cache.NewSharedInformer(podListWatcher, &v1.Pod{}, time.Minute)

	// 创建 Service SharedInformer
	serviceListWatcher := cache.NewListWatchFromClient(
		clientset.CoreV1().RESTClient(),
		"services",
		metav1.NamespaceAll,
		fields.Everything(),
	)
	serviceInformer := cache.NewSharedInformer(serviceListWatcher, &v1.Service{}, time.Minute)

	// 添加 Pod 事件处理器
	podInformer.AddEventHandler(cache.ResourceEventHandlerFuncs{
		AddFunc: func(obj interface{}) {
			pod := obj.(*v1.Pod)
			klog.Infof("pod created: %s/%s", pod.Namespace, pod.Name)
		},
		UpdateFunc: func(oldObj, newObj interface{}) {
			oldPod := oldObj.(*v1.Pod)
			newPod := newObj.(*v1.Pod)
			klog.Infof("pod updated: %s/%s %s", oldPod.Namespace, oldPod.Name, newPod.Status.Phase)
		},
		DeleteFunc: func(obj interface{}) {
			pod := obj.(*v1.Pod)
			klog.Infof("pod deleted: %s/%s", pod.Namespace, pod.Name)
		},
	})

	// 添加 Service 事件处理器
	serviceInformer.AddEventHandler(cache.ResourceEventHandlerFuncs{
		AddFunc: func(obj interface{}) {
			service := obj.(*v1.Service)
			klog.Infof("service created: %s/%s", service.Namespace, service.Name)
		},
		UpdateFunc: func(oldObj, newObj interface{}) {
			oldService := oldObj.(*v1.Service)
			newService := newObj.(*v1.Service)
			klog.Infof("service updated: %s/%s %s", oldService.Namespace, oldService.Name, newService.Spec.ClusterIP)
		},
		DeleteFunc: func(obj interface{}) {
			service := obj.(*v1.Service)
			klog.Infof("service deleted: %s/%s", service.Namespace, service.Name)
		},
	})

	// 启动 informers
	go podInformer.Run(stopCh)
	go serviceInformer.Run(stopCh)

	// 等待缓存同步
	if !cache.WaitForCacheSync(stopCh, podInformer.HasSynced, serviceInformer.HasSynced) {
		klog.Fatal("Timed out waiting for caches to sync")
	}

	klog.Info("Informers are synced and running")

	<-stopCh
}
