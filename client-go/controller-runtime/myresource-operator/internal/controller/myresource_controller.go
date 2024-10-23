/*
Copyright 2024.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

package controller

import (
	"context"
	corev1 "k8s.io/api/core/v1"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"sigs.k8s.io/controller-runtime/pkg/controller/controllerutil"

	apierrors "k8s.io/apimachinery/pkg/api/errors"
	"k8s.io/apimachinery/pkg/runtime"
	ctrl "sigs.k8s.io/controller-runtime"
	"sigs.k8s.io/controller-runtime/pkg/client"

	examplev1 "github.com/cr7258/myresource-operator/api/v1"
)

// MyResourceReconciler reconciles a MyResource object
type MyResourceReconciler struct {
	client.Client
	Scheme *runtime.Scheme
}

// +kubebuilder:rbac:groups=example.mydomain.com,resources=myresources,verbs=get;list;watch;create;update;patch;delete
// +kubebuilder:rbac:groups=example.mydomain.com,resources=myresources/status,verbs=get;update;patch
// +kubebuilder:rbac:groups=example.mydomain.com,resources=myresources/finalizers,verbs=update

// Reconcile is part of the main kubernetes reconciliation loop which aims to
// move the current state of the cluster closer to the desired state.
// TODO(user): Modify the Reconcile function to compare the state specified by
// the MyResource object against the actual cluster state, and then
// perform operations to make the cluster state reflect the state specified by
// the user.
//
// For more details, check Reconcile and its Result here:
// - https://pkg.go.dev/sigs.k8s.io/controller-runtime@v0.19.0/pkg/reconcile
func (r *MyResourceReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
	log := ctrl.LoggerFrom(ctx)

	// 尝试获取 MyResource 实例
	var myResource examplev1.MyResource
	err := r.Get(ctx, req.NamespacedName, &myResource)

	// 如果 MyResource 不存在，处理删除逻辑
	if err != nil {
		if apierrors.IsNotFound(err) {
			// MyResource 已被删除，执行相应的清理逻辑（例如删除 Pod）
			podName := req.Name // 从请求中获取 Pod 名称
			var existingPod corev1.Pod
			if err := r.Get(ctx, client.ObjectKey{Namespace: req.Namespace, Name: podName}, &existingPod); err == nil {
				log.Info("Deleting Pod", "Pod.Namespace", existingPod.Namespace, "Pod.Name", existingPod.Name)
				if err := r.Delete(ctx, &existingPod); err != nil {
					log.Error(err, "failed to delete Pod", "Pod.Namespace", existingPod.Namespace, "Pod.Name", existingPod.Name)
					return ctrl.Result{}, err
				}
				log.Info("Deleted Pod successfully", "Pod.Namespace", existingPod.Namespace, "Pod.Name", existingPod.Name)
			}
			// 这里可以直接返回，表示处理完删除逻辑
			return ctrl.Result{}, nil
		}
		log.Error(err, "unable to fetch MyResource")
		return ctrl.Result{}, err // 其他错误返回
	}

	log.Info("Reconciling MyResource", "name", myResource.Name)

	// 如果 MyResource 正在被删除
	if myResource.DeletionTimestamp != nil {
		// 删除 Pod
		podName := myResource.Spec.Name
		var existingPod corev1.Pod
		if err := r.Get(ctx, client.ObjectKey{Namespace: req.Namespace, Name: podName}, &existingPod); err == nil {
			log.Info("Deleting Pod", "Pod.Namespace", existingPod.Namespace, "Pod.Name", existingPod.Name)
			if err := r.Delete(ctx, &existingPod); err != nil {
				log.Error(err, "failed to delete Pod", "Pod.Namespace", existingPod.Namespace, "Pod.Name", existingPod.Name)
				return ctrl.Result{}, err
			}
			log.Info("Deleted Pod successfully", "Pod.Namespace", existingPod.Namespace, "Pod.Name", existingPod.Name)
		}
		return ctrl.Result{}, nil // 处理完删除后返回
	}

	podName := myResource.Spec.Name
	podImage := myResource.Spec.Image

	// 定义要创建的 Pod
	pod := &corev1.Pod{
		ObjectMeta: metav1.ObjectMeta{
			Name:      podName,
			Namespace: req.Namespace,
		},
		Spec: corev1.PodSpec{
			Containers: []corev1.Container{
				{
					Name:  "main-container",
					Image: podImage,
				},
			},
		},
	}
	// 设置 OwnerReference，确保 Pod 被删除时也能触发 MyResource 的 Reconcile
	if err := controllerutil.SetControllerReference(&myResource, pod, r.Scheme); err != nil {
		log.Error(err, "failed to set owner reference on Pod")
		return ctrl.Result{}, err
	}

	// 检查 Pod 是否已经存在
	var existingPod corev1.Pod
	err = r.Get(ctx, client.ObjectKey{Namespace: req.Namespace, Name: podName}, &existingPod)

	if err == nil {
		log.Info("Pod already exists", "Pod.Namespace", pod.Namespace, "Pod.Name", pod.Name)

		// 检查 MyResource 的 Spec 是否发生变化
		if existingPod.Spec.Containers[0].Image != podImage {
			log.Info("Updating Pod image", "Pod.Namespace", pod.Namespace, "Pod.Name", pod.Name)
			existingPod.Spec.Containers[0].Image = podImage
			if err := r.Update(ctx, &existingPod); err != nil {
				log.Error(err, "failed to update Pod", "Pod.Namespace", pod.Namespace, "Pod.Name", pod.Name)
				return ctrl.Result{}, err
			}
			log.Info("Updated Pod successfully", "Pod.Namespace", pod.Namespace, "Pod.Name", pod.Name)
		}

		// 更新 MyResource.Status，根据 Pod 的状态来更新 CRD 的 status
		podStatus := string(existingPod.Status.Phase)
		if myResource.Status.PodStatus != podStatus {
			myResource.Status.PodStatus = podStatus
			if err := r.Status().Update(ctx, &myResource); err != nil {
				log.Error(err, "failed to update MyResource status", "MyResource.Namespace", req.Namespace, "MyResource.Name", req.Name)
				return ctrl.Result{}, err
			}
		}

	} else if apierrors.IsNotFound(err) {
		// 如果 Pod 不存在，创建它
		log.Info("Creating Pod", "Pod.Namespace", pod.Namespace, "Pod.Name", pod.Name)
		if err := r.Create(ctx, pod); err != nil {
			log.Error(err, "failed to create Pod", "Pod.Namespace", pod.Namespace, "Pod.Name", pod.Name)
			return ctrl.Result{}, err
		}
		log.Info("Created Pod successfully", "Pod.Namespace", pod.Namespace, "Pod.Name", pod.Name)
	} else {
		log.Error(err, "failed to get Pod")
		return ctrl.Result{}, err
	}

	return ctrl.Result{}, nil
}

// SetupWithManager sets up the controller with the Manager.
func (r *MyResourceReconciler) SetupWithManager(mgr ctrl.Manager) error {
	return ctrl.NewControllerManagedBy(mgr).
		For(&examplev1.MyResource{}).
		Owns(&corev1.Pod{}).
		Complete(r)
}
