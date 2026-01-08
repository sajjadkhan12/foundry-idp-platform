// package: deployment
// file: deployment.proto

import * as deployment_pb from "./deployment_pb";
import {grpc} from "@improbable-eng/grpc-web";

type DeploymentServiceCreateDeployment = {
  readonly methodName: string;
  readonly service: typeof DeploymentService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof deployment_pb.CreateDeploymentRequest;
  readonly responseType: typeof deployment_pb.DeploymentResponse;
};

type DeploymentServiceGetDeployment = {
  readonly methodName: string;
  readonly service: typeof DeploymentService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof deployment_pb.GetDeploymentRequest;
  readonly responseType: typeof deployment_pb.DeploymentResponse;
};

type DeploymentServiceUpdateDeployment = {
  readonly methodName: string;
  readonly service: typeof DeploymentService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof deployment_pb.UpdateDeploymentRequest;
  readonly responseType: typeof deployment_pb.DeploymentResponse;
};

type DeploymentServiceDeleteDeployment = {
  readonly methodName: string;
  readonly service: typeof DeploymentService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof deployment_pb.DeleteDeploymentRequest;
  readonly responseType: typeof deployment_pb.Empty;
};

type DeploymentServiceListDeployments = {
  readonly methodName: string;
  readonly service: typeof DeploymentService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof deployment_pb.ListDeploymentsRequest;
  readonly responseType: typeof deployment_pb.ListDeploymentsResponse;
};

type DeploymentServiceGetDeploymentHistory = {
  readonly methodName: string;
  readonly service: typeof DeploymentService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof deployment_pb.GetDeploymentHistoryRequest;
  readonly responseType: typeof deployment_pb.ListDeploymentHistoryResponse;
};

type DeploymentServiceGetDeploymentHistoryVersion = {
  readonly methodName: string;
  readonly service: typeof DeploymentService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof deployment_pb.GetDeploymentHistoryVersionRequest;
  readonly responseType: typeof deployment_pb.DeploymentHistoryResponse;
};

type DeploymentServiceAddDeploymentTag = {
  readonly methodName: string;
  readonly service: typeof DeploymentService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof deployment_pb.AddDeploymentTagRequest;
  readonly responseType: typeof deployment_pb.Empty;
};

type DeploymentServiceRemoveDeploymentTag = {
  readonly methodName: string;
  readonly service: typeof DeploymentService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof deployment_pb.RemoveDeploymentTagRequest;
  readonly responseType: typeof deployment_pb.Empty;
};

type DeploymentServiceListDeploymentTags = {
  readonly methodName: string;
  readonly service: typeof DeploymentService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof deployment_pb.ListDeploymentTagsRequest;
  readonly responseType: typeof deployment_pb.ListDeploymentTagsResponse;
};

type DeploymentServiceUpdateCICDStatus = {
  readonly methodName: string;
  readonly service: typeof DeploymentService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof deployment_pb.UpdateCICDStatusRequest;
  readonly responseType: typeof deployment_pb.Empty;
};

type DeploymentServiceGetCICDStatus = {
  readonly methodName: string;
  readonly service: typeof DeploymentService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof deployment_pb.GetCICDStatusRequest;
  readonly responseType: typeof deployment_pb.CICDStatusResponse;
};

type DeploymentServiceGetDeploymentStats = {
  readonly methodName: string;
  readonly service: typeof DeploymentService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof deployment_pb.GetDeploymentStatsRequest;
  readonly responseType: typeof deployment_pb.DeploymentStatsResponse;
};

type DeploymentServiceGetDeploymentCosts = {
  readonly methodName: string;
  readonly service: typeof DeploymentService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof deployment_pb.GetDeploymentCostsRequest;
  readonly responseType: typeof deployment_pb.DeploymentCostsResponse;
};

