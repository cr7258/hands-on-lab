// Code generated by protoc-gen-connect-go. DO NOT EDIT.
//
// Source: objectives/v1alpha1/objectives.proto

package objectivesv1alpha1connect

import (
	context "context"
	errors "errors"
	connect_go "github.com/bufbuild/connect-go"
	v1alpha1 "github.com/pyrra-dev/pyrra/proto/objectives/v1alpha1"
	http "net/http"
	strings "strings"
)

// This is a compile-time assertion to ensure that this generated file and the connect package are
// compatible. If you get a compiler error that this constant is not defined, this code was
// generated with a version of connect newer than the one compiled into your binary. You can fix the
// problem by either regenerating this code with an older version of connect or updating the connect
// version compiled into your binary.
const _ = connect_go.IsAtLeastVersion0_1_0

const (
	// ObjectiveServiceName is the fully-qualified name of the ObjectiveService service.
	ObjectiveServiceName = "objectives.v1alpha1.ObjectiveService"
	// ObjectiveBackendServiceName is the fully-qualified name of the ObjectiveBackendService service.
	ObjectiveBackendServiceName = "objectives.v1alpha1.ObjectiveBackendService"
)

// ObjectiveServiceClient is a client for the objectives.v1alpha1.ObjectiveService service.
type ObjectiveServiceClient interface {
	List(context.Context, *connect_go.Request[v1alpha1.ListRequest]) (*connect_go.Response[v1alpha1.ListResponse], error)
	GetStatus(context.Context, *connect_go.Request[v1alpha1.GetStatusRequest]) (*connect_go.Response[v1alpha1.GetStatusResponse], error)
	GetAlerts(context.Context, *connect_go.Request[v1alpha1.GetAlertsRequest]) (*connect_go.Response[v1alpha1.GetAlertsResponse], error)
	GraphErrorBudget(context.Context, *connect_go.Request[v1alpha1.GraphErrorBudgetRequest]) (*connect_go.Response[v1alpha1.GraphErrorBudgetResponse], error)
	GraphRate(context.Context, *connect_go.Request[v1alpha1.GraphRateRequest]) (*connect_go.Response[v1alpha1.GraphRateResponse], error)
	GraphErrors(context.Context, *connect_go.Request[v1alpha1.GraphErrorsRequest]) (*connect_go.Response[v1alpha1.GraphErrorsResponse], error)
	GraphDuration(context.Context, *connect_go.Request[v1alpha1.GraphDurationRequest]) (*connect_go.Response[v1alpha1.GraphDurationResponse], error)
}

// NewObjectiveServiceClient constructs a client for the objectives.v1alpha1.ObjectiveService
// service. By default, it uses the Connect protocol with the binary Protobuf Codec, asks for
// gzipped responses, and sends uncompressed requests. To use the gRPC or gRPC-Web protocols, supply
// the connect.WithGRPC() or connect.WithGRPCWeb() options.
//
// The URL supplied here should be the base URL for the Connect or gRPC server (for example,
// http://api.acme.com or https://acme.com/grpc).
func NewObjectiveServiceClient(httpClient connect_go.HTTPClient, baseURL string, opts ...connect_go.ClientOption) ObjectiveServiceClient {
	baseURL = strings.TrimRight(baseURL, "/")
	return &objectiveServiceClient{
		list: connect_go.NewClient[v1alpha1.ListRequest, v1alpha1.ListResponse](
			httpClient,
			baseURL+"/objectives.v1alpha1.ObjectiveService/List",
			opts...,
		),
		getStatus: connect_go.NewClient[v1alpha1.GetStatusRequest, v1alpha1.GetStatusResponse](
			httpClient,
			baseURL+"/objectives.v1alpha1.ObjectiveService/GetStatus",
			opts...,
		),
		getAlerts: connect_go.NewClient[v1alpha1.GetAlertsRequest, v1alpha1.GetAlertsResponse](
			httpClient,
			baseURL+"/objectives.v1alpha1.ObjectiveService/GetAlerts",
			opts...,
		),
		graphErrorBudget: connect_go.NewClient[v1alpha1.GraphErrorBudgetRequest, v1alpha1.GraphErrorBudgetResponse](
			httpClient,
			baseURL+"/objectives.v1alpha1.ObjectiveService/GraphErrorBudget",
			opts...,
		),
		graphRate: connect_go.NewClient[v1alpha1.GraphRateRequest, v1alpha1.GraphRateResponse](
			httpClient,
			baseURL+"/objectives.v1alpha1.ObjectiveService/GraphRate",
			opts...,
		),
		graphErrors: connect_go.NewClient[v1alpha1.GraphErrorsRequest, v1alpha1.GraphErrorsResponse](
			httpClient,
			baseURL+"/objectives.v1alpha1.ObjectiveService/GraphErrors",
			opts...,
		),
		graphDuration: connect_go.NewClient[v1alpha1.GraphDurationRequest, v1alpha1.GraphDurationResponse](
			httpClient,
			baseURL+"/objectives.v1alpha1.ObjectiveService/GraphDuration",
			opts...,
		),
	}
}

