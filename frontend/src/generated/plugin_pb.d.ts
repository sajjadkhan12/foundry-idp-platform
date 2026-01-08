// package: plugin
// file: plugin.proto

import * as jspb from "google-protobuf";

export class Empty extends jspb.Message {
  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): Empty.AsObject;
  static toObject(includeInstance: boolean, msg: Empty): Empty.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: Empty, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): Empty;
  static deserializeBinaryFromReader(message: Empty, reader: jspb.BinaryReader): Empty;
}

export namespace Empty {
  export type AsObject = {
  }
}

export class UploadPluginRequest extends jspb.Message {
  getFileContent(): Uint8Array | string;
  getFileContent_asU8(): Uint8Array;
  getFileContent_asB64(): string;
  setFileContent(value: Uint8Array | string): void;

  getFilename(): string;
  setFilename(value: string): void;

  getGitRepoUrl(): string;
  setGitRepoUrl(value: string): void;

  getGitBranch(): string;
  setGitBranch(value: string): void;

  getUserId(): string;
  setUserId(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): UploadPluginRequest.AsObject;
  static toObject(includeInstance: boolean, msg: UploadPluginRequest): UploadPluginRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: UploadPluginRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): UploadPluginRequest;
  static deserializeBinaryFromReader(message: UploadPluginRequest, reader: jspb.BinaryReader): UploadPluginRequest;
}

export namespace UploadPluginRequest {
  export type AsObject = {
    fileContent: Uint8Array | string,
    filename: string,
    gitRepoUrl: string,
    gitBranch: string,
    userId: string,
  }
}

export class UploadMicroserviceTemplateRequest extends jspb.Message {
  getPluginId(): string;
  setPluginId(value: string): void;

  getName(): string;
  setName(value: string): void;

  getVersion(): string;
  setVersion(value: string): void;

  getDescription(): string;
  setDescription(value: string): void;

  getTemplateRepoUrl(): string;
  setTemplateRepoUrl(value: string): void;

  getTemplatePath(): string;
  setTemplatePath(value: string): void;

  getAuthor(): string;
  setAuthor(value: string): void;

  getUserId(): string;
  setUserId(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): UploadMicroserviceTemplateRequest.AsObject;
  static toObject(includeInstance: boolean, msg: UploadMicroserviceTemplateRequest): UploadMicroserviceTemplateRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: UploadMicroserviceTemplateRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): UploadMicroserviceTemplateRequest;
  static deserializeBinaryFromReader(message: UploadMicroserviceTemplateRequest, reader: jspb.BinaryReader): UploadMicroserviceTemplateRequest;
}

export namespace UploadMicroserviceTemplateRequest {
  export type AsObject = {
    pluginId: string,
    name: string,
    version: string,
    description: string,
    templateRepoUrl: string,
    templatePath: string,
    author: string,
    userId: string,
  }
}

export class PluginVersionResponse extends jspb.Message {
  getId(): number;
  setId(value: number): void;

  getPluginId(): string;
  setPluginId(value: string): void;

  getVersion(): string;
  setVersion(value: string): void;

  getManifest(): string;
  setManifest(value: string): void;

  getStoragePath(): string;
  setStoragePath(value: string): void;

  getGitRepoUrl(): string;
  setGitRepoUrl(value: string): void;

  getGitBranch(): string;
  setGitBranch(value: string): void;

  getTemplateRepoUrl(): string;
  setTemplateRepoUrl(value: string): void;

  getTemplatePath(): string;
  setTemplatePath(value: string): void;

  getCreatedAt(): string;
  setCreatedAt(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): PluginVersionResponse.AsObject;
  static toObject(includeInstance: boolean, msg: PluginVersionResponse): PluginVersionResponse.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: PluginVersionResponse, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): PluginVersionResponse;
  static deserializeBinaryFromReader(message: PluginVersionResponse, reader: jspb.BinaryReader): PluginVersionResponse;
}