export class DeploymentService {
  static readonly serviceName: string;
  static readonly CreateDeployment: DeploymentServiceCreateDeployment;
  static readonly GetDeployment: DeploymentServiceGetDeployment;
  static readonly UpdateDeployment: DeploymentServiceUpdateDeployment;
  static readonly DeleteDeployment: DeploymentServiceDeleteDeployment;
  static readonly ListDeployments: DeploymentServiceListDeployments;
  static readonly GetDeploymentHistory: DeploymentServiceGetDeploymentHistory;
  static readonly GetDeploymentHistoryVersion: DeploymentServiceGetDeploymentHistoryVersion;
  static readonly AddDeploymentTag: DeploymentServiceAddDeploymentTag;
  static readonly RemoveDeploymentTag: DeploymentServiceRemoveDeploymentTag;
  static readonly ListDeploymentTags: DeploymentServiceListDeploymentTags;
  static readonly UpdateCICDStatus: DeploymentServiceUpdateCICDStatus;
  static readonly GetCICDStatus: DeploymentServiceGetCICDStatus;
  static readonly GetDeploymentStats: DeploymentServiceGetDeploymentStats;
  static readonly GetDeploymentCosts: DeploymentServiceGetDeploymentCosts;
}

export type ServiceError = { message: string, code: number; metadata: grpc.Metadata }
export type Status = { details: string, code: number; metadata: grpc.Metadata }

interface UnaryResponse {
  cancel(): void;
}
interface ResponseStream<T> {
  cancel(): void;
  on(type: 'data', handler: (message: T) => void): ResponseStream<T>;
  on(type: 'end', handler: (status?: Status) => void): ResponseStream<T>;
  on(type: 'status', handler: (status: Status) => void): ResponseStream<T>;
}
interface RequestStream<T> {
  write(message: T): RequestStream<T>;
  end(): void;
  cancel(): void;
  on(type: 'end', handler: (status?: Status) => void): RequestStream<T>;
  on(type: 'status', handler: (status: Status) => void): RequestStream<T>;
}
interface BidirectionalStream<ReqT, ResT> {
  write(message: ReqT): BidirectionalStream<ReqT, ResT>;
  end(): void;
  cancel(): void;
  on(type: 'data', handler: (message: ResT) => void): BidirectionalStream<ReqT, ResT>;
  on(type: 'end', handler: (status?: Status) => void): BidirectionalStream<ReqT, ResT>;
  on(type: 'status', handler: (status: Status) => void): BidirectionalStream<ReqT, ResT>;
}

export class DeploymentServiceClient {
  readonly serviceHost: string;