// objectiveServiceClient implements ObjectiveServiceClient.
type objectiveServiceClient struct {
	list             *connect_go.Client[v1alpha1.ListRequest, v1alpha1.ListResponse]
	getStatus        *connect_go.Client[v1alpha1.GetStatusRequest, v1alpha1.GetStatusResponse]
	getAlerts        *connect_go.Client[v1alpha1.GetAlertsRequest, v1alpha1.GetAlertsResponse]
	graphErrorBudget *connect_go.Client[v1alpha1.GraphErrorBudgetRequest, v1alpha1.GraphErrorBudgetResponse]
	graphRate        *connect_go.Client[v1alpha1.GraphRateRequest, v1alpha1.GraphRateResponse]
	graphErrors      *connect_go.Client[v1alpha1.GraphErrorsRequest, v1alpha1.GraphErrorsResponse]
	graphDuration    *connect_go.Client[v1alpha1.GraphDurationRequest, v1alpha1.GraphDurationResponse]
}

// List calls objectives.v1alpha1.ObjectiveService.List.
func (c *objectiveServiceClient) List(ctx context.Context, req *connect_go.Request[v1alpha1.ListRequest]) (*connect_go.Response[v1alpha1.ListResponse], error) {
	return c.list.CallUnary(ctx, req)
}

// GetStatus calls objectives.v1alpha1.ObjectiveService.GetStatus.
func (c *objectiveServiceClient) GetStatus(ctx context.Context, req *connect_go.Request[v1alpha1.GetStatusRequest]) (*connect_go.Response[v1alpha1.GetStatusResponse], error) {
	return c.getStatus.CallUnary(ctx, req)
}

// GetAlerts calls objectives.v1alpha1.ObjectiveService.GetAlerts.
func (c *objectiveServiceClient) GetAlerts(ctx context.Context, req *connect_go.Request[v1alpha1.GetAlertsRequest]) (*connect_go.Response[v1alpha1.GetAlertsResponse], error) {
	return c.getAlerts.CallUnary(ctx, req)
}

// GraphErrorBudget calls objectives.v1alpha1.ObjectiveService.GraphErrorBudget.
func (c *objectiveServiceClient) GraphErrorBudget(ctx context.Context, req *connect_go.Request[v1alpha1.GraphErrorBudgetRequest]) (*connect_go.Response[v1alpha1.GraphErrorBudgetResponse], error) {
	return c.graphErrorBudget.CallUnary(ctx, req)
}

// GraphRate calls objectives.v1alpha1.ObjectiveService.GraphRate.
func (c *objectiveServiceClient) GraphRate(ctx context.Context, req *connect_go.Request[v1alpha1.GraphRateRequest]) (*connect_go.Response[v1alpha1.GraphRateResponse], error) {
	return c.graphRate.CallUnary(ctx, req)
}

// GraphErrors calls objectives.v1alpha1.ObjectiveService.GraphErrors.
func (c *objectiveServiceClient) GraphErrors(ctx context.Context, req *connect_go.Request[v1alpha1.GraphErrorsRequest]) (*connect_go.Response[v1alpha1.GraphErrorsResponse], error) {
	return c.graphErrors.CallUnary(ctx, req)
}

// GraphDuration calls objectives.v1alpha1.ObjectiveService.GraphDuration.
func (c *objectiveServiceClient) GraphDuration(ctx context.Context, req *connect_go.Request[v1alpha1.GraphDurationRequest]) (*connect_go.Response[v1alpha1.GraphDurationResponse], error) {
	return c.graphDuration.CallUnary(ctx, req)
}

// ObjectiveServiceHandler is an implementation of the objectives.v1alpha1.ObjectiveService service.
type ObjectiveServiceHandler interface {
	List(context.Context, *connect_go.Request[v1alpha1.ListRequest]) (*connect_go.Response[v1alpha1.ListResponse], error)
	GetStatus(context.Context, *connect_go.Request[v1alpha1.GetStatusRequest]) (*connect_go.Response[v1alpha1.GetStatusResponse], error)
	GetAlerts(context.Context, *connect_go.Request[v1alpha1.GetAlertsRequest]) (*connect_go.Response[v1alpha1.GetAlertsResponse], error)
	GraphErrorBudget(context.Context, *connect_go.Request[v1alpha1.GraphErrorBudgetRequest]) (*connect_go.Response[v1alpha1.GraphErrorBudgetResponse], error)
	GraphRate(context.Context, *connect_go.Request[v1alpha1.GraphRateRequest]) (*connect_go.Response[v1alpha1.GraphRateResponse], error)
	GraphErrors(context.Context, *connect_go.Request[v1alpha1.GraphErrorsRequest]) (*connect_go.Response[v1alpha1.GraphErrorsResponse], error)
	GraphDuration(context.Context, *connect_go.Request[v1alpha1.GraphDurationRequest]) (*connect_go.Response[v1alpha1.GraphDurationResponse], error)
}