export namespace PluginVersionResponse {
  export type AsObject = {
    id: number,
    pluginId: string,
    version: string,
    manifest: string,
    storagePath: string,
    gitRepoUrl: string,
    gitBranch: string,
    templateRepoUrl: string,
    templatePath: string,
    createdAt: string,
  }
}

export class ProvisionPluginRequest extends jspb.Message {
  getPluginId(): string;
  setPluginId(value: string): void;

  getVersion(): string;
  setVersion(value: string): void;

  getInputs(): string;
  setInputs(value: string): void;

  getEnvironment(): string;
  setEnvironment(value: string): void;

  getTags(): string;
  setTags(value: string): void;

  getDeploymentName(): string;
  setDeploymentName(value: string): void;

  getCostCenter(): string;
  setCostCenter(value: string): void;

  getProjectCode(): string;
  setProjectCode(value: string): void;

  getUserId(): string;
  setUserId(value: string): void;

  getUserEmail(): string;
  setUserEmail(value: string): void;

  getBusinessUnitId(): string;
  setBusinessUnitId(value: string): void;

  getOrganizationId(): string;
  setOrganizationId(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): ProvisionPluginRequest.AsObject;
  static toObject(includeInstance: boolean, msg: ProvisionPluginRequest): ProvisionPluginRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: ProvisionPluginRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): ProvisionPluginRequest;
  static deserializeBinaryFromReader(message: ProvisionPluginRequest, reader: jspb.BinaryReader): ProvisionPluginRequest;
}

export namespace ProvisionPluginRequest {
  export type AsObject = {
    pluginId: string,
    version: string,
    inputs: string,
    environment: string,
    tags: string,
    deploymentName: string,
    costCenter: string,
    projectCode: string,
    userId: string,
    userEmail: string,
    businessUnitId: string,
    organizationId: string,
  }
}

export class ProvisionResponse extends jspb.Message {
  getJobId(): string;
  setJobId(value: string): void;

  getDeploymentId(): string;
  setDeploymentId(value: string): void;

  getStatus(): string;
  setStatus(value: string): void;

  getMessage(): string;
  setMessage(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): ProvisionResponse.AsObject;
  static toObject(includeInstance: boolean, msg: ProvisionResponse): ProvisionResponse.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: ProvisionResponse, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): ProvisionResponse;
  static deserializeBinaryFromReader(message: ProvisionResponse, reader: jspb.BinaryReader): ProvisionResponse;
}

export namespace ProvisionResponse {
  export type AsObject = {
    jobId: string,
    deploymentId: string,
    status: string,
    message: string,
  }
}

export class GetJobRequest extends jspb.Message {
  getJobId(): string;
  setJobId(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): GetJobRequest.AsObject;
  static toObject(includeInstance: boolean, msg: GetJobRequest): GetJobRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: GetJobRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): GetJobRequest;
  static deserializeBinaryFromReader(message: GetJobRequest, reader: jspb.BinaryReader): GetJobRequest;
}

export namespace GetJobRequest {
  export type AsObject = {
    jobId: string,
  }
}

export class ListJobsRequest extends jspb.Message {
  getUserId(): string;
  setUserId(value: string): void;

  getBusinessUnitId(): string;
  setBusinessUnitId(value: string): void;

  getSkip(): number;
  setSkip(value: number): void;

  getLimit(): number;
  setLimit(value: number): void;

  getStatus(): string;
  setStatus(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): ListJobsRequest.AsObject;
  static toObject(includeInstance: boolean, msg: ListJobsRequest): ListJobsRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: ListJobsRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): ListJobsRequest;
  static deserializeBinaryFromReader(message: ListJobsRequest, reader: jspb.BinaryReader): ListJobsRequest;
}

export namespace ListJobsRequest {
  export type AsObject = {
    userId: string,
    businessUnitId: string,
    skip: number,
    limit: number,
    status: string,
  }
}

