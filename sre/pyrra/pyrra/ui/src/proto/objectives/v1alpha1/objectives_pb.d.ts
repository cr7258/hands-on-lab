// @generated by protoc-gen-es v1.2.0 with parameter "target=js+dts"
// @generated from file objectives/v1alpha1/objectives.proto (package objectives.v1alpha1, syntax proto3)
/* eslint-disable */
// @ts-nocheck

import type { BinaryReadOptions, Duration, FieldList, JsonReadOptions, JsonValue, PartialMessage, PlainMessage, Timestamp } from "@bufbuild/protobuf";
import { Message, proto3 } from "@bufbuild/protobuf";

/**
 * @generated from message objectives.v1alpha1.ListRequest
 */
export declare class ListRequest extends Message<ListRequest> {
  /**
   * @generated from field: string expr = 1;
   */
  expr: string;

  /**
   * @generated from field: string grouping = 2;
   */
  grouping: string;

  constructor(data?: PartialMessage<ListRequest>);

  static readonly runtime: typeof proto3;
  static readonly typeName = "objectives.v1alpha1.ListRequest";
  static readonly fields: FieldList;

  static fromBinary(bytes: Uint8Array, options?: Partial<BinaryReadOptions>): ListRequest;

  static fromJson(jsonValue: JsonValue, options?: Partial<JsonReadOptions>): ListRequest;

  static fromJsonString(jsonString: string, options?: Partial<JsonReadOptions>): ListRequest;

  static equals(a: ListRequest | PlainMessage<ListRequest> | undefined, b: ListRequest | PlainMessage<ListRequest> | undefined): boolean;
}

/**
 * @generated from message objectives.v1alpha1.ListResponse
 */
export declare class ListResponse extends Message<ListResponse> {
  /**
   * @generated from field: repeated objectives.v1alpha1.Objective objectives = 1;
   */
  objectives: Objective[];

  constructor(data?: PartialMessage<ListResponse>);

  static readonly runtime: typeof proto3;
  static readonly typeName = "objectives.v1alpha1.ListResponse";
  static readonly fields: FieldList;

  static fromBinary(bytes: Uint8Array, options?: Partial<BinaryReadOptions>): ListResponse;

  static fromJson(jsonValue: JsonValue, options?: Partial<JsonReadOptions>): ListResponse;

  static fromJsonString(jsonString: string, options?: Partial<JsonReadOptions>): ListResponse;

  static equals(a: ListResponse | PlainMessage<ListResponse> | undefined, b: ListResponse | PlainMessage<ListResponse> | undefined): boolean;
}

/**
 * @generated from message objectives.v1alpha1.Objective
 */
export declare class Objective extends Message<Objective> {
  /**
   * @generated from field: map<string, string> labels = 1;
   */
  labels: { [key: string]: string };

  /**
   * @generated from field: double target = 2;
   */
  target: number;

  /**
   * @generated from field: google.protobuf.Duration window = 3;
   */
  window?: Duration;

  /**
   * @generated from field: string description = 4;
   */
  description: string;

  /**
   * @generated from field: objectives.v1alpha1.Indicator indicator = 5;
   */
  indicator?: Indicator;

  /**
   * @generated from field: string config = 6;
   */
  config: string;

  /**
   * @generated from field: objectives.v1alpha1.Queries queries = 7;
   */
  queries?: Queries;

  constructor(data?: PartialMessage<Objective>);

  static readonly runtime: typeof proto3;
  static readonly typeName = "objectives.v1alpha1.Objective";
  static readonly fields: FieldList;

  static fromBinary(bytes: Uint8Array, options?: Partial<BinaryReadOptions>): Objective;

  static fromJson(jsonValue: JsonValue, options?: Partial<JsonReadOptions>): Objective;

  static fromJsonString(jsonString: string, options?: Partial<JsonReadOptions>): Objective;

  static equals(a: Objective | PlainMessage<Objective> | undefined, b: Objective | PlainMessage<Objective> | undefined): boolean;
}

/**
 * @generated from message objectives.v1alpha1.Indicator
 */
export declare class Indicator extends Message<Indicator> {
  /**
   * @generated from oneof objectives.v1alpha1.Indicator.options
   */
  options: {
    /**
     * @generated from field: objectives.v1alpha1.Ratio ratio = 1;
     */
    value: Ratio;
    case: "ratio";
  } | {
    /**
     * @generated from field: objectives.v1alpha1.Latency latency = 2;
     */
    value: Latency;
    case: "latency";
  } | {
    /**
     * @generated from field: objectives.v1alpha1.BoolGauge boolGauge = 3;
     */
    value: BoolGauge;
    case: "boolGauge";
  } | {
    /**
     * @generated from field: objectives.v1alpha1.LatencyNative latency_native = 4;
     */
    value: LatencyNative;
    case: "latencyNative";
  } | { case: undefined; value?: undefined };