// NewObjectiveServiceHandler builds an HTTP handler from the service implementation. It returns the
// path on which to mount the handler and the handler itself.
//
// By default, handlers support the Connect, gRPC, and gRPC-Web protocols with the binary Protobuf
// and JSON codecs. They also support gzip compression.
func NewObjectiveServiceHandler(svc ObjectiveServiceHandler, opts ...connect_go.HandlerOption) (string, http.Handler) {
	mux := http.NewServeMux()
	mux.Handle("/objectives.v1alpha1.ObjectiveService/List", connect_go.NewUnaryHandler(
		"/objectives.v1alpha1.ObjectiveService/List",
		svc.List,
		opts...,
	))
	mux.Handle("/objectives.v1alpha1.ObjectiveService/GetStatus", connect_go.NewUnaryHandler(
		"/objectives.v1alpha1.ObjectiveService/GetStatus",
		svc.GetStatus,
		opts...,
	))
	mux.Handle("/objectives.v1alpha1.ObjectiveService/GetAlerts", connect_go.NewUnaryHandler(
		"/objectives.v1alpha1.ObjectiveService/GetAlerts",
		svc.GetAlerts,
		opts...,
	))
	mux.Handle("/objectives.v1alpha1.ObjectiveService/GraphErrorBudget", connect_go.NewUnaryHandler(
		"/objectives.v1alpha1.ObjectiveService/GraphErrorBudget",
		svc.GraphErrorBudget,
		opts...,
	))
	mux.Handle("/objectives.v1alpha1.ObjectiveService/GraphRate", connect_go.NewUnaryHandler(
		"/objectives.v1alpha1.ObjectiveService/GraphRate",
		svc.GraphRate,
		opts...,
	))
	mux.Handle("/objectives.v1alpha1.ObjectiveService/GraphErrors", connect_go.NewUnaryHandler(
		"/objectives.v1alpha1.ObjectiveService/GraphErrors",
		svc.GraphErrors,
		opts...,
	))
	mux.Handle("/objectives.v1alpha1.ObjectiveService/GraphDuration", connect_go.NewUnaryHandler(
		"/objectives.v1alpha1.ObjectiveService/GraphDuration",
		svc.GraphDuration,
		opts...,
	))
	return "/objectives.v1alpha1.ObjectiveService/", mux
}

// UnimplementedObjectiveServiceHandler returns CodeUnimplemented from all methods.
type UnimplementedObjectiveServiceHandler struct{}

func (UnimplementedObjectiveServiceHandler) List(context.Context, *connect_go.Request[v1alpha1.ListRequest]) (*connect_go.Response[v1alpha1.ListResponse], error) {
	return nil, connect_go.NewError(connect_go.CodeUnimplemented, errors.New("objectives.v1alpha1.ObjectiveService.List is not implemented"))
}

func (UnimplementedObjectiveServiceHandler) GetStatus(context.Context, *connect_go.Request[v1alpha1.GetStatusRequest]) (*connect_go.Response[v1alpha1.GetStatusResponse], error) {
	return nil, connect_go.NewError(connect_go.CodeUnimplemented, errors.New("objectives.v1alpha1.ObjectiveService.GetStatus is not implemented"))
}

func (UnimplementedObjectiveServiceHandler) GetAlerts(context.Context, *connect_go.Request[v1alpha1.GetAlertsRequest]) (*connect_go.Response[v1alpha1.GetAlertsResponse], error) {
	return nil, connect_go.NewError(connect_go.CodeUnimplemented, errors.New("objectives.v1alpha1.ObjectiveService.GetAlerts is not implemented"))
}

func (UnimplementedObjectiveServiceHandler) GraphErrorBudget(context.Context, *connect_go.Request[v1alpha1.GraphErrorBudgetRequest]) (*connect_go.Response[v1alpha1.GraphErrorBudgetResponse], error) {
	return nil, connect_go.NewError(connect_go.CodeUnimplemented, errors.New("objectives.v1alpha1.ObjectiveService.GraphErrorBudget is not implemented"))
}