export class GetJobLogsRequest extends jspb.Message {
  getJobId(): string;
  setJobId(value: string): void;

  getSkip(): number;
  setSkip(value: number): void;

  getLimit(): number;
  setLimit(value: number): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): GetJobLogsRequest.AsObject;
  static toObject(includeInstance: boolean, msg: GetJobLogsRequest): GetJobLogsRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: GetJobLogsRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): GetJobLogsRequest;
  static deserializeBinaryFromReader(message: GetJobLogsRequest, reader: jspb.BinaryReader): GetJobLogsRequest;
}

export namespace GetJobLogsRequest {
  export type AsObject = {
    jobId: string,
    skip: number,
    limit: number,
  }
}

export class CancelJobRequest extends jspb.Message {
  getJobId(): string;
  setJobId(value: string): void;

  getUserId(): string;
  setUserId(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): CancelJobRequest.AsObject;
  static toObject(includeInstance: boolean, msg: CancelJobRequest): CancelJobRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: CancelJobRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): CancelJobRequest;
  static deserializeBinaryFromReader(message: CancelJobRequest, reader: jspb.BinaryReader): CancelJobRequest;
}

export namespace CancelJobRequest {
  export type AsObject = {
    jobId: string,
    userId: string,
  }
}

export class DeleteJobRequest extends jspb.Message {
  getJobId(): string;
  setJobId(value: string): void;

  getUserId(): string;
  setUserId(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): DeleteJobRequest.AsObject;
  static toObject(includeInstance: boolean, msg: DeleteJobRequest): DeleteJobRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: DeleteJobRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): DeleteJobRequest;
  static deserializeBinaryFromReader(message: DeleteJobRequest, reader: jspb.BinaryReader): DeleteJobRequest;
}

export namespace DeleteJobRequest {
  export type AsObject = {
    jobId: string,
    userId: string,
  }
}

export class JobResponse extends jspb.Message {
  getId(): string;
  setId(value: string): void;

  getPluginVersionId(): number;
  setPluginVersionId(value: number): void;

  getDeploymentId(): string;
  setDeploymentId(value: string): void;

  getStatus(): string;
  setStatus(value: string): void;

  getTriggeredBy(): string;
  setTriggeredBy(value: string): void;

  getInputs(): string;
  setInputs(value: string): void;

  getOutputs(): string;
  setOutputs(value: string): void;

  getRetryCount(): number;
  setRetryCount(value: number): void;

  getErrorState(): string;
  setErrorState(value: string): void;

  getErrorMessage(): string;
  setErrorMessage(value: string): void;

  getCreatedAt(): string;
  setCreatedAt(value: string): void;

  getFinishedAt(): string;
  setFinishedAt(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): JobResponse.AsObject;
  static toObject(includeInstance: boolean, msg: JobResponse): JobResponse.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: JobResponse, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): JobResponse;
  static deserializeBinaryFromReader(message: JobResponse, reader: jspb.BinaryReader): JobResponse;
}

export namespace JobResponse {
  export type AsObject = {
    id: string,
    pluginVersionId: number,
    deploymentId: string,
    status: string,
    triggeredBy: string,
    inputs: string,
    outputs: string,
    retryCount: number,
    errorState: string,
    errorMessage: string,
    createdAt: string,
    finishedAt: string,
  }
}

export class ListJobsResponse extends jspb.Message {
  clearJobsList(): void;
  getJobsList(): Array<JobResponse>;
  setJobsList(value: Array<JobResponse>): void;
  addJobs(value?: JobResponse, index?: number): JobResponse;

  getTotal(): number;
  setTotal(value: number): void;

  getSkip(): number;
  setSkip(value: number): void;

  getLimit(): number;
  setLimit(value: number): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): ListJobsResponse.AsObject;
  static toObject(includeInstance: boolean, msg: ListJobsResponse): ListJobsResponse.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: ListJobsResponse, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): ListJobsResponse;
  static deserializeBinaryFromReader(message: ListJobsResponse, reader: jspb.BinaryReader): ListJobsResponse;
}