  constructor(data?: PartialMessage<Indicator>);

  static readonly runtime: typeof proto3;
  static readonly typeName = "objectives.v1alpha1.Indicator";
  static readonly fields: FieldList;

  static fromBinary(bytes: Uint8Array, options?: Partial<BinaryReadOptions>): Indicator;

  static fromJson(jsonValue: JsonValue, options?: Partial<JsonReadOptions>): Indicator;

  static fromJsonString(jsonString: string, options?: Partial<JsonReadOptions>): Indicator;

  static equals(a: Indicator | PlainMessage<Indicator> | undefined, b: Indicator | PlainMessage<Indicator> | undefined): boolean;
}

/**
 * @generated from message objectives.v1alpha1.Ratio
 */
export declare class Ratio extends Message<Ratio> {
  /**
   * @generated from field: objectives.v1alpha1.Query total = 1;
   */
  total?: Query;

  /**
   * @generated from field: objectives.v1alpha1.Query errors = 2;
   */
  errors?: Query;

  /**
   * @generated from field: repeated string grouping = 3;
   */
  grouping: string[];

  constructor(data?: PartialMessage<Ratio>);

  static readonly runtime: typeof proto3;
  static readonly typeName = "objectives.v1alpha1.Ratio";
  static readonly fields: FieldList;

  static fromBinary(bytes: Uint8Array, options?: Partial<BinaryReadOptions>): Ratio;

  static fromJson(jsonValue: JsonValue, options?: Partial<JsonReadOptions>): Ratio;

  static fromJsonString(jsonString: string, options?: Partial<JsonReadOptions>): Ratio;

  static equals(a: Ratio | PlainMessage<Ratio> | undefined, b: Ratio | PlainMessage<Ratio> | undefined): boolean;
}

/**
 * @generated from message objectives.v1alpha1.Latency
 */
export declare class Latency extends Message<Latency> {
  /**
   * @generated from field: objectives.v1alpha1.Query total = 1;
   */
  total?: Query;

  /**
   * @generated from field: objectives.v1alpha1.Query success = 2;
   */
  success?: Query;

  /**
   * @generated from field: repeated string grouping = 3;
   */
  grouping: string[];

  constructor(data?: PartialMessage<Latency>);

  static readonly runtime: typeof proto3;
  static readonly typeName = "objectives.v1alpha1.Latency";
  static readonly fields: FieldList;

  static fromBinary(bytes: Uint8Array, options?: Partial<BinaryReadOptions>): Latency;

  static fromJson(jsonValue: JsonValue, options?: Partial<JsonReadOptions>): Latency;

  static fromJsonString(jsonString: string, options?: Partial<JsonReadOptions>): Latency;

  static equals(a: Latency | PlainMessage<Latency> | undefined, b: Latency | PlainMessage<Latency> | undefined): boolean;
}

/**
 * @generated from message objectives.v1alpha1.LatencyNative
 */
export declare class LatencyNative extends Message<LatencyNative> {
  /**
   * @generated from field: objectives.v1alpha1.Query total = 1;
   */
  total?: Query;

  /**
   * @generated from field: string latency = 2;
   */
  latency: string;

  /**
   * @generated from field: repeated string grouping = 3;
   */
  grouping: string[];

  constructor(data?: PartialMessage<LatencyNative>);

  static readonly runtime: typeof proto3;
  static readonly typeName = "objectives.v1alpha1.LatencyNative";
  static readonly fields: FieldList;

  static fromBinary(bytes: Uint8Array, options?: Partial<BinaryReadOptions>): LatencyNative;

  static fromJson(jsonValue: JsonValue, options?: Partial<JsonReadOptions>): LatencyNative;

  static fromJsonString(jsonString: string, options?: Partial<JsonReadOptions>): LatencyNative;

  static equals(a: LatencyNative | PlainMessage<LatencyNative> | undefined, b: LatencyNative | PlainMessage<LatencyNative> | undefined): boolean;
}

/**
 * @generated from message objectives.v1alpha1.BoolGauge
 */
export declare class BoolGauge extends Message<BoolGauge> {
  /**
   * @generated from field: objectives.v1alpha1.Query boolGauge = 1;
   */
  boolGauge?: Query;

