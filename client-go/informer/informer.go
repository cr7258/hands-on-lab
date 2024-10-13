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
		klog.Fatal(err)
	}

	clientset, err := kubernetes.NewForConfig(config)
	if err != nil {
		klog.Fatal(err)
	}

	go watchPods(clientset)
	go watchServices(clientset)

	// Keep the main goroutine running
	select {}
}

func watchPods(clientset *kubernetes.Clientset) {
	listWatcher := cache.NewListWatchFromClient(
		clientset.CoreV1().RESTClient(),
		"pods",
		metav1.NamespaceAll,
		fields.Everything(),
	)

	_, controller := cache.NewInformer(
		listWatcher,
		&v1.Pod{},
		time.Minute,
		cache.ResourceEventHandlerFuncs{
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
		},
	)

	stopCh := make(chan struct{})
	defer close(stopCh)
	go controller.Run(stopCh)

	<-stopCh
}

func watchServices(clientset *kubernetes.Clientset) {
	listWatcher := cache.NewListWatchFromClient(
		clientset.CoreV1().RESTClient(),
		"services",
		metav1.NamespaceAll,
		fields.Everything(),
	)

	_, controller := cache.NewInformer(
		listWatcher,
		&v1.Service{},
		time.Minute,
		cache.ResourceEventHandlerFuncs{
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
		},
	)

	stopCh := make(chan struct{})
	defer close(stopCh)
	go controller.Run(stopCh)

	<-stopCh
}