export namespace ListJobsResponse {
  export type AsObject = {
    jobsList: Array<JobResponse.AsObject>,
    total: number,
    skip: number,
    limit: number,
  }
}

export class JobLogResponse extends jspb.Message {
  getId(): number;
  setId(value: number): void;

  getJobId(): string;
  setJobId(value: string): void;

  getTimestamp(): string;
  setTimestamp(value: string): void;

  getLevel(): string;
  setLevel(value: string): void;

  getMessage(): string;
  setMessage(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): JobLogResponse.AsObject;
  static toObject(includeInstance: boolean, msg: JobLogResponse): JobLogResponse.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: JobLogResponse, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): JobLogResponse;
  static deserializeBinaryFromReader(message: JobLogResponse, reader: jspb.BinaryReader): JobLogResponse;
}

export namespace JobLogResponse {
  export type AsObject = {
    id: number,
    jobId: string,
    timestamp: string,
    level: string,
    message: string,
  }
}

export class JobLogsResponse extends jspb.Message {
  clearLogsList(): void;
  getLogsList(): Array<JobLogResponse>;
  setLogsList(value: Array<JobLogResponse>): void;
  addLogs(value?: JobLogResponse, index?: number): JobLogResponse;

  getTotal(): number;
  setTotal(value: number): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): JobLogsResponse.AsObject;
  static toObject(includeInstance: boolean, msg: JobLogsResponse): JobLogsResponse.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: JobLogsResponse, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): JobLogsResponse;
  static deserializeBinaryFromReader(message: JobLogsResponse, reader: jspb.BinaryReader): JobLogsResponse;
}

export namespace JobLogsResponse {
  export type AsObject = {
    logsList: Array<JobLogResponse.AsObject>,
    total: number,
  }
}

export class ListPluginsRequest extends jspb.Message {
  getUserId(): string;
  setUserId(value: string): void;

  getBusinessUnitId(): string;
  setBusinessUnitId(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): ListPluginsRequest.AsObject;
  static toObject(includeInstance: boolean, msg: ListPluginsRequest): ListPluginsRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: ListPluginsRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): ListPluginsRequest;
  static deserializeBinaryFromReader(message: ListPluginsRequest, reader: jspb.BinaryReader): ListPluginsRequest;
}

export namespace ListPluginsRequest {
  export type AsObject = {
    userId: string,
    businessUnitId: string,
  }
}

export class GetPluginRequest extends jspb.Message {
  getPluginId(): string;
  setPluginId(value: string): void;

  getUserId(): string;
  setUserId(value: string): void;

  getBusinessUnitId(): string;
  setBusinessUnitId(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): GetPluginRequest.AsObject;
  static toObject(includeInstance: boolean, msg: GetPluginRequest): GetPluginRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: GetPluginRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): GetPluginRequest;
  static deserializeBinaryFromReader(message: GetPluginRequest, reader: jspb.BinaryReader): GetPluginRequest;
}

export namespace GetPluginRequest {
  export type AsObject = {
    pluginId: string,
    userId: string,
    businessUnitId: string,
  }
}

export class DeletePluginRequest extends jspb.Message {
  getPluginId(): string;
  setPluginId(value: string): void;

  getUserId(): string;
  setUserId(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): DeletePluginRequest.AsObject;
  static toObject(includeInstance: boolean, msg: DeletePluginRequest): DeletePluginRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: DeletePluginRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): DeletePluginRequest;
  static deserializeBinaryFromReader(message: DeletePluginRequest, reader: jspb.BinaryReader): DeletePluginRequest;
}

export namespace DeletePluginRequest {
  export type AsObject = {
    pluginId: string,
    userId: string,
  }
}