  /**
   * @generated from field: repeated string grouping = 3;
   */
  grouping: string[];

  constructor(data?: PartialMessage<BoolGauge>);

  static readonly runtime: typeof proto3;
  static readonly typeName = "objectives.v1alpha1.BoolGauge";
  static readonly fields: FieldList;

  static fromBinary(bytes: Uint8Array, options?: Partial<BinaryReadOptions>): BoolGauge;

  static fromJson(jsonValue: JsonValue, options?: Partial<JsonReadOptions>): BoolGauge;

  static fromJsonString(jsonString: string, options?: Partial<JsonReadOptions>): BoolGauge;

  static equals(a: BoolGauge | PlainMessage<BoolGauge> | undefined, b: BoolGauge | PlainMessage<BoolGauge> | undefined): boolean;
}

/**
 * @generated from message objectives.v1alpha1.Query
 */
export declare class Query extends Message<Query> {
  /**
   * @generated from field: string metric = 1;
   */
  metric: string;

  /**
   * @generated from field: string name = 2;
   */
  name: string;

  /**
   * @generated from field: repeated objectives.v1alpha1.LabelMatcher matchers = 3;
   */
  matchers: LabelMatcher[];

  constructor(data?: PartialMessage<Query>);

  static readonly runtime: typeof proto3;
  static readonly typeName = "objectives.v1alpha1.Query";
  static readonly fields: FieldList;

  static fromBinary(bytes: Uint8Array, options?: Partial<BinaryReadOptions>): Query;

  static fromJson(jsonValue: JsonValue, options?: Partial<JsonReadOptions>): Query;

  static fromJsonString(jsonString: string, options?: Partial<JsonReadOptions>): Query;

  static equals(a: Query | PlainMessage<Query> | undefined, b: Query | PlainMessage<Query> | undefined): boolean;
}

/**
 * @generated from message objectives.v1alpha1.Queries
 */
export declare class Queries extends Message<Queries> {
  /**
   * @generated from field: string countTotal = 1;
   */
  countTotal: string;

  /**
   * @generated from field: string countErrors = 2;
   */
  countErrors: string;

  /**
   * @generated from field: string graphErrorBudget = 3;
   */
  graphErrorBudget: string;

  /**
   * @generated from field: string graphRequests = 4;
   */
  graphRequests: string;

  /**
   * @generated from field: string graphErrors = 5;
   */
  graphErrors: string;

  constructor(data?: PartialMessage<Queries>);

  static readonly runtime: typeof proto3;
  static readonly typeName = "objectives.v1alpha1.Queries";
  static readonly fields: FieldList;

  static fromBinary(bytes: Uint8Array, options?: Partial<BinaryReadOptions>): Queries;

  static fromJson(jsonValue: JsonValue, options?: Partial<JsonReadOptions>): Queries;

  static fromJsonString(jsonString: string, options?: Partial<JsonReadOptions>): Queries;

  static equals(a: Queries | PlainMessage<Queries> | undefined, b: Queries | PlainMessage<Queries> | undefined): boolean;
}

/**
 * Copied from Prometheus.
 * Matcher specifies a rule, which can match or set of labels or not.
 *
 * @generated from message objectives.v1alpha1.LabelMatcher
 */
export declare class LabelMatcher extends Message<LabelMatcher> {
  /**
   * @generated from field: objectives.v1alpha1.LabelMatcher.Type type = 1;
   */
  type: LabelMatcher_Type;

  /**
   * @generated from field: string name = 2;
   */
  name: string;

  /**
   * @generated from field: string value = 3;
   */
  value: string;

  constructor(data?: PartialMessage<LabelMatcher>);

  static readonly runtime: typeof proto3;
  static readonly typeName = "objectives.v1alpha1.LabelMatcher";
  static readonly fields: FieldList;

  static fromBinary(bytes: Uint8Array, options?: Partial<BinaryReadOptions>): LabelMatcher;

  static fromJson(jsonValue: JsonValue, options?: Partial<JsonReadOptions>): LabelMatcher;

  static fromJsonString(jsonString: string, options?: Partial<JsonReadOptions>): LabelMatcher;

  static equals(a: LabelMatcher | PlainMessage<LabelMatcher> | undefined, b: LabelMatcher | PlainMessage<LabelMatcher> | undefined): boolean;
}

/**
 * @generated from enum objectives.v1alpha1.LabelMatcher.Type
 */
export declare enum LabelMatcher_Type {
  /**
   * @generated from enum value: EQ = 0;
   */
  EQ = 0,

