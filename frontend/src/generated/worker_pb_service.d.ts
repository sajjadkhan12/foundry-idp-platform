// package: worker
// file: worker.proto

import * as worker_pb from "./worker_pb";
import {grpc} from "@improbable-eng/grpc-web";

type WorkerServiceProvisionInfrastructure = {
  readonly methodName: string;
  readonly service: typeof WorkerService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof worker_pb.ProvisionInfrastructureRequest;
  readonly responseType: typeof worker_pb.TaskResponse;
};

type WorkerServiceDestroyInfrastructure = {
  readonly methodName: string;
  readonly service: typeof WorkerService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof worker_pb.DestroyInfrastructureRequest;
  readonly responseType: typeof worker_pb.TaskResponse;
};

type WorkerServiceProvisionMicroservice = {
  readonly methodName: string;
  readonly service: typeof WorkerService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof worker_pb.ProvisionMicroserviceRequest;
  readonly responseType: typeof worker_pb.TaskResponse;
};

type WorkerServiceDestroyMicroservice = {
  readonly methodName: string;
  readonly service: typeof WorkerService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof worker_pb.DestroyMicroserviceRequest;
  readonly responseType: typeof worker_pb.TaskResponse;
};

type WorkerServiceCleanupStuckDeployments = {
  readonly methodName: string;
  readonly service: typeof WorkerService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof worker_pb.Empty;
  readonly responseType: typeof worker_pb.TaskResponse;
};

type WorkerServiceCleanupExpiredRefreshTokens = {
  readonly methodName: string;
  readonly service: typeof WorkerService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof worker_pb.Empty;
  readonly responseType: typeof worker_pb.TaskResponse;
};

type WorkerServicePollGitHubActionsStatus = {
  readonly methodName: string;
  readonly service: typeof WorkerService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof worker_pb.Empty;
  readonly responseType: typeof worker_pb.TaskResponse;
};

type WorkerServiceProcessGitHubWebhook = {
  readonly methodName: string;
  readonly service: typeof WorkerService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof worker_pb.ProcessGitHubWebhookRequest;
  readonly responseType: typeof worker_pb.ProcessGitHubWebhookResponse;
};

type WorkerServiceGetTaskStatus = {
  readonly methodName: string;
  readonly service: typeof WorkerService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof worker_pb.GetTaskStatusRequest;
  readonly responseType: typeof worker_pb.TaskStatusResponse;
};

export class WorkerService {
  static readonly serviceName: string;
  static readonly ProvisionInfrastructure: WorkerServiceProvisionInfrastructure;
  static readonly DestroyInfrastructure: WorkerServiceDestroyInfrastructure;
  static readonly ProvisionMicroservice: WorkerServiceProvisionMicroservice;
  static readonly DestroyMicroservice: WorkerServiceDestroyMicroservice;
  static readonly CleanupStuckDeployments: WorkerServiceCleanupStuckDeployments;
  static readonly CleanupExpiredRefreshTokens: WorkerServiceCleanupExpiredRefreshTokens;
  static readonly PollGitHubActionsStatus: WorkerServicePollGitHubActionsStatus;
  static readonly ProcessGitHubWebhook: WorkerServiceProcessGitHubWebhook;
  static readonly GetTaskStatus: WorkerServiceGetTaskStatus;
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

export class WorkerServiceClient {
  readonly serviceHost: string;

  constructor(serviceHost: string, options?: grpc.RpcOptions);
  provisionInfrastructure(
    requestMessage: worker_pb.ProvisionInfrastructureRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: worker_pb.TaskResponse|null) => void
  ): UnaryResponse;
  provisionInfrastructure(
    requestMessage: worker_pb.ProvisionInfrastructureRequest,
    callback: (error: ServiceError|null, responseMessage: worker_pb.TaskResponse|null) => void
  ): UnaryResponse;
  destroyInfrastructure(
    requestMessage: worker_pb.DestroyInfrastructureRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: worker_pb.TaskResponse|null) => void
  ): UnaryResponse;
  destroyInfrastructure(
    requestMessage: worker_pb.DestroyInfrastructureRequest,
    callback: (error: ServiceError|null, responseMessage: worker_pb.TaskResponse|null) => void
  ): UnaryResponse;
  provisionMicroservice(
    requestMessage: worker_pb.ProvisionMicroserviceRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: worker_pb.TaskResponse|null) => void
  ): UnaryResponse;
  provisionMicroservice(
    requestMessage: worker_pb.ProvisionMicroserviceRequest,
    callback: (error: ServiceError|null, responseMessage: worker_pb.TaskResponse|null) => void
  ): UnaryResponse;
  destroyMicroservice(
    requestMessage: worker_pb.DestroyMicroserviceRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: worker_pb.TaskResponse|null) => void
  ): UnaryResponse;
  destroyMicroservice(
    requestMessage: worker_pb.DestroyMicroserviceRequest,
    callback: (error: ServiceError|null, responseMessage: worker_pb.TaskResponse|null) => void
  ): UnaryResponse;
  cleanupStuckDeployments(
    requestMessage: worker_pb.Empty,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: worker_pb.TaskResponse|null) => void
  ): UnaryResponse;
  cleanupStuckDeployments(
    requestMessage: worker_pb.Empty,
    callback: (error: ServiceError|null, responseMessage: worker_pb.TaskResponse|null) => void
  ): UnaryResponse;
  cleanupExpiredRefreshTokens(
    requestMessage: worker_pb.Empty,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: worker_pb.TaskResponse|null) => void
  ): UnaryResponse;
  cleanupExpiredRefreshTokens(
    requestMessage: worker_pb.Empty,
    callback: (error: ServiceError|null, responseMessage: worker_pb.TaskResponse|null) => void
  ): UnaryResponse;
  pollGitHubActionsStatus(
    requestMessage: worker_pb.Empty,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: worker_pb.TaskResponse|null) => void
  ): UnaryResponse;
  pollGitHubActionsStatus(
    requestMessage: worker_pb.Empty,
    callback: (error: ServiceError|null, responseMessage: worker_pb.TaskResponse|null) => void
  ): UnaryResponse;
  processGitHubWebhook(
    requestMessage: worker_pb.ProcessGitHubWebhookRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: worker_pb.ProcessGitHubWebhookResponse|null) => void
  ): UnaryResponse;
  processGitHubWebhook(
    requestMessage: worker_pb.ProcessGitHubWebhookRequest,
    callback: (error: ServiceError|null, responseMessage: worker_pb.ProcessGitHubWebhookResponse|null) => void
  ): UnaryResponse;
  getTaskStatus(
    requestMessage: worker_pb.GetTaskStatusRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: worker_pb.TaskStatusResponse|null) => void
  ): UnaryResponse;
  getTaskStatus(
    requestMessage: worker_pb.GetTaskStatusRequest,
    callback: (error: ServiceError|null, responseMessage: worker_pb.TaskStatusResponse|null) => void
  ): UnaryResponse;
}