export class LockPluginRequest extends jspb.Message {
  getPluginId(): string;
  setPluginId(value: string): void;

  getUserId(): string;
  setUserId(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): LockPluginRequest.AsObject;
  static toObject(includeInstance: boolean, msg: LockPluginRequest): LockPluginRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: LockPluginRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): LockPluginRequest;
  static deserializeBinaryFromReader(message: LockPluginRequest, reader: jspb.BinaryReader): LockPluginRequest;
}

export namespace LockPluginRequest {
  export type AsObject = {
    pluginId: string,
    userId: string,
  }
}

export class UnlockPluginRequest extends jspb.Message {
  getPluginId(): string;
  setPluginId(value: string): void;

  getUserId(): string;
  setUserId(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): UnlockPluginRequest.AsObject;
  static toObject(includeInstance: boolean, msg: UnlockPluginRequest): UnlockPluginRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: UnlockPluginRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): UnlockPluginRequest;
  static deserializeBinaryFromReader(message: UnlockPluginRequest, reader: jspb.BinaryReader): UnlockPluginRequest;
}

export namespace UnlockPluginRequest {
  export type AsObject = {
    pluginId: string,
    userId: string,
  }
}

export class PluginResponse extends jspb.Message {
  getId(): string;
  setId(value: string): void;

  getName(): string;
  setName(value: string): void;

  getDescription(): string;
  setDescription(value: string): void;

  getAuthor(): string;
  setAuthor(value: string): void;

  getIsLocked(): boolean;
  setIsLocked(value: boolean): void;

  getDeploymentType(): string;
  setDeploymentType(value: string): void;

  getHasAccess(): boolean;
  setHasAccess(value: boolean): void;

  getHasPendingRequest(): boolean;
  setHasPendingRequest(value: boolean): void;

  getCreatedAt(): string;
  setCreatedAt(value: string): void;

  getUpdatedAt(): string;
  setUpdatedAt(value: string): void;

  clearVersionsList(): void;
  getVersionsList(): Array<PluginVersionResponse>;
  setVersionsList(value: Array<PluginVersionResponse>): void;
  addVersions(value?: PluginVersionResponse, index?: number): PluginVersionResponse;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): PluginResponse.AsObject;
  static toObject(includeInstance: boolean, msg: PluginResponse): PluginResponse.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: PluginResponse, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): PluginResponse;
  static deserializeBinaryFromReader(message: PluginResponse, reader: jspb.BinaryReader): PluginResponse;
}

export namespace PluginResponse {
  export type AsObject = {
    id: string,
    name: string,
    description: string,
    author: string,
    isLocked: boolean,
    deploymentType: string,
    hasAccess: boolean,
    hasPendingRequest: boolean,
    createdAt: string,
    updatedAt: string,
    versionsList: Array<PluginVersionResponse.AsObject>,
  }
}

export class ListPluginsResponse extends jspb.Message {
  clearPluginsList(): void;
  getPluginsList(): Array<PluginResponse>;
  setPluginsList(value: Array<PluginResponse>): void;
  addPlugins(value?: PluginResponse, index?: number): PluginResponse;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): ListPluginsResponse.AsObject;
  static toObject(includeInstance: boolean, msg: ListPluginsResponse): ListPluginsResponse.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: ListPluginsResponse, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): ListPluginsResponse;
  static deserializeBinaryFromReader(message: ListPluginsResponse, reader: jspb.BinaryReader): ListPluginsResponse;
}

export namespace ListPluginsResponse {
  export type AsObject = {
    pluginsList: Array<PluginResponse.AsObject>,
  }
}

export class ListPluginVersionsRequest extends jspb.Message {
  getPluginId(): string;
  setPluginId(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): ListPluginVersionsRequest.AsObject;
  static toObject(includeInstance: boolean, msg: ListPluginVersionsRequest): ListPluginVersionsRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: ListPluginVersionsRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): ListPluginVersionsRequest;
  static deserializeBinaryFromReader(message: ListPluginVersionsRequest, reader: jspb.BinaryReader): ListPluginVersionsRequest;
}