  /**
   * @generated from enum value: NEQ = 1;
   */
  NEQ = 1,

  /**
   * @generated from enum value: RE = 2;
   */
  RE = 2,

  /**
   * @generated from enum value: NRE = 3;
   */
  NRE = 3,
}

/**
 * @generated from message objectives.v1alpha1.GetStatusRequest
 */
export declare class GetStatusRequest extends Message<GetStatusRequest> {
  /**
   * @generated from field: string expr = 1;
   */
  expr: string;

  /**
   * @generated from field: string grouping = 2;
   */
  grouping: string;

  /**
   * @generated from field: google.protobuf.Timestamp time = 3;
   */
  time?: Timestamp;

  constructor(data?: PartialMessage<GetStatusRequest>);

  static readonly runtime: typeof proto3;
  static readonly typeName = "objectives.v1alpha1.GetStatusRequest";
  static readonly fields: FieldList;

  static fromBinary(bytes: Uint8Array, options?: Partial<BinaryReadOptions>): GetStatusRequest;

  static fromJson(jsonValue: JsonValue, options?: Partial<JsonReadOptions>): GetStatusRequest;

  static fromJsonString(jsonString: string, options?: Partial<JsonReadOptions>): GetStatusRequest;

  static equals(a: GetStatusRequest | PlainMessage<GetStatusRequest> | undefined, b: GetStatusRequest | PlainMessage<GetStatusRequest> | undefined): boolean;
}

/**
 * @generated from message objectives.v1alpha1.GetStatusResponse
 */
export declare class GetStatusResponse extends Message<GetStatusResponse> {
  /**
   * @generated from field: repeated objectives.v1alpha1.ObjectiveStatus status = 1;
   */
  status: ObjectiveStatus[];

  constructor(data?: PartialMessage<GetStatusResponse>);

  static readonly runtime: typeof proto3;
  static readonly typeName = "objectives.v1alpha1.GetStatusResponse";
  static readonly fields: FieldList;

  static fromBinary(bytes: Uint8Array, options?: Partial<BinaryReadOptions>): GetStatusResponse;

  static fromJson(jsonValue: JsonValue, options?: Partial<JsonReadOptions>): GetStatusResponse;

  static fromJsonString(jsonString: string, options?: Partial<JsonReadOptions>): GetStatusResponse;

  static equals(a: GetStatusResponse | PlainMessage<GetStatusResponse> | undefined, b: GetStatusResponse | PlainMessage<GetStatusResponse> | undefined): boolean;
}

/**
 * @generated from message objectives.v1alpha1.ObjectiveStatus
 */
export declare class ObjectiveStatus extends Message<ObjectiveStatus> {
  /**
   * @generated from field: map<string, string> labels = 1;
   */
  labels: { [key: string]: string };

  /**
   * @generated from field: objectives.v1alpha1.Availability availability = 2;
   */
  availability?: Availability;

  /**
   * @generated from field: objectives.v1alpha1.Budget budget = 3;
   */
  budget?: Budget;

  constructor(data?: PartialMessage<ObjectiveStatus>);

  static readonly runtime: typeof proto3;
  static readonly typeName = "objectives.v1alpha1.ObjectiveStatus";
  static readonly fields: FieldList;

  static fromBinary(bytes: Uint8Array, options?: Partial<BinaryReadOptions>): ObjectiveStatus;

  static fromJson(jsonValue: JsonValue, options?: Partial<JsonReadOptions>): ObjectiveStatus;

  static fromJsonString(jsonString: string, options?: Partial<JsonReadOptions>): ObjectiveStatus;

  static equals(a: ObjectiveStatus | PlainMessage<ObjectiveStatus> | undefined, b: ObjectiveStatus | PlainMessage<ObjectiveStatus> | undefined): boolean;
}

/**
 * @generated from message objectives.v1alpha1.Availability
 */
export declare class Availability extends Message<Availability> {
  /**
   * @generated from field: double percentage = 1;
   */
  percentage: number;

  /**
   * @generated from field: double total = 2;
   */
  total: number;

  /**
   * @generated from field: double errors = 3;
   */
  errors: number;

  constructor(data?: PartialMessage<Availability>);

  static readonly runtime: typeof proto3;
  static readonly typeName = "objectives.v1alpha1.Availability";
  static readonly fields: FieldList;

  static fromBinary(bytes: Uint8Array, options?: Partial<BinaryReadOptions>): Availability;

  static fromJson(jsonValue: JsonValue, options?: Partial<JsonReadOptions>): Availability;

