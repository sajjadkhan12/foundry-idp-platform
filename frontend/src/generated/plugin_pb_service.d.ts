// package: plugin
// file: plugin.proto

import * as plugin_pb from "./plugin_pb";
import {grpc} from "@improbable-eng/grpc-web";

type PluginServiceUploadPlugin = {
  readonly methodName: string;
  readonly service: typeof PluginService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof plugin_pb.UploadPluginRequest;
  readonly responseType: typeof plugin_pb.PluginVersionResponse;
};

type PluginServiceUploadMicroserviceTemplate = {
  readonly methodName: string;
  readonly service: typeof PluginService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof plugin_pb.UploadMicroserviceTemplateRequest;
  readonly responseType: typeof plugin_pb.PluginVersionResponse;
};

type PluginServiceListPlugins = {
  readonly methodName: string;
  readonly service: typeof PluginService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof plugin_pb.ListPluginsRequest;
  readonly responseType: typeof plugin_pb.ListPluginsResponse;
};

type PluginServiceGetPlugin = {
  readonly methodName: string;
  readonly service: typeof PluginService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof plugin_pb.GetPluginRequest;
  readonly responseType: typeof plugin_pb.PluginResponse;
};

type PluginServiceDeletePlugin = {
  readonly methodName: string;
  readonly service: typeof PluginService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof plugin_pb.DeletePluginRequest;
  readonly responseType: typeof plugin_pb.Empty;
};

type PluginServiceLockPlugin = {
  readonly methodName: string;
  readonly service: typeof PluginService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof plugin_pb.LockPluginRequest;
  readonly responseType: typeof plugin_pb.Empty;
};

type PluginServiceUnlockPlugin = {
  readonly methodName: string;
  readonly service: typeof PluginService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof plugin_pb.UnlockPluginRequest;
  readonly responseType: typeof plugin_pb.Empty;
};

type PluginServiceListPluginVersions = {
  readonly methodName: string;
  readonly service: typeof PluginService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof plugin_pb.ListPluginVersionsRequest;
  readonly responseType: typeof plugin_pb.ListPluginVersionsResponse;
};

type PluginServiceGetPluginVersion = {
  readonly methodName: string;
  readonly service: typeof PluginService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof plugin_pb.GetPluginVersionRequest;
  readonly responseType: typeof plugin_pb.PluginVersionResponse;
};

type PluginServiceRequestPluginAccess = {
  readonly methodName: string;
  readonly service: typeof PluginService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof plugin_pb.RequestPluginAccessRequest;
  readonly responseType: typeof plugin_pb.PluginAccessRequestResponse;
};

type PluginServiceGrantPluginAccess = {
  readonly methodName: string;
  readonly service: typeof PluginService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof plugin_pb.GrantPluginAccessRequest;
  readonly responseType: typeof plugin_pb.PluginAccessResponse;
};

type PluginServiceRejectPluginAccess = {
  readonly methodName: string;
  readonly service: typeof PluginService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof plugin_pb.RejectPluginAccessRequest;
  readonly responseType: typeof plugin_pb.Empty;
};

type PluginServiceRevokePluginAccess = {
  readonly methodName: string;
  readonly service: typeof PluginService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof plugin_pb.RevokePluginAccessRequest;
  readonly responseType: typeof plugin_pb.Empty;
};

type PluginServiceRestorePluginAccess = {
  readonly methodName: string;
  readonly service: typeof PluginService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof plugin_pb.RestorePluginAccessRequest;
  readonly responseType: typeof plugin_pb.Empty;
};

type PluginServiceListAccessRequests = {
  readonly methodName: string;
  readonly service: typeof PluginService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof plugin_pb.ListAccessRequestsRequest;
  readonly responseType: typeof plugin_pb.ListAccessRequestsResponse;
};

type PluginServiceListAccessGrants = {
  readonly methodName: string;
  readonly service: typeof PluginService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof plugin_pb.ListAccessGrantsRequest;
  readonly responseType: typeof plugin_pb.ListAccessGrantsResponse;
};