export namespace ListPluginVersionsRequest {
  export type AsObject = {
    pluginId: string,
  }
}

export class GetPluginVersionRequest extends jspb.Message {
  getPluginId(): string;
  setPluginId(value: string): void;

  getVersion(): string;
  setVersion(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): GetPluginVersionRequest.AsObject;
  static toObject(includeInstance: boolean, msg: GetPluginVersionRequest): GetPluginVersionRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: GetPluginVersionRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): GetPluginVersionRequest;
  static deserializeBinaryFromReader(message: GetPluginVersionRequest, reader: jspb.BinaryReader): GetPluginVersionRequest;
}

export namespace GetPluginVersionRequest {
  export type AsObject = {
    pluginId: string,
    version: string,
  }
}

export class ListPluginVersionsResponse extends jspb.Message {
  clearVersionsList(): void;
  getVersionsList(): Array<PluginVersionResponse>;
  setVersionsList(value: Array<PluginVersionResponse>): void;
  addVersions(value?: PluginVersionResponse, index?: number): PluginVersionResponse;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): ListPluginVersionsResponse.AsObject;
  static toObject(includeInstance: boolean, msg: ListPluginVersionsResponse): ListPluginVersionsResponse.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: ListPluginVersionsResponse, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): ListPluginVersionsResponse;
  static deserializeBinaryFromReader(message: ListPluginVersionsResponse, reader: jspb.BinaryReader): ListPluginVersionsResponse;
}

export namespace ListPluginVersionsResponse {
  export type AsObject = {
    versionsList: Array<PluginVersionResponse.AsObject>,
  }
}

export class RequestPluginAccessRequest extends jspb.Message {
  getPluginId(): string;
  setPluginId(value: string): void;

  getUserId(): string;
  setUserId(value: string): void;

  getBusinessUnitId(): string;
  setBusinessUnitId(value: string): void;

  getNote(): string;
  setNote(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): RequestPluginAccessRequest.AsObject;
  static toObject(includeInstance: boolean, msg: RequestPluginAccessRequest): RequestPluginAccessRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: RequestPluginAccessRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): RequestPluginAccessRequest;
  static deserializeBinaryFromReader(message: RequestPluginAccessRequest, reader: jspb.BinaryReader): RequestPluginAccessRequest;
}

export namespace RequestPluginAccessRequest {
  export type AsObject = {
    pluginId: string,
    userId: string,
    businessUnitId: string,
    note: string,
  }
}

export class GrantPluginAccessRequest extends jspb.Message {
  getPluginId(): string;
  setPluginId(value: string): void;

  getUserId(): string;
  setUserId(value: string): void;

  getGrantedByUserId(): string;
  setGrantedByUserId(value: string): void;

  getBusinessUnitId(): string;
  setBusinessUnitId(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): GrantPluginAccessRequest.AsObject;
  static toObject(includeInstance: boolean, msg: GrantPluginAccessRequest): GrantPluginAccessRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: GrantPluginAccessRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): GrantPluginAccessRequest;
  static deserializeBinaryFromReader(message: GrantPluginAccessRequest, reader: jspb.BinaryReader): GrantPluginAccessRequest;
}

export namespace GrantPluginAccessRequest {
  export type AsObject = {
    pluginId: string,
    userId: string,
    grantedByUserId: string,
    businessUnitId: string,
  }
}

export class RejectPluginAccessRequest extends jspb.Message {
  getPluginId(): string;
  setPluginId(value: string): void;

  getUserId(): string;
  setUserId(value: string): void;