  static fromJsonString(jsonString: string, options?: Partial<JsonReadOptions>): Availability;

  static equals(a: Availability | PlainMessage<Availability> | undefined, b: Availability | PlainMessage<Availability> | undefined): boolean;
}

/**
 * @generated from message objectives.v1alpha1.Budget
 */
export declare class Budget extends Message<Budget> {
  /**
   * @generated from field: double total = 1;
   */
  total: number;

  /**
   * @generated from field: double remaining = 2;
   */
  remaining: number;

  /**
   * @generated from field: double max = 3;
   */
  max: number;

  constructor(data?: PartialMessage<Budget>);

  static readonly runtime: typeof proto3;
  static readonly typeName = "objectives.v1alpha1.Budget";
  static readonly fields: FieldList;

  static fromBinary(bytes: Uint8Array, options?: Partial<BinaryReadOptions>): Budget;

  static fromJson(jsonValue: JsonValue, options?: Partial<JsonReadOptions>): Budget;

  static fromJsonString(jsonString: string, options?: Partial<JsonReadOptions>): Budget;

  static equals(a: Budget | PlainMessage<Budget> | undefined, b: Budget | PlainMessage<Budget> | undefined): boolean;
}

/**
 * @generated from message objectives.v1alpha1.GetAlertsRequest
 */
export declare class GetAlertsRequest extends Message<GetAlertsRequest> {
  /**
   * @generated from field: string expr = 1;
   */
  expr: string;

  /**
   * @generated from field: string grouping = 2;
   */
  grouping: string;

  /**
   * @generated from field: bool inactive = 3;
   */
  inactive: boolean;

  /**
   * @generated from field: bool current = 4;
   */
  current: boolean;

  constructor(data?: PartialMessage<GetAlertsRequest>);

  static readonly runtime: typeof proto3;
  static readonly typeName = "objectives.v1alpha1.GetAlertsRequest";
  static readonly fields: FieldList;

  static fromBinary(bytes: Uint8Array, options?: Partial<BinaryReadOptions>): GetAlertsRequest;

  static fromJson(jsonValue: JsonValue, options?: Partial<JsonReadOptions>): GetAlertsRequest;

  static fromJsonString(jsonString: string, options?: Partial<JsonReadOptions>): GetAlertsRequest;

  static equals(a: GetAlertsRequest | PlainMessage<GetAlertsRequest> | undefined, b: GetAlertsRequest | PlainMessage<GetAlertsRequest> | undefined): boolean;
}

/**
 * @generated from message objectives.v1alpha1.GetAlertsResponse
 */
export declare class GetAlertsResponse extends Message<GetAlertsResponse> {
  /**
   * @generated from field: repeated objectives.v1alpha1.Alert alerts = 1;
   */
  alerts: Alert[];

  constructor(data?: PartialMessage<GetAlertsResponse>);

  static readonly runtime: typeof proto3;
  static readonly typeName = "objectives.v1alpha1.GetAlertsResponse";
  static readonly fields: FieldList;

  static fromBinary(bytes: Uint8Array, options?: Partial<BinaryReadOptions>): GetAlertsResponse;

  static fromJson(jsonValue: JsonValue, options?: Partial<JsonReadOptions>): GetAlertsResponse;

  static fromJsonString(jsonString: string, options?: Partial<JsonReadOptions>): GetAlertsResponse;

  static equals(a: GetAlertsResponse | PlainMessage<GetAlertsResponse> | undefined, b: GetAlertsResponse | PlainMessage<GetAlertsResponse> | undefined): boolean;
}

/**
 * @generated from message objectives.v1alpha1.Alert
 */
export declare class Alert extends Message<Alert> {
  /**
   * @generated from field: map<string, string> labels = 1;
   */
  labels: { [key: string]: string };

  /**
   * @generated from field: string severity = 2;
   */
  severity: string;

  /**
   * @generated from field: google.protobuf.Duration for = 3;
   */
  for?: Duration;

  /**
   * @generated from field: double factor = 4;
   */
  factor: number;

  /**
   * @generated from field: objectives.v1alpha1.Alert.State state = 5;
   */
  state: Alert_State;

  /**
   * @generated from field: objectives.v1alpha1.Burnrate short = 6;
   */
  short?: Burnrate;

  /**
   * @generated from field: objectives.v1alpha1.Burnrate long = 7;
   */
  long?: Burnrate;

  constructor(data?: PartialMessage<Alert>);

  static readonly runtime: typeof proto3;
  static readonly typeName = "objectives.v1alpha1.Alert";
  static readonly fields: FieldList;