type PluginServiceProvisionPlugin = {
  readonly methodName: string;
  readonly service: typeof PluginService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof plugin_pb.ProvisionPluginRequest;
  readonly responseType: typeof plugin_pb.ProvisionResponse;
};

type PluginServiceGetJob = {
  readonly methodName: string;
  readonly service: typeof PluginService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof plugin_pb.GetJobRequest;
  readonly responseType: typeof plugin_pb.JobResponse;
};

type PluginServiceListJobs = {
  readonly methodName: string;
  readonly service: typeof PluginService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof plugin_pb.ListJobsRequest;
  readonly responseType: typeof plugin_pb.ListJobsResponse;
};

type PluginServiceGetJobLogs = {
  readonly methodName: string;
  readonly service: typeof PluginService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof plugin_pb.GetJobLogsRequest;
  readonly responseType: typeof plugin_pb.JobLogsResponse;
};

type PluginServiceCancelJob = {
  readonly methodName: string;
  readonly service: typeof PluginService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof plugin_pb.CancelJobRequest;
  readonly responseType: typeof plugin_pb.Empty;
};

type PluginServiceDeleteJob = {
  readonly methodName: string;
  readonly service: typeof PluginService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof plugin_pb.DeleteJobRequest;
  readonly responseType: typeof plugin_pb.Empty;
};

export class PluginService {
  static readonly serviceName: string;
  static readonly UploadPlugin: PluginServiceUploadPlugin;
  static readonly UploadMicroserviceTemplate: PluginServiceUploadMicroserviceTemplate;
  static readonly ListPlugins: PluginServiceListPlugins;
  static readonly GetPlugin: PluginServiceGetPlugin;
  static readonly DeletePlugin: PluginServiceDeletePlugin;
  static readonly LockPlugin: PluginServiceLockPlugin;
  static readonly UnlockPlugin: PluginServiceUnlockPlugin;
  static readonly ListPluginVersions: PluginServiceListPluginVersions;
  static readonly GetPluginVersion: PluginServiceGetPluginVersion;
  static readonly RequestPluginAccess: PluginServiceRequestPluginAccess;
  static readonly GrantPluginAccess: PluginServiceGrantPluginAccess;
  static readonly RejectPluginAccess: PluginServiceRejectPluginAccess;
  static readonly RevokePluginAccess: PluginServiceRevokePluginAccess;
  static readonly RestorePluginAccess: PluginServiceRestorePluginAccess;
  static readonly ListAccessRequests: PluginServiceListAccessRequests;
  static readonly ListAccessGrants: PluginServiceListAccessGrants;
  static readonly ProvisionPlugin: PluginServiceProvisionPlugin;
  static readonly GetJob: PluginServiceGetJob;
  static readonly ListJobs: PluginServiceListJobs;
  static readonly GetJobLogs: PluginServiceGetJobLogs;
  static readonly CancelJob: PluginServiceCancelJob;
  static readonly DeleteJob: PluginServiceDeleteJob;
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

export class PluginServiceClient {
  readonly serviceHost: string;

