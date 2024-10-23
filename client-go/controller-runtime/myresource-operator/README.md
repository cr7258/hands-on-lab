## 初始化项目

```bash
kubebuilder init --domain mydomain.com --repo github.com/cr7258/myresource-operator
```

## 创建 API

```bash
kubebuilder create api --group example --version v1 --kind MyResource
```

## 更新 MyResourceSpec 和 MyResourceStatus，设置自定义的字段

```go
// MyResourceSpec defines the desired state of MyResource.
type MyResourceSpec struct {
	// INSERT ADDITIONAL SPEC FIELDS - desired state of cluster
	// Important: Run "make" to regenerate code after modifying this file

	// Foo is an example field of MyResource. Edit myresource_types.go to remove/update
	Name  string `json:"name,omitempty"`
	Image string `json:"image,omitempty"`
}

// MyResourceStatus defines the observed state of MyResource.
type MyResourceStatus struct {
	// INSERT ADDITIONAL STATUS FIELD - define observed state of cluster
	// Important: Run "make" to regenerate code after modifying this file
	PodStatus string `json:"podStatus,omitempty"`
}
```

## 生成 CRD

```bash
make manifests
```

## 安装 CRD 到集群

```bash
make install
```

## 实现控制器的 Reconcile 逻辑

```go
func (r *MyResourceReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
	......
}
```

## 启动控制器

```bash
make run
```