  static fromBinary(bytes: Uint8Array, options?: Partial<BinaryReadOptions>): Alert;

  static fromJson(jsonValue: JsonValue, options?: Partial<JsonReadOptions>): Alert;

  static fromJsonString(jsonString: string, options?: Partial<JsonReadOptions>): Alert;

  static equals(a: Alert | PlainMessage<Alert> | undefined, b: Alert | PlainMessage<Alert> | undefined): boolean;
}

/**
 * @generated from enum objectives.v1alpha1.Alert.State
 */
export declare enum Alert_State {
  /**
   * @generated from enum value: inactive = 0;
   */
  inactive = 0,

  /**
   * @generated from enum value: pending = 1;
   */
  pending = 1,

  /**
   * @generated from enum value: firing = 2;
   */
  firing = 2,
}

/**
 * @generated from message objectives.v1alpha1.Burnrate
 */
export declare class Burnrate extends Message<Burnrate> {
  /**
   * @generated from field: google.protobuf.Duration window = 1;
   */
  window?: Duration;

  /**
   * @generated from field: double current = 2;
   */
  current: number;

  /**
   * @generated from field: string query = 3;
   */
  query: string;

  constructor(data?: PartialMessage<Burnrate>);

  static readonly runtime: typeof proto3;
  static readonly typeName = "objectives.v1alpha1.Burnrate";
  static readonly fields: FieldList;

  static fromBinary(bytes: Uint8Array, options?: Partial<BinaryReadOptions>): Burnrate;

  static fromJson(jsonValue: JsonValue, options?: Partial<JsonReadOptions>): Burnrate;

  static fromJsonString(jsonString: string, options?: Partial<JsonReadOptions>): Burnrate;

  static equals(a: Burnrate | PlainMessage<Burnrate> | undefined, b: Burnrate | PlainMessage<Burnrate> | undefined): boolean;
}

/**
 * @generated from message objectives.v1alpha1.GraphErrorBudgetRequest
 */
export declare class GraphErrorBudgetRequest extends Message<GraphErrorBudgetRequest> {
  /**
   * @generated from field: string expr = 1;
   */
  expr: string;

  /**
   * @generated from field: string grouping = 2;
   */
  grouping: string;

  /**
   * @generated from field: google.protobuf.Timestamp start = 3;
   */
  start?: Timestamp;

  /**
   * @generated from field: google.protobuf.Timestamp end = 4;
   */
  end?: Timestamp;

  constructor(data?: PartialMessage<GraphErrorBudgetRequest>);

  static readonly runtime: typeof proto3;
  static readonly typeName = "objectives.v1alpha1.GraphErrorBudgetRequest";
  static readonly fields: FieldList;

  static fromBinary(bytes: Uint8Array, options?: Partial<BinaryReadOptions>): GraphErrorBudgetRequest;

  static fromJson(jsonValue: JsonValue, options?: Partial<JsonReadOptions>): GraphErrorBudgetRequest;

  static fromJsonString(jsonString: string, options?: Partial<JsonReadOptions>): GraphErrorBudgetRequest;

  static equals(a: GraphErrorBudgetRequest | PlainMessage<GraphErrorBudgetRequest> | undefined, b: GraphErrorBudgetRequest | PlainMessage<GraphErrorBudgetRequest> | undefined): boolean;
}

/**
 * @generated from message objectives.v1alpha1.GraphErrorBudgetResponse
 */
export declare class GraphErrorBudgetResponse extends Message<GraphErrorBudgetResponse> {
  /**
   * @generated from field: objectives.v1alpha1.Timeseries timeseries = 1;
   */
  timeseries?: Timeseries;

  constructor(data?: PartialMessage<GraphErrorBudgetResponse>);

  static readonly runtime: typeof proto3;
  static readonly typeName = "objectives.v1alpha1.GraphErrorBudgetResponse";
  static readonly fields: FieldList;

  static fromBinary(bytes: Uint8Array, options?: Partial<BinaryReadOptions>): GraphErrorBudgetResponse;

  static fromJson(jsonValue: JsonValue, options?: Partial<JsonReadOptions>): GraphErrorBudgetResponse;

  static fromJsonString(jsonString: string, options?: Partial<JsonReadOptions>): GraphErrorBudgetResponse;

  static equals(a: GraphErrorBudgetResponse | PlainMessage<GraphErrorBudgetResponse> | undefined, b: GraphErrorBudgetResponse | PlainMessage<GraphErrorBudgetResponse> | undefined): boolean;
}