  constructor(serviceHost: string, options?: grpc.RpcOptions);
  createDeployment(
    requestMessage: deployment_pb.CreateDeploymentRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: deployment_pb.DeploymentResponse|null) => void
  ): UnaryResponse;
  createDeployment(
    requestMessage: deployment_pb.CreateDeploymentRequest,
    callback: (error: ServiceError|null, responseMessage: deployment_pb.DeploymentResponse|null) => void
  ): UnaryResponse;
  getDeployment(
    requestMessage: deployment_pb.GetDeploymentRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: deployment_pb.DeploymentResponse|null) => void
  ): UnaryResponse;
  getDeployment(
    requestMessage: deployment_pb.GetDeploymentRequest,
    callback: (error: ServiceError|null, responseMessage: deployment_pb.DeploymentResponse|null) => void
  ): UnaryResponse;
  updateDeployment(
    requestMessage: deployment_pb.UpdateDeploymentRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: deployment_pb.DeploymentResponse|null) => void
  ): UnaryResponse;
  updateDeployment(
    requestMessage: deployment_pb.UpdateDeploymentRequest,
    callback: (error: ServiceError|null, responseMessage: deployment_pb.DeploymentResponse|null) => void
  ): UnaryResponse;
  deleteDeployment(
    requestMessage: deployment_pb.DeleteDeploymentRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: deployment_pb.Empty|null) => void
  ): UnaryResponse;
  deleteDeployment(
    requestMessage: deployment_pb.DeleteDeploymentRequest,
    callback: (error: ServiceError|null, responseMessage: deployment_pb.Empty|null) => void
  ): UnaryResponse;
  listDeployments(
    requestMessage: deployment_pb.ListDeploymentsRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: deployment_pb.ListDeploymentsResponse|null) => void
  ): UnaryResponse;
  listDeployments(
    requestMessage: deployment_pb.ListDeploymentsRequest,
    callback: (error: ServiceError|null, responseMessage: deployment_pb.ListDeploymentsResponse|null) => void
  ): UnaryResponse;
  getDeploymentHistory(
    requestMessage: deployment_pb.GetDeploymentHistoryRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: deployment_pb.ListDeploymentHistoryResponse|null) => void
  ): UnaryResponse;
  getDeploymentHistory(
    requestMessage: deployment_pb.GetDeploymentHistoryRequest,
    callback: (error: ServiceError|null, responseMessage: deployment_pb.ListDeploymentHistoryResponse|null) => void
  ): UnaryResponse;
  getDeploymentHistoryVersion(
    requestMessage: deployment_pb.GetDeploymentHistoryVersionRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: deployment_pb.DeploymentHistoryResponse|null) => void
  ): UnaryResponse;
  getDeploymentHistoryVersion(
    requestMessage: deployment_pb.GetDeploymentHistoryVersionRequest,
    callback: (error: ServiceError|null, responseMessage: deployment_pb.DeploymentHistoryResponse|null) => void
  ): UnaryResponse;
  addDeploymentTag(
    requestMessage: deployment_pb.AddDeploymentTagRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: deployment_pb.Empty|null) => void
  ): UnaryResponse;
  addDeploymentTag(
    requestMessage: deployment_pb.AddDeploymentTagRequest,
    callback: (error: ServiceError|null, responseMessage: deployment_pb.Empty|null) => void
  ): UnaryResponse;
  removeDeploymentTag(
    requestMessage: deployment_pb.RemoveDeploymentTagRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: deployment_pb.Empty|null) => void
  ): UnaryResponse;
  removeDeploymentTag(
    requestMessage: deployment_pb.RemoveDeploymentTagRequest,
    callback: (error: ServiceError|null, responseMessage: deployment_pb.Empty|null) => void
  ): UnaryResponse;
  listDeploymentTags(
    requestMessage: deployment_pb.ListDeploymentTagsRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: deployment_pb.ListDeploymentTagsResponse|null) => void
  ): UnaryResponse;
  listDeploymentTags(
    requestMessage: deployment_pb.ListDeploymentTagsRequest,
    callback: (error: ServiceError|null, responseMessage: deployment_pb.ListDeploymentTagsResponse|null) => void
  ): UnaryResponse;
  updateCICDStatus(
    requestMessage: deployment_pb.UpdateCICDStatusRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: deployment_pb.Empty|null) => void
  ): UnaryResponse;
  updateCICDStatus(
    requestMessage: deployment_pb.UpdateCICDStatusRequest,
    callback: (error: ServiceError|null, responseMessage: deployment_pb.Empty|null) => void
  ): UnaryResponse;
  getCICDStatus(
    requestMessage: deployment_pb.GetCICDStatusRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: deployment_pb.CICDStatusResponse|null) => void
  ): UnaryResponse;
  getCICDStatus(
    requestMessage: deployment_pb.GetCICDStatusRequest,
    callback: (error: ServiceError|null, responseMessage: deployment_pb.CICDStatusResponse|null) => void
  ): UnaryResponse;
  getDeploymentStats(
    requestMessage: deployment_pb.GetDeploymentStatsRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: deployment_pb.DeploymentStatsResponse|null) => void
  ): UnaryResponse;
  getDeploymentStats(
    requestMessage: deployment_pb.GetDeploymentStatsRequest,
    callback: (error: ServiceError|null, responseMessage: deployment_pb.DeploymentStatsResponse|null) => void
  ): UnaryResponse;
  getDeploymentCosts(
    requestMessage: deployment_pb.GetDeploymentCostsRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: deployment_pb.DeploymentCostsResponse|null) => void
  ): UnaryResponse;
  getDeploymentCosts(
    requestMessage: deployment_pb.GetDeploymentCostsRequest,
    callback: (error: ServiceError|null, responseMessage: deployment_pb.DeploymentCostsResponse|null) => void
  ): UnaryResponse;
}