  getRejectedByUserId(): string;
  setRejectedByUserId(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): RejectPluginAccessRequest.AsObject;
  static toObject(includeInstance: boolean, msg: RejectPluginAccessRequest): RejectPluginAccessRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: RejectPluginAccessRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): RejectPluginAccessRequest;
  static deserializeBinaryFromReader(message: RejectPluginAccessRequest, reader: jspb.BinaryReader): RejectPluginAccessRequest;
}

export namespace RejectPluginAccessRequest {
  export type AsObject = {
    pluginId: string,
    userId: string,
    rejectedByUserId: string,
  }
}

export class RevokePluginAccessRequest extends jspb.Message {
  getPluginId(): string;
  setPluginId(value: string): void;

  getUserId(): string;
  setUserId(value: string): void;

  getRevokedByUserId(): string;
  setRevokedByUserId(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): RevokePluginAccessRequest.AsObject;
  static toObject(includeInstance: boolean, msg: RevokePluginAccessRequest): RevokePluginAccessRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: RevokePluginAccessRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): RevokePluginAccessRequest;
  static deserializeBinaryFromReader(message: RevokePluginAccessRequest, reader: jspb.BinaryReader): RevokePluginAccessRequest;
}

export namespace RevokePluginAccessRequest {
  export type AsObject = {
    pluginId: string,
    userId: string,
    revokedByUserId: string,
  }
}

export class RestorePluginAccessRequest extends jspb.Message {
  getPluginId(): string;
  setPluginId(value: string): void;

  getUserId(): string;
  setUserId(value: string): void;

  getRestoredByUserId(): string;
  setRestoredByUserId(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): RestorePluginAccessRequest.AsObject;
  static toObject(includeInstance: boolean, msg: RestorePluginAccessRequest): RestorePluginAccessRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: RestorePluginAccessRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): RestorePluginAccessRequest;
  static deserializeBinaryFromReader(message: RestorePluginAccessRequest, reader: jspb.BinaryReader): RestorePluginAccessRequest;
}

export namespace RestorePluginAccessRequest {
  export type AsObject = {
    pluginId: string,
    userId: string,
    restoredByUserId: string,
  }
}

export class ListAccessRequestsRequest extends jspb.Message {
  getPluginId(): string;
  setPluginId(value: string): void;

  getStatus(): string;
  setStatus(value: string): void;

  getSearch(): string;
  setSearch(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): ListAccessRequestsRequest.AsObject;
  static toObject(includeInstance: boolean, msg: ListAccessRequestsRequest): ListAccessRequestsRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: ListAccessRequestsRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): ListAccessRequestsRequest;
  static deserializeBinaryFromReader(message: ListAccessRequestsRequest, reader: jspb.BinaryReader): ListAccessRequestsRequest;
}

export namespace ListAccessRequestsRequest {
  export type AsObject = {
    pluginId: string,
    status: string,
    search: string,
  }
}

export class ListAccessGrantsRequest extends jspb.Message {
  getPluginId(): string;
  setPluginId(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): ListAccessGrantsRequest.AsObject;
  static toObject(includeInstance: boolean, msg: ListAccessGrantsRequest): ListAccessGrantsRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: ListAccessGrantsRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): ListAccessGrantsRequest;
  static deserializeBinaryFromReader(message: ListAccessGrantsRequest, reader: jspb.BinaryReader): ListAccessGrantsRequest;
}

export namespace ListAccessGrantsRequest {
  export type AsObject = {
    pluginId: string,
  }
}

export class PluginAccessRequestResponse extends jspb.Message {
  getId(): string;
  setId(value: string): void;

  getPluginId(): string;
  setPluginId(value: string): void;

  getUserId(): string;
  setUserId(value: string): void;

  getUserEmail(): string;
  setUserEmail(value: string): void;

  getUserName(): string;
  setUserName(value: string): void;

  getBusinessUnitId(): string;
  setBusinessUnitId(value: string): void;

  getStatus(): string;
  setStatus(value: string): void;

  getNote(): string;
  setNote(value: string): void;

  getRequestedAt(): string;
  setRequestedAt(value: string): void;