/**
 * @generated from message objectives.v1alpha1.GraphRateRequest
 */
export declare class GraphRateRequest extends Message<GraphRateRequest> {
  /**
   * @generated from field: string expr = 1;
   */
  expr: string;

  /**
   * @generated from field: string grouping = 2;
   */
  grouping: string;

  /**
   * @generated from field: google.protobuf.Timestamp start = 3;
   */
  start?: Timestamp;

  /**
   * @generated from field: google.protobuf.Timestamp end = 4;
   */
  end?: Timestamp;

  constructor(data?: PartialMessage<GraphRateRequest>);

  static readonly runtime: typeof proto3;
  static readonly typeName = "objectives.v1alpha1.GraphRateRequest";
  static readonly fields: FieldList;

  static fromBinary(bytes: Uint8Array, options?: Partial<BinaryReadOptions>): GraphRateRequest;

  static fromJson(jsonValue: JsonValue, options?: Partial<JsonReadOptions>): GraphRateRequest;

  static fromJsonString(jsonString: string, options?: Partial<JsonReadOptions>): GraphRateRequest;

  static equals(a: GraphRateRequest | PlainMessage<GraphRateRequest> | undefined, b: GraphRateRequest | PlainMessage<GraphRateRequest> | undefined): boolean;
}

/**
 * @generated from message objectives.v1alpha1.GraphRateResponse
 */
export declare class GraphRateResponse extends Message<GraphRateResponse> {
  /**
   * @generated from field: objectives.v1alpha1.Timeseries timeseries = 1;
   */
  timeseries?: Timeseries;

  constructor(data?: PartialMessage<GraphRateResponse>);

  static readonly runtime: typeof proto3;
  static readonly typeName = "objectives.v1alpha1.GraphRateResponse";
  static readonly fields: FieldList;

  static fromBinary(bytes: Uint8Array, options?: Partial<BinaryReadOptions>): GraphRateResponse;

  static fromJson(jsonValue: JsonValue, options?: Partial<JsonReadOptions>): GraphRateResponse;

  static fromJsonString(jsonString: string, options?: Partial<JsonReadOptions>): GraphRateResponse;

  static equals(a: GraphRateResponse | PlainMessage<GraphRateResponse> | undefined, b: GraphRateResponse | PlainMessage<GraphRateResponse> | undefined): boolean;
}

/**
 * @generated from message objectives.v1alpha1.GraphErrorsRequest
 */
export declare class GraphErrorsRequest extends Message<GraphErrorsRequest> {
  /**
   * @generated from field: string expr = 1;
   */
  expr: string;

  /**
   * @generated from field: string grouping = 2;
   */
  grouping: string;

  /**
   * @generated from field: google.protobuf.Timestamp start = 3;
   */
  start?: Timestamp;

  /**
   * @generated from field: google.protobuf.Timestamp end = 4;
   */
  end?: Timestamp;

  constructor(data?: PartialMessage<GraphErrorsRequest>);

  static readonly runtime: typeof proto3;
  static readonly typeName = "objectives.v1alpha1.GraphErrorsRequest";
  static readonly fields: FieldList;

  static fromBinary(bytes: Uint8Array, options?: Partial<BinaryReadOptions>): GraphErrorsRequest;

  static fromJson(jsonValue: JsonValue, options?: Partial<JsonReadOptions>): GraphErrorsRequest;

  static fromJsonString(jsonString: string, options?: Partial<JsonReadOptions>): GraphErrorsRequest;

  static equals(a: GraphErrorsRequest | PlainMessage<GraphErrorsRequest> | undefined, b: GraphErrorsRequest | PlainMessage<GraphErrorsRequest> | undefined): boolean;
}

/**
 * @generated from message objectives.v1alpha1.GraphErrorsResponse
 */
export declare class GraphErrorsResponse extends Message<GraphErrorsResponse> {
  /**
   * @generated from field: objectives.v1alpha1.Timeseries timeseries = 1;
   */
  timeseries?: Timeseries;

  constructor(data?: PartialMessage<GraphErrorsResponse>);

  static readonly runtime: typeof proto3;
  static readonly typeName = "objectives.v1alpha1.GraphErrorsResponse";
  static readonly fields: FieldList;

  static fromBinary(bytes: Uint8Array, options?: Partial<BinaryReadOptions>): GraphErrorsResponse;

  static fromJson(jsonValue: JsonValue, options?: Partial<JsonReadOptions>): GraphErrorsResponse;

  static fromJsonString(jsonString: string, options?: Partial<JsonReadOptions>): GraphErrorsResponse;

