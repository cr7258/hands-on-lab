package main

import (
	"context"
	"fmt"
	"path/filepath"

	corev1 "k8s.io/api/core/v1"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/client-go/kubernetes/scheme"
	"k8s.io/client-go/rest"
	"k8s.io/client-go/tools/clientcmd"
	"k8s.io/client-go/util/homedir"
)

func main() {
	homedir := homedir.HomeDir()
	config, err := clientcmd.BuildConfigFromFlags("", filepath.Join(homedir, ".kube", "config"))
	if err != nil {
		panic(err)
	}

	// 配置 API 路径和请求的资源组/资源版本信息
	config.APIPath = "/api"
	config.GroupVersion = &corev1.SchemeGroupVersion

	// 配置数据的编解码器
	config.NegotiatedSerializer = scheme.Codecs

	// 实例化 RESTClient 对象
	restClient, err := rest.RESTClientFor(config)
	if err != nil {
		panic(err)
	}

	// 预设返回值存放对象
	result := &corev1.PodList{}

	// Do 方法发起请求并用 Into 方法将 API Server 的返回结果写入 Result 对象中
	err = restClient.Get().
		Namespace("default").
		Resource("pods").
		VersionedParams(&metav1.ListOptions{Limit: 500}, scheme.ParameterCodec).
		Do(context.Background()).
		Into(result)

	if err != nil {
		panic(err)
	}

	// 打印 Pod 对象
	for _, pod := range result.Items {
		fmt.Printf("Name: %s, Status: %s\n", pod.Name, pod.Status.Phase)
	}
}