func (UnimplementedObjectiveServiceHandler) GraphRate(context.Context, *connect_go.Request[v1alpha1.GraphRateRequest]) (*connect_go.Response[v1alpha1.GraphRateResponse], error) {
	return nil, connect_go.NewError(connect_go.CodeUnimplemented, errors.New("objectives.v1alpha1.ObjectiveService.GraphRate is not implemented"))
}

func (UnimplementedObjectiveServiceHandler) GraphErrors(context.Context, *connect_go.Request[v1alpha1.GraphErrorsRequest]) (*connect_go.Response[v1alpha1.GraphErrorsResponse], error) {
	return nil, connect_go.NewError(connect_go.CodeUnimplemented, errors.New("objectives.v1alpha1.ObjectiveService.GraphErrors is not implemented"))
}

func (UnimplementedObjectiveServiceHandler) GraphDuration(context.Context, *connect_go.Request[v1alpha1.GraphDurationRequest]) (*connect_go.Response[v1alpha1.GraphDurationResponse], error) {
	return nil, connect_go.NewError(connect_go.CodeUnimplemented, errors.New("objectives.v1alpha1.ObjectiveService.GraphDuration is not implemented"))
}

// ObjectiveBackendServiceClient is a client for the objectives.v1alpha1.ObjectiveBackendService
// service.
type ObjectiveBackendServiceClient interface {
	List(context.Context, *connect_go.Request[v1alpha1.ListRequest]) (*connect_go.Response[v1alpha1.ListResponse], error)
}

// NewObjectiveBackendServiceClient constructs a client for the
// objectives.v1alpha1.ObjectiveBackendService service. By default, it uses the Connect protocol
// with the binary Protobuf Codec, asks for gzipped responses, and sends uncompressed requests. To
// use the gRPC or gRPC-Web protocols, supply the connect.WithGRPC() or connect.WithGRPCWeb()
// options.
//
// The URL supplied here should be the base URL for the Connect or gRPC server (for example,
// http://api.acme.com or https://acme.com/grpc).
func NewObjectiveBackendServiceClient(httpClient connect_go.HTTPClient, baseURL string, opts ...connect_go.ClientOption) ObjectiveBackendServiceClient {
	baseURL = strings.TrimRight(baseURL, "/")
	return &objectiveBackendServiceClient{
		list: connect_go.NewClient[v1alpha1.ListRequest, v1alpha1.ListResponse](
			httpClient,
			baseURL+"/objectives.v1alpha1.ObjectiveBackendService/List",
			opts...,
		),
	}
}

// objectiveBackendServiceClient implements ObjectiveBackendServiceClient.
type objectiveBackendServiceClient struct {
	list *connect_go.Client[v1alpha1.ListRequest, v1alpha1.ListResponse]
}

// List calls objectives.v1alpha1.ObjectiveBackendService.List.
func (c *objectiveBackendServiceClient) List(ctx context.Context, req *connect_go.Request[v1alpha1.ListRequest]) (*connect_go.Response[v1alpha1.ListResponse], error) {
	return c.list.CallUnary(ctx, req)
}

// ObjectiveBackendServiceHandler is an implementation of the
// objectives.v1alpha1.ObjectiveBackendService service.
type ObjectiveBackendServiceHandler interface {
	List(context.Context, *connect_go.Request[v1alpha1.ListRequest]) (*connect_go.Response[v1alpha1.ListResponse], error)
}

// NewObjectiveBackendServiceHandler builds an HTTP handler from the service implementation. It
// returns the path on which to mount the handler and the handler itself.
//
// By default, handlers support the Connect, gRPC, and gRPC-Web protocols with the binary Protobuf
// and JSON codecs. They also support gzip compression.
func NewObjectiveBackendServiceHandler(svc ObjectiveBackendServiceHandler, opts ...connect_go.HandlerOption) (string, http.Handler) {
	mux := http.NewServeMux()
	mux.Handle("/objectives.v1alpha1.ObjectiveBackendService/List", connect_go.NewUnaryHandler(
		"/objectives.v1alpha1.ObjectiveBackendService/List",
		svc.List,
		opts...,
	))
	return "/objectives.v1alpha1.ObjectiveBackendService/", mux
}

// UnimplementedObjectiveBackendServiceHandler returns CodeUnimplemented from all methods.
type UnimplementedObjectiveBackendServiceHandler struct{}

func (UnimplementedObjectiveBackendServiceHandler) List(context.Context, *connect_go.Request[v1alpha1.ListRequest]) (*connect_go.Response[v1alpha1.ListResponse], error) {
	return nil, connect_go.NewError(connect_go.CodeUnimplemented, errors.New("objectives.v1alpha1.ObjectiveBackendService.List is not implemented"))
}