  static equals(a: GraphErrorsResponse | PlainMessage<GraphErrorsResponse> | undefined, b: GraphErrorsResponse | PlainMessage<GraphErrorsResponse> | undefined): boolean;
}

/**
 * @generated from message objectives.v1alpha1.Timeseries
 */
export declare class Timeseries extends Message<Timeseries> {
  /**
   * @generated from field: repeated string labels = 1;
   */
  labels: string[];

  /**
   * @generated from field: string query = 2;
   */
  query: string;

  /**
   * @generated from field: repeated objectives.v1alpha1.Series series = 3;
   */
  series: Series[];

  constructor(data?: PartialMessage<Timeseries>);

  static readonly runtime: typeof proto3;
  static readonly typeName = "objectives.v1alpha1.Timeseries";
  static readonly fields: FieldList;

  static fromBinary(bytes: Uint8Array, options?: Partial<BinaryReadOptions>): Timeseries;

  static fromJson(jsonValue: JsonValue, options?: Partial<JsonReadOptions>): Timeseries;

  static fromJsonString(jsonString: string, options?: Partial<JsonReadOptions>): Timeseries;

  static equals(a: Timeseries | PlainMessage<Timeseries> | undefined, b: Timeseries | PlainMessage<Timeseries> | undefined): boolean;
}

/**
 * @generated from message objectives.v1alpha1.Series
 */
export declare class Series extends Message<Series> {
  /**
   * @generated from field: repeated double values = 1;
   */
  values: number[];

  constructor(data?: PartialMessage<Series>);

  static readonly runtime: typeof proto3;
  static readonly typeName = "objectives.v1alpha1.Series";
  static readonly fields: FieldList;

  static fromBinary(bytes: Uint8Array, options?: Partial<BinaryReadOptions>): Series;

  static fromJson(jsonValue: JsonValue, options?: Partial<JsonReadOptions>): Series;

  static fromJsonString(jsonString: string, options?: Partial<JsonReadOptions>): Series;

  static equals(a: Series | PlainMessage<Series> | undefined, b: Series | PlainMessage<Series> | undefined): boolean;
}

/**
 * @generated from message objectives.v1alpha1.GraphDurationRequest
 */
export declare class GraphDurationRequest extends Message<GraphDurationRequest> {
  /**
   * @generated from field: string expr = 1;
   */
  expr: string;

  /**
   * @generated from field: string grouping = 2;
   */
  grouping: string;

  /**
   * @generated from field: google.protobuf.Timestamp start = 3;
   */
  start?: Timestamp;

  /**
   * @generated from field: google.protobuf.Timestamp end = 4;
   */
  end?: Timestamp;

  constructor(data?: PartialMessage<GraphDurationRequest>);

  static readonly runtime: typeof proto3;
  static readonly typeName = "objectives.v1alpha1.GraphDurationRequest";
  static readonly fields: FieldList;

  static fromBinary(bytes: Uint8Array, options?: Partial<BinaryReadOptions>): GraphDurationRequest;

  static fromJson(jsonValue: JsonValue, options?: Partial<JsonReadOptions>): GraphDurationRequest;

  static fromJsonString(jsonString: string, options?: Partial<JsonReadOptions>): GraphDurationRequest;

  static equals(a: GraphDurationRequest | PlainMessage<GraphDurationRequest> | undefined, b: GraphDurationRequest | PlainMessage<GraphDurationRequest> | undefined): boolean;
}

/**
 * @generated from message objectives.v1alpha1.GraphDurationResponse
 */
export declare class GraphDurationResponse extends Message<GraphDurationResponse> {
  /**
   * @generated from field: repeated objectives.v1alpha1.Timeseries timeseries = 1;
   */
  timeseries: Timeseries[];

  constructor(data?: PartialMessage<GraphDurationResponse>);

  static readonly runtime: typeof proto3;
  static readonly typeName = "objectives.v1alpha1.GraphDurationResponse";
  static readonly fields: FieldList;

  static fromBinary(bytes: Uint8Array, options?: Partial<BinaryReadOptions>): GraphDurationResponse;

  static fromJson(jsonValue: JsonValue, options?: Partial<JsonReadOptions>): GraphDurationResponse;

  static fromJsonString(jsonString: string, options?: Partial<JsonReadOptions>): GraphDurationResponse;

  static equals(a: GraphDurationResponse | PlainMessage<GraphDurationResponse> | undefined, b: GraphDurationResponse | PlainMessage<GraphDurationResponse> | undefined): boolean;
}
