package main

import (
	"context"

	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/utils/ptr"

	"github.com/upbound/provider-aws/apis/s3/v1beta1"

	"github.com/crossplane/function-sdk-go/errors"
	"github.com/crossplane/function-sdk-go/logging"
	fnv1beta1 "github.com/crossplane/function-sdk-go/proto/v1beta1"
	"github.com/crossplane/function-sdk-go/request"
	"github.com/crossplane/function-sdk-go/resource"
	"github.com/crossplane/function-sdk-go/resource/composed"
	"github.com/crossplane/function-sdk-go/response"
)

// Function returns whatever response you ask it to.
type Function struct {
	fnv1beta1.UnimplementedFunctionRunnerServiceServer

	log logging.Logger
}

// RunFunction observes an XBuckets composite resource (XR). It adds an S3
// bucket to the desired state for every entry in the XR's spec.names array.
func (f *Function) RunFunction(_ context.Context, req *fnv1beta1.RunFunctionRequest) (*fnv1beta1.RunFunctionResponse, error) {
	f.log.Info("Running Function", "tag", req.GetMeta().GetTag())

	// Create a response to the request. This copies the desired state and
	// pipeline context from the request to the response.
	rsp := response.To(req, response.DefaultTTL)

	// Read the observed XR from the request. Most functions use the observed XR
	// to add desired managed resources.
	xr, err := request.GetObservedCompositeResource(req)
	if err != nil {
		// If the function can't read the XR, the request is malformed. This
		// should never happen. The function returns a fatal result. This tells
		// Crossplane to stop running functions and return an error.
		response.Fatal(rsp, errors.Wrapf(err, "cannot get observed composite resource from %T", req))
		return rsp, nil
	}

	// Create an updated logger with useful information about the XR.
	log := f.log.WithValues(
		"xr-version", xr.Resource.GetAPIVersion(),
		"xr-kind", xr.Resource.GetKind(),
		"xr-name", xr.Resource.GetName(),
	)

	// Get the region from the XR. The XR has getter methods like GetString,
	// GetBool, etc. You can use them to get values by their field path.
	region, err := xr.Resource.GetString("spec.region")
	if err != nil {
		response.Fatal(rsp, errors.Wrapf(err, "cannot read spec.region field of %s", xr.Resource.GetKind()))
		return rsp, nil
	}

	// Get the array of bucket names from the XR.
	names, err := xr.Resource.GetStringArray("spec.names")
	if err != nil {
		response.Fatal(rsp, errors.Wrapf(err, "cannot read spec.names field of %s", xr.Resource.GetKind()))
		return rsp, nil
	}

	// Get all desired composed resources from the request. The function will
	// update this map of resources, then save it. This get, update, set pattern
	// ensures the function keeps any resources added by other functions.
	desired, err := request.GetDesiredComposedResources(req)
	if err != nil {
		response.Fatal(rsp, errors.Wrapf(err, "cannot get desired resources from %T", req))
		return rsp, nil
	}

	// Add v1beta1 types (including Bucket) to the composed resource scheme.
	// composed.From uses this to automatically set apiVersion and kind.
	_ = v1beta1.AddToScheme(composed.Scheme)

	// Add a desired S3 bucket for each name.
	for _, name := range names {
		// One advantage of writing a function in Go is strong typing. The
		// function can import and use managed resource types from the provider.
		b := &v1beta1.Bucket{
			ObjectMeta: metav1.ObjectMeta{
				// Set the external name annotation to the desired bucket name.
				// This controls what the bucket will be named in AWS.
				Annotations: map[string]string{
					"crossplane.io/external-name": name,
				},
			},
			Spec: v1beta1.BucketSpec{
				ForProvider: v1beta1.BucketParameters{
					// Set the bucket's region to the value read from the XR.
					Region: ptr.To[string](region),
				},
			},
		}

		// Convert the bucket to the unstructured resource data format the SDK
		// uses to store desired composed resources.
		cd, err := composed.From(b)
		if err != nil {
			response.Fatal(rsp, errors.Wrapf(err, "cannot convert %T to %T", b, &composed.Unstructured{}))
			return rsp, nil
		}

		// Add the bucket to the map of desired composed resources. It's
		// important that the function adds the same bucket every time it's
		// called. It's also important that the bucket is added with the same
		// resource.Name every time it's called. The function prefixes the name
		// with "xbuckets-" to avoid collisions with any other composed
		// resources that might be in the desired resources map.
		desired[resource.Name("xbuckets-"+name)] = &resource.DesiredComposed{Resource: cd}
	}

	// Finally, save the updated desired composed resources to the response.
	if err := response.SetDesiredComposedResources(rsp, desired); err != nil {
		response.Fatal(rsp, errors.Wrapf(err, "cannot set desired composed resources in %T", rsp))
		return rsp, nil
	}

	// Log what the function did. This will only appear in the function's pod
	// logs. A function can use response.Normal and response.Warning to emit
	// Kubernetes events associated with the XR it's operating on.
	log.Info("Added desired buckets", "region", region, "count", len(names))

	return rsp, nil
}