  getReviewedAt(): string;
  setReviewedAt(value: string): void;

  getReviewedBy(): string;
  setReviewedBy(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): PluginAccessRequestResponse.AsObject;
  static toObject(includeInstance: boolean, msg: PluginAccessRequestResponse): PluginAccessRequestResponse.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: PluginAccessRequestResponse, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): PluginAccessRequestResponse;
  static deserializeBinaryFromReader(message: PluginAccessRequestResponse, reader: jspb.BinaryReader): PluginAccessRequestResponse;
}

export namespace PluginAccessRequestResponse {
  export type AsObject = {
    id: string,
    pluginId: string,
    userId: string,
    userEmail: string,
    userName: string,
    businessUnitId: string,
    status: string,
    note: string,
    requestedAt: string,
    reviewedAt: string,
    reviewedBy: string,
  }
}

export class PluginAccessResponse extends jspb.Message {
  getId(): string;
  setId(value: string): void;

  getPluginId(): string;
  setPluginId(value: string): void;

  getUserId(): string;
  setUserId(value: string): void;

  getUserEmail(): string;
  setUserEmail(value: string): void;

  getUserName(): string;
  setUserName(value: string): void;

  getBusinessUnitId(): string;
  setBusinessUnitId(value: string): void;

  getGrantedBy(): string;
  setGrantedBy(value: string): void;

  getGrantedAt(): string;
  setGrantedAt(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): PluginAccessResponse.AsObject;
  static toObject(includeInstance: boolean, msg: PluginAccessResponse): PluginAccessResponse.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: PluginAccessResponse, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): PluginAccessResponse;
  static deserializeBinaryFromReader(message: PluginAccessResponse, reader: jspb.BinaryReader): PluginAccessResponse;
}

export namespace PluginAccessResponse {
  export type AsObject = {
    id: string,
    pluginId: string,
    userId: string,
    userEmail: string,
    userName: string,
    businessUnitId: string,
    grantedBy: string,
    grantedAt: string,
  }
}

export class ListAccessRequestsResponse extends jspb.Message {
  clearRequestsList(): void;
  getRequestsList(): Array<PluginAccessRequestResponse>;
  setRequestsList(value: Array<PluginAccessRequestResponse>): void;
  addRequests(value?: PluginAccessRequestResponse, index?: number): PluginAccessRequestResponse;

  getTotal(): number;
  setTotal(value: number): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): ListAccessRequestsResponse.AsObject;
  static toObject(includeInstance: boolean, msg: ListAccessRequestsResponse): ListAccessRequestsResponse.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: ListAccessRequestsResponse, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): ListAccessRequestsResponse;
  static deserializeBinaryFromReader(message: ListAccessRequestsResponse, reader: jspb.BinaryReader): ListAccessRequestsResponse;
}

export namespace ListAccessRequestsResponse {
  export type AsObject = {
    requestsList: Array<PluginAccessRequestResponse.AsObject>,
    total: number,
  }
}

export class ListAccessGrantsResponse extends jspb.Message {
  clearGrantsList(): void;
  getGrantsList(): Array<PluginAccessResponse>;
  setGrantsList(value: Array<PluginAccessResponse>): void;
  addGrants(value?: PluginAccessResponse, index?: number): PluginAccessResponse;

  getTotal(): number;
  setTotal(value: number): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): ListAccessGrantsResponse.AsObject;
  static toObject(includeInstance: boolean, msg: ListAccessGrantsResponse): ListAccessGrantsResponse.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: ListAccessGrantsResponse, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): ListAccessGrantsResponse;
  static deserializeBinaryFromReader(message: ListAccessGrantsResponse, reader: jspb.BinaryReader): ListAccessGrantsResponse;
}

export namespace ListAccessGrantsResponse {
  export type AsObject = {
    grantsList: Array<PluginAccessResponse.AsObject>,
    total: number,
  }
}

