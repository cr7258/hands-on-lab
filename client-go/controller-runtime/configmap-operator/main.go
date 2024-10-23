package main

import (
	"context"
	"fmt"
	corev1 "k8s.io/api/core/v1"
	"k8s.io/apimachinery/pkg/runtime"
	"os"
	ctrl "sigs.k8s.io/controller-runtime"
	"sigs.k8s.io/controller-runtime/pkg/client"
	"sigs.k8s.io/controller-runtime/pkg/log/zap"
	"sigs.k8s.io/controller-runtime/pkg/manager"
)

// ConfigMapReconciler reconciles a ConfigMap object
type ConfigMapReconciler struct {
	client.Client
}

// Reconcile contains the logic for each reconciliation loop
func (r *ConfigMapReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
	// Fetch the ConfigMap instance
	var cm corev1.ConfigMap
	err := r.Get(ctx, req.NamespacedName, &cm)
	if err != nil {
		fmt.Printf("unable to fetch ConfigMap: %v\n", err)
		return ctrl.Result{}, client.IgnoreNotFound(err)
	}

	// Log ConfigMap name and namespace
	fmt.Printf("Reconciling ConfigMap %s/%s\n", cm.Namespace, cm.Name)
	return ctrl.Result{}, nil
}

// SetupWithManager sets up the controller with the Manager
func (r *ConfigMapReconciler) SetupWithManager(mgr ctrl.Manager) error {
	return ctrl.NewControllerManagedBy(mgr).
		For(&corev1.ConfigMap{}). // Watches for ConfigMap objects
		Complete(r)
}

func main() {
	ctrl.SetLogger(zap.New(zap.UseDevMode(true)))

	// Create a new manager
	mgr, err := ctrl.NewManager(ctrl.GetConfigOrDie(), manager.Options{
		Scheme: runtime.NewScheme(),
	})
	if err != nil {
		fmt.Fprintf(os.Stderr, "unable to start manager: %v\n", err)
		os.Exit(1)
	}

	// Register the corev1 (Kubernetes core API group) scheme
	if err := corev1.AddToScheme(mgr.GetScheme()); err != nil {
		fmt.Fprintf(os.Stderr, "unable to add corev1 scheme: %v\n", err)
		os.Exit(1)
	}

	// Create a new reconciler
	reconciler := &ConfigMapReconciler{
		Client: mgr.GetClient(),
	}

	// Setup the reconciler with the manager
	if err := reconciler.SetupWithManager(mgr); err != nil {
		fmt.Fprintf(os.Stderr, "unable to create controller: %v\n", err)
		os.Exit(1)
	}

	// Start the manager
	fmt.Println("Starting manager...")
	if err := mgr.Start(ctrl.SetupSignalHandler()); err != nil {
		fmt.Fprintf(os.Stderr, "unable to start manager: %v\n", err)
		os.Exit(1)
	}
}