  constructor(serviceHost: string, options?: grpc.RpcOptions);
  uploadPlugin(
    requestMessage: plugin_pb.UploadPluginRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: plugin_pb.PluginVersionResponse|null) => void
  ): UnaryResponse;
  uploadPlugin(
    requestMessage: plugin_pb.UploadPluginRequest,
    callback: (error: ServiceError|null, responseMessage: plugin_pb.PluginVersionResponse|null) => void
  ): UnaryResponse;
  uploadMicroserviceTemplate(
    requestMessage: plugin_pb.UploadMicroserviceTemplateRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: plugin_pb.PluginVersionResponse|null) => void
  ): UnaryResponse;
  uploadMicroserviceTemplate(
    requestMessage: plugin_pb.UploadMicroserviceTemplateRequest,
    callback: (error: ServiceError|null, responseMessage: plugin_pb.PluginVersionResponse|null) => void
  ): UnaryResponse;
  listPlugins(
    requestMessage: plugin_pb.ListPluginsRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: plugin_pb.ListPluginsResponse|null) => void
  ): UnaryResponse;
  listPlugins(
    requestMessage: plugin_pb.ListPluginsRequest,
    callback: (error: ServiceError|null, responseMessage: plugin_pb.ListPluginsResponse|null) => void
  ): UnaryResponse;
  getPlugin(
    requestMessage: plugin_pb.GetPluginRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: plugin_pb.PluginResponse|null) => void
  ): UnaryResponse;
  getPlugin(
    requestMessage: plugin_pb.GetPluginRequest,
    callback: (error: ServiceError|null, responseMessage: plugin_pb.PluginResponse|null) => void
  ): UnaryResponse;
  deletePlugin(
    requestMessage: plugin_pb.DeletePluginRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: plugin_pb.Empty|null) => void
  ): UnaryResponse;
  deletePlugin(
    requestMessage: plugin_pb.DeletePluginRequest,
    callback: (error: ServiceError|null, responseMessage: plugin_pb.Empty|null) => void
  ): UnaryResponse;
  lockPlugin(
    requestMessage: plugin_pb.LockPluginRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: plugin_pb.Empty|null) => void
  ): UnaryResponse;
  lockPlugin(
    requestMessage: plugin_pb.LockPluginRequest,
    callback: (error: ServiceError|null, responseMessage: plugin_pb.Empty|null) => void
  ): UnaryResponse;
  unlockPlugin(
    requestMessage: plugin_pb.UnlockPluginRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: plugin_pb.Empty|null) => void
  ): UnaryResponse;
  unlockPlugin(
    requestMessage: plugin_pb.UnlockPluginRequest,
    callback: (error: ServiceError|null, responseMessage: plugin_pb.Empty|null) => void
  ): UnaryResponse;
  listPluginVersions(
    requestMessage: plugin_pb.ListPluginVersionsRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: plugin_pb.ListPluginVersionsResponse|null) => void
  ): UnaryResponse;
  listPluginVersions(
    requestMessage: plugin_pb.ListPluginVersionsRequest,
    callback: (error: ServiceError|null, responseMessage: plugin_pb.ListPluginVersionsResponse|null) => void
  ): UnaryResponse;
  getPluginVersion(
    requestMessage: plugin_pb.GetPluginVersionRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: plugin_pb.PluginVersionResponse|null) => void
  ): UnaryResponse;
  getPluginVersion(
    requestMessage: plugin_pb.GetPluginVersionRequest,
    callback: (error: ServiceError|null, responseMessage: plugin_pb.PluginVersionResponse|null) => void
  ): UnaryResponse;
  requestPluginAccess(
    requestMessage: plugin_pb.RequestPluginAccessRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: plugin_pb.PluginAccessRequestResponse|null) => void
  ): UnaryResponse;
  requestPluginAccess(
    requestMessage: plugin_pb.RequestPluginAccessRequest,
    callback: (error: ServiceError|null, responseMessage: plugin_pb.PluginAccessRequestResponse|null) => void
  ): UnaryResponse;
  grantPluginAccess(
    requestMessage: plugin_pb.GrantPluginAccessRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: plugin_pb.PluginAccessResponse|null) => void
  ): UnaryResponse;
  grantPluginAccess(
    requestMessage: plugin_pb.GrantPluginAccessRequest,
    callback: (error: ServiceError|null, responseMessage: plugin_pb.PluginAccessResponse|null) => void
  ): UnaryResponse;
  rejectPluginAccess(
    requestMessage: plugin_pb.RejectPluginAccessRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: plugin_pb.Empty|null) => void
  ): UnaryResponse;
  rejectPluginAccess(
    requestMessage: plugin_pb.RejectPluginAccessRequest,
    callback: (error: ServiceError|null, responseMessage: plugin_pb.Empty|null) => void
  ): UnaryResponse;
  revokePluginAccess(
    requestMessage: plugin_pb.RevokePluginAccessRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: plugin_pb.Empty|null) => void
  ): UnaryResponse;
  revokePluginAccess(
    requestMessage: plugin_pb.RevokePluginAccessRequest,
    callback: (error: ServiceError|null, responseMessage: plugin_pb.Empty|null) => void
  ): UnaryResponse;
  restorePluginAccess(
    requestMessage: plugin_pb.RestorePluginAccessRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: plugin_pb.Empty|null) => void
  ): UnaryResponse;
  restorePluginAccess(
    requestMessage: plugin_pb.RestorePluginAccessRequest,
    callback: (error: ServiceError|null, responseMessage: plugin_pb.Empty|null) => void
  ): UnaryResponse;
  listAccessRequests(
    requestMessage: plugin_pb.ListAccessRequestsRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: plugin_pb.ListAccessRequestsResponse|null) => void
  ): UnaryResponse;
  listAccessRequests(
    requestMessage: plugin_pb.ListAccessRequestsRequest,
    callback: (error: ServiceError|null, responseMessage: plugin_pb.ListAccessRequestsResponse|null) => void
  ): UnaryResponse;
  listAccessGrants(
    requestMessage: plugin_pb.ListAccessGrantsRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: plugin_pb.ListAccessGrantsResponse|null) => void
  ): UnaryResponse;
  listAccessGrants(
    requestMessage: plugin_pb.ListAccessGrantsRequest,
    callback: (error: ServiceError|null, responseMessage: plugin_pb.ListAccessGrantsResponse|null) => void
  ): UnaryResponse;
  provisionPlugin(
    requestMessage: plugin_pb.ProvisionPluginRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: plugin_pb.ProvisionResponse|null) => void
  ): UnaryResponse;
  provisionPlugin(
    requestMessage: plugin_pb.ProvisionPluginRequest,
    callback: (error: ServiceError|null, responseMessage: plugin_pb.ProvisionResponse|null) => void
  ): UnaryResponse;
  getJob(
    requestMessage: plugin_pb.GetJobRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: plugin_pb.JobResponse|null) => void
  ): UnaryResponse;
  getJob(
    requestMessage: plugin_pb.GetJobRequest,
    callback: (error: ServiceError|null, responseMessage: plugin_pb.JobResponse|null) => void
  ): UnaryResponse;
  listJobs(
    requestMessage: plugin_pb.ListJobsRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: plugin_pb.ListJobsResponse|null) => void
  ): UnaryResponse;
  listJobs(
    requestMessage: plugin_pb.ListJobsRequest,
    callback: (error: ServiceError|null, responseMessage: plugin_pb.ListJobsResponse|null) => void
  ): UnaryResponse;
  getJobLogs(
    requestMessage: plugin_pb.GetJobLogsRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: plugin_pb.JobLogsResponse|null) => void
  ): UnaryResponse;
  getJobLogs(
    requestMessage: plugin_pb.GetJobLogsRequest,
    callback: (error: ServiceError|null, responseMessage: plugin_pb.JobLogsResponse|null) => void
  ): UnaryResponse;
  cancelJob(
    requestMessage: plugin_pb.CancelJobRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: plugin_pb.Empty|null) => void
  ): UnaryResponse;
  cancelJob(
    requestMessage: plugin_pb.CancelJobRequest,
    callback: (error: ServiceError|null, responseMessage: plugin_pb.Empty|null) => void
  ): UnaryResponse;
  deleteJob(
    requestMessage: plugin_pb.DeleteJobRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: plugin_pb.Empty|null) => void
  ): UnaryResponse;
  deleteJob(
    requestMessage: plugin_pb.DeleteJobRequest,
    callback: (error: ServiceError|null, responseMessage: plugin_pb.Empty|null) => void
  ): UnaryResponse;
}

