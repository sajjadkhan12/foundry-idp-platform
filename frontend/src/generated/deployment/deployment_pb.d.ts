// package: deployment
// file: deployment.proto

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

export class CreateDeploymentRequest extends jspb.Message {
  getName(): string;
  setName(value: string): void;

  getDeploymentType(): string;
  setDeploymentType(value: string): void;

  getPluginId(): string;
  setPluginId(value: string): void;

  getVersion(): string;
  setVersion(value: string): void;

  getEnvironment(): string;
  setEnvironment(value: string): void;

  getUserId(): string;
  setUserId(value: string): void;

  getBusinessUnitId(): string;
  setBusinessUnitId(value: string): void;

  getInputs(): string;
  setInputs(value: string): void;

  getCostCenter(): string;
  setCostCenter(value: string): void;

  getProjectCode(): string;
  setProjectCode(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): CreateDeploymentRequest.AsObject;
  static toObject(includeInstance: boolean, msg: CreateDeploymentRequest): CreateDeploymentRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: CreateDeploymentRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): CreateDeploymentRequest;
  static deserializeBinaryFromReader(message: CreateDeploymentRequest, reader: jspb.BinaryReader): CreateDeploymentRequest;
}

export namespace CreateDeploymentRequest {
  export type AsObject = {
    name: string,
    deploymentType: string,
    pluginId: string,
    version: string,
    environment: string,
    userId: string,
    businessUnitId: string,
    inputs: string,
    costCenter: string,
    projectCode: string,
  }
}

export class UpdateDeploymentRequest extends jspb.Message {
  getDeploymentId(): string;
  setDeploymentId(value: string): void;

  getName(): string;
  setName(value: string): void;

  getEnvironment(): string;
  setEnvironment(value: string): void;

  getInputs(): string;
  setInputs(value: string): void;

  getCostCenter(): string;
  setCostCenter(value: string): void;

  getProjectCode(): string;
  setProjectCode(value: string): void;

  getStatus(): string;
  setStatus(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): UpdateDeploymentRequest.AsObject;
  static toObject(includeInstance: boolean, msg: UpdateDeploymentRequest): UpdateDeploymentRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: UpdateDeploymentRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): UpdateDeploymentRequest;
  static deserializeBinaryFromReader(message: UpdateDeploymentRequest, reader: jspb.BinaryReader): UpdateDeploymentRequest;
}

export namespace UpdateDeploymentRequest {
  export type AsObject = {
    deploymentId: string,
    name: string,
    environment: string,
    inputs: string,
    costCenter: string,
    projectCode: string,
    status: string,
  }
}

export class GetDeploymentRequest extends jspb.Message {
  getDeploymentId(): string;
  setDeploymentId(value: string): void;

  getIncludeTags(): boolean;
  setIncludeTags(value: boolean): void;

  getIncludeHistory(): boolean;
  setIncludeHistory(value: boolean): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): GetDeploymentRequest.AsObject;
  static toObject(includeInstance: boolean, msg: GetDeploymentRequest): GetDeploymentRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: GetDeploymentRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): GetDeploymentRequest;
  static deserializeBinaryFromReader(message: GetDeploymentRequest, reader: jspb.BinaryReader): GetDeploymentRequest;
}

export namespace GetDeploymentRequest {
  export type AsObject = {
    deploymentId: string,
    includeTags: boolean,
    includeHistory: boolean,
  }
}

export class DeleteDeploymentRequest extends jspb.Message {
  getDeploymentId(): string;
  setDeploymentId(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): DeleteDeploymentRequest.AsObject;
  static toObject(includeInstance: boolean, msg: DeleteDeploymentRequest): DeleteDeploymentRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: DeleteDeploymentRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): DeleteDeploymentRequest;
  static deserializeBinaryFromReader(message: DeleteDeploymentRequest, reader: jspb.BinaryReader): DeleteDeploymentRequest;
}

export namespace DeleteDeploymentRequest {
  export type AsObject = {
    deploymentId: string,
  }
}

export class ListDeploymentsRequest extends jspb.Message {
  getSearch(): string;
  setSearch(value: string): void;

  getStatus(): string;
  setStatus(value: string): void;

  getCloudProvider(): string;
  setCloudProvider(value: string): void;

  getPluginId(): string;
  setPluginId(value: string): void;

  getEnvironment(): string;
  setEnvironment(value: string): void;

  getTags(): string;
  setTags(value: string): void;

  getUserId(): string;
  setUserId(value: string): void;

  getBusinessUnitId(): string;
  setBusinessUnitId(value: string): void;

  getSkip(): number;
  setSkip(value: number): void;

  getLimit(): number;
  setLimit(value: number): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): ListDeploymentsRequest.AsObject;
  static toObject(includeInstance: boolean, msg: ListDeploymentsRequest): ListDeploymentsRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: ListDeploymentsRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): ListDeploymentsRequest;
  static deserializeBinaryFromReader(message: ListDeploymentsRequest, reader: jspb.BinaryReader): ListDeploymentsRequest;
}

export namespace ListDeploymentsRequest {
  export type AsObject = {
    search: string,
    status: string,
    cloudProvider: string,
    pluginId: string,
    environment: string,
    tags: string,
    userId: string,
    businessUnitId: string,
    skip: number,
    limit: number,
  }
}

export class DeploymentResponse extends jspb.Message {
  getId(): string;
  setId(value: string): void;

  getName(): string;
  setName(value: string): void;

  getStatus(): string;
  setStatus(value: string): void;

  getDeploymentType(): string;
  setDeploymentType(value: string): void;

  getEnvironment(): string;
  setEnvironment(value: string): void;

  getPluginId(): string;
  setPluginId(value: string): void;

  getVersion(): string;
  setVersion(value: string): void;

  getStackName(): string;
  setStackName(value: string): void;

  getCloudProvider(): string;
  setCloudProvider(value: string): void;

  getRegion(): string;
  setRegion(value: string): void;

  getGitBranch(): string;
  setGitBranch(value: string): void;

  getGithubRepoUrl(): string;
  setGithubRepoUrl(value: string): void;

  getGithubRepoName(): string;
  setGithubRepoName(value: string): void;

  getCiCdStatus(): string;
  setCiCdStatus(value: string): void;

  getCiCdRunId(): number;
  setCiCdRunId(value: number): void;

  getCiCdRunUrl(): string;
  setCiCdRunUrl(value: string): void;

  getCiCdUpdatedAt(): string;
  setCiCdUpdatedAt(value: string): void;

  getUpdateStatus(): string;
  setUpdateStatus(value: string): void;

  getLastUpdateJobId(): string;
  setLastUpdateJobId(value: string): void;

  getLastUpdateError(): string;
  setLastUpdateError(value: string): void;

  getLastUpdateAttemptedAt(): string;
  setLastUpdateAttemptedAt(value: string): void;

  getInputs(): string;
  setInputs(value: string): void;

  getOutputs(): string;
  setOutputs(value: string): void;

  getUserId(): string;
  setUserId(value: string): void;

  getBusinessUnitId(): string;
  setBusinessUnitId(value: string): void;

  getCostCenter(): string;
  setCostCenter(value: string): void;

  getProjectCode(): string;
  setProjectCode(value: string): void;

  getCreatedAt(): string;
  setCreatedAt(value: string): void;

  getUpdatedAt(): string;
  setUpdatedAt(value: string): void;

  clearTagsList(): void;
  getTagsList(): Array<DeploymentTagResponse>;
  setTagsList(value: Array<DeploymentTagResponse>): void;
  addTags(value?: DeploymentTagResponse, index?: number): DeploymentTagResponse;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): DeploymentResponse.AsObject;
  static toObject(includeInstance: boolean, msg: DeploymentResponse): DeploymentResponse.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: DeploymentResponse, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): DeploymentResponse;
  static deserializeBinaryFromReader(message: DeploymentResponse, reader: jspb.BinaryReader): DeploymentResponse;
}

export namespace DeploymentResponse {
  export type AsObject = {
    id: string,
    name: string,
    status: string,
    deploymentType: string,
    environment: string,
    pluginId: string,
    version: string,
    stackName: string,
    cloudProvider: string,
    region: string,
    gitBranch: string,
    githubRepoUrl: string,
    githubRepoName: string,
    ciCdStatus: string,
    ciCdRunId: number,
    ciCdRunUrl: string,
    ciCdUpdatedAt: string,
    updateStatus: string,
    lastUpdateJobId: string,
    lastUpdateError: string,
    lastUpdateAttemptedAt: string,
    inputs: string,
    outputs: string,
    userId: string,
    businessUnitId: string,
    costCenter: string,
    projectCode: string,
    createdAt: string,
    updatedAt: string,
    tagsList: Array<DeploymentTagResponse.AsObject>,
  }
}

export class ListDeploymentsResponse extends jspb.Message {
  clearDeploymentsList(): void;
  getDeploymentsList(): Array<DeploymentResponse>;
  setDeploymentsList(value: Array<DeploymentResponse>): void;
  addDeployments(value?: DeploymentResponse, index?: number): DeploymentResponse;

  getTotal(): number;
  setTotal(value: number): void;

  getSkip(): number;
  setSkip(value: number): void;

  getLimit(): number;
  setLimit(value: number): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): ListDeploymentsResponse.AsObject;
  static toObject(includeInstance: boolean, msg: ListDeploymentsResponse): ListDeploymentsResponse.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: ListDeploymentsResponse, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): ListDeploymentsResponse;
  static deserializeBinaryFromReader(message: ListDeploymentsResponse, reader: jspb.BinaryReader): ListDeploymentsResponse;
}

export namespace ListDeploymentsResponse {
  export type AsObject = {
    deploymentsList: Array<DeploymentResponse.AsObject>,
    total: number,
    skip: number,
    limit: number,
  }
}

export class GetDeploymentHistoryRequest extends jspb.Message {
  getDeploymentId(): string;
  setDeploymentId(value: string): void;

  getSkip(): number;
  setSkip(value: number): void;

  getLimit(): number;
  setLimit(value: number): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): GetDeploymentHistoryRequest.AsObject;
  static toObject(includeInstance: boolean, msg: GetDeploymentHistoryRequest): GetDeploymentHistoryRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: GetDeploymentHistoryRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): GetDeploymentHistoryRequest;
  static deserializeBinaryFromReader(message: GetDeploymentHistoryRequest, reader: jspb.BinaryReader): GetDeploymentHistoryRequest;
}

export namespace GetDeploymentHistoryRequest {
  export type AsObject = {
    deploymentId: string,
    skip: number,
    limit: number,
  }
}

export class GetDeploymentHistoryVersionRequest extends jspb.Message {
  getDeploymentId(): string;
  setDeploymentId(value: string): void;

  getVersionNumber(): number;
  setVersionNumber(value: number): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): GetDeploymentHistoryVersionRequest.AsObject;
  static toObject(includeInstance: boolean, msg: GetDeploymentHistoryVersionRequest): GetDeploymentHistoryVersionRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: GetDeploymentHistoryVersionRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): GetDeploymentHistoryVersionRequest;
  static deserializeBinaryFromReader(message: GetDeploymentHistoryVersionRequest, reader: jspb.BinaryReader): GetDeploymentHistoryVersionRequest;
}

export namespace GetDeploymentHistoryVersionRequest {
  export type AsObject = {
    deploymentId: string,
    versionNumber: number,
  }
}

export class DeploymentHistoryResponse extends jspb.Message {
  getId(): string;
  setId(value: string): void;

  getDeploymentId(): string;
  setDeploymentId(value: string): void;

  getVersionNumber(): number;
  setVersionNumber(value: number): void;

  getInputs(): string;
  setInputs(value: string): void;

  getOutputs(): string;
  setOutputs(value: string): void;

  getStatus(): string;
  setStatus(value: string): void;

  getJobId(): string;
  setJobId(value: string): void;

  getCreatedAt(): string;
  setCreatedAt(value: string): void;

  getCreatedBy(): string;
  setCreatedBy(value: string): void;

  getDescription(): string;
  setDescription(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): DeploymentHistoryResponse.AsObject;
  static toObject(includeInstance: boolean, msg: DeploymentHistoryResponse): DeploymentHistoryResponse.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: DeploymentHistoryResponse, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): DeploymentHistoryResponse;
  static deserializeBinaryFromReader(message: DeploymentHistoryResponse, reader: jspb.BinaryReader): DeploymentHistoryResponse;
}

export namespace DeploymentHistoryResponse {
  export type AsObject = {
    id: string,
    deploymentId: string,
    versionNumber: number,
    inputs: string,
    outputs: string,
    status: string,
    jobId: string,
    createdAt: string,
    createdBy: string,
    description: string,
  }
}

export class ListDeploymentHistoryResponse extends jspb.Message {
  clearHistoryList(): void;
  getHistoryList(): Array<DeploymentHistoryResponse>;
  setHistoryList(value: Array<DeploymentHistoryResponse>): void;
  addHistory(value?: DeploymentHistoryResponse, index?: number): DeploymentHistoryResponse;

  getTotal(): number;
  setTotal(value: number): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): ListDeploymentHistoryResponse.AsObject;
  static toObject(includeInstance: boolean, msg: ListDeploymentHistoryResponse): ListDeploymentHistoryResponse.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: ListDeploymentHistoryResponse, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): ListDeploymentHistoryResponse;
  static deserializeBinaryFromReader(message: ListDeploymentHistoryResponse, reader: jspb.BinaryReader): ListDeploymentHistoryResponse;
}

export namespace ListDeploymentHistoryResponse {
  export type AsObject = {
    historyList: Array<DeploymentHistoryResponse.AsObject>,
    total: number,
  }
}

export class AddDeploymentTagRequest extends jspb.Message {
  getDeploymentId(): string;
  setDeploymentId(value: string): void;

  getKey(): string;
  setKey(value: string): void;

  getValue(): string;
  setValue(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): AddDeploymentTagRequest.AsObject;
  static toObject(includeInstance: boolean, msg: AddDeploymentTagRequest): AddDeploymentTagRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: AddDeploymentTagRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): AddDeploymentTagRequest;
  static deserializeBinaryFromReader(message: AddDeploymentTagRequest, reader: jspb.BinaryReader): AddDeploymentTagRequest;
}

export namespace AddDeploymentTagRequest {
  export type AsObject = {
    deploymentId: string,
    key: string,
    value: string,
  }
}

export class RemoveDeploymentTagRequest extends jspb.Message {
  getDeploymentId(): string;
  setDeploymentId(value: string): void;

  getKey(): string;
  setKey(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): RemoveDeploymentTagRequest.AsObject;
  static toObject(includeInstance: boolean, msg: RemoveDeploymentTagRequest): RemoveDeploymentTagRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: RemoveDeploymentTagRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): RemoveDeploymentTagRequest;
  static deserializeBinaryFromReader(message: RemoveDeploymentTagRequest, reader: jspb.BinaryReader): RemoveDeploymentTagRequest;
}

export namespace RemoveDeploymentTagRequest {
  export type AsObject = {
    deploymentId: string,
    key: string,
  }
}

export class ListDeploymentTagsRequest extends jspb.Message {
  getDeploymentId(): string;
  setDeploymentId(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): ListDeploymentTagsRequest.AsObject;
  static toObject(includeInstance: boolean, msg: ListDeploymentTagsRequest): ListDeploymentTagsRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: ListDeploymentTagsRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): ListDeploymentTagsRequest;
  static deserializeBinaryFromReader(message: ListDeploymentTagsRequest, reader: jspb.BinaryReader): ListDeploymentTagsRequest;
}

export namespace ListDeploymentTagsRequest {
  export type AsObject = {
    deploymentId: string,
  }
}

export class DeploymentTagResponse extends jspb.Message {
  getId(): string;
  setId(value: string): void;

  getDeploymentId(): string;
  setDeploymentId(value: string): void;

  getKey(): string;
  setKey(value: string): void;

  getValue(): string;
  setValue(value: string): void;

  getCreatedAt(): string;
  setCreatedAt(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): DeploymentTagResponse.AsObject;
  static toObject(includeInstance: boolean, msg: DeploymentTagResponse): DeploymentTagResponse.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: DeploymentTagResponse, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): DeploymentTagResponse;
  static deserializeBinaryFromReader(message: DeploymentTagResponse, reader: jspb.BinaryReader): DeploymentTagResponse;
}

export namespace DeploymentTagResponse {
  export type AsObject = {
    id: string,
    deploymentId: string,
    key: string,
    value: string,
    createdAt: string,
  }
}

export class ListDeploymentTagsResponse extends jspb.Message {
  clearTagsList(): void;
  getTagsList(): Array<DeploymentTagResponse>;
  setTagsList(value: Array<DeploymentTagResponse>): void;
  addTags(value?: DeploymentTagResponse, index?: number): DeploymentTagResponse;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): ListDeploymentTagsResponse.AsObject;
  static toObject(includeInstance: boolean, msg: ListDeploymentTagsResponse): ListDeploymentTagsResponse.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: ListDeploymentTagsResponse, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): ListDeploymentTagsResponse;
  static deserializeBinaryFromReader(message: ListDeploymentTagsResponse, reader: jspb.BinaryReader): ListDeploymentTagsResponse;
}

export namespace ListDeploymentTagsResponse {
  export type AsObject = {
    tagsList: Array<DeploymentTagResponse.AsObject>,
  }
}

export class UpdateCICDStatusRequest extends jspb.Message {
  getDeploymentId(): string;
  setDeploymentId(value: string): void;

  getCiCdStatus(): string;
  setCiCdStatus(value: string): void;

  getCiCdRunId(): number;
  setCiCdRunId(value: number): void;

  getCiCdRunUrl(): string;
  setCiCdRunUrl(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): UpdateCICDStatusRequest.AsObject;
  static toObject(includeInstance: boolean, msg: UpdateCICDStatusRequest): UpdateCICDStatusRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: UpdateCICDStatusRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): UpdateCICDStatusRequest;
  static deserializeBinaryFromReader(message: UpdateCICDStatusRequest, reader: jspb.BinaryReader): UpdateCICDStatusRequest;
}

export namespace UpdateCICDStatusRequest {
  export type AsObject = {
    deploymentId: string,
    ciCdStatus: string,
    ciCdRunId: number,
    ciCdRunUrl: string,
  }
}

export class GetCICDStatusRequest extends jspb.Message {
  getDeploymentId(): string;
  setDeploymentId(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): GetCICDStatusRequest.AsObject;
  static toObject(includeInstance: boolean, msg: GetCICDStatusRequest): GetCICDStatusRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: GetCICDStatusRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): GetCICDStatusRequest;
  static deserializeBinaryFromReader(message: GetCICDStatusRequest, reader: jspb.BinaryReader): GetCICDStatusRequest;
}

export namespace GetCICDStatusRequest {
  export type AsObject = {
    deploymentId: string,
  }
}

export class CICDStatusResponse extends jspb.Message {
  getCiCdStatus(): string;
  setCiCdStatus(value: string): void;

  getCiCdRunId(): number;
  setCiCdRunId(value: number): void;

  getCiCdRunUrl(): string;
  setCiCdRunUrl(value: string): void;

  getCiCdUpdatedAt(): string;
  setCiCdUpdatedAt(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): CICDStatusResponse.AsObject;
  static toObject(includeInstance: boolean, msg: CICDStatusResponse): CICDStatusResponse.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: CICDStatusResponse, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): CICDStatusResponse;
  static deserializeBinaryFromReader(message: CICDStatusResponse, reader: jspb.BinaryReader): CICDStatusResponse;
}

export namespace CICDStatusResponse {
  export type AsObject = {
    ciCdStatus: string,
    ciCdRunId: number,
    ciCdRunUrl: string,
    ciCdUpdatedAt: string,
  }
}

export class GetDeploymentStatsRequest extends jspb.Message {
  getBusinessUnitId(): string;
  setBusinessUnitId(value: string): void;

  getUserId(): string;
  setUserId(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): GetDeploymentStatsRequest.AsObject;
  static toObject(includeInstance: boolean, msg: GetDeploymentStatsRequest): GetDeploymentStatsRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: GetDeploymentStatsRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): GetDeploymentStatsRequest;
  static deserializeBinaryFromReader(message: GetDeploymentStatsRequest, reader: jspb.BinaryReader): GetDeploymentStatsRequest;
}

export namespace GetDeploymentStatsRequest {
  export type AsObject = {
    businessUnitId: string,
    userId: string,
  }
}

export class DeploymentStatsResponse extends jspb.Message {
  getTotal(): number;
  setTotal(value: number): void;

  getActive(): number;
  setActive(value: number): void;

  getProvisioning(): number;
  setProvisioning(value: number): void;

  getFailed(): number;
  setFailed(value: number): void;

  getByEnvironment(): string;
  setByEnvironment(value: string): void;

  getByCloudProvider(): string;
  setByCloudProvider(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): DeploymentStatsResponse.AsObject;
  static toObject(includeInstance: boolean, msg: DeploymentStatsResponse): DeploymentStatsResponse.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: DeploymentStatsResponse, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): DeploymentStatsResponse;
  static deserializeBinaryFromReader(message: DeploymentStatsResponse, reader: jspb.BinaryReader): DeploymentStatsResponse;
}

export namespace DeploymentStatsResponse {
  export type AsObject = {
    total: number,
    active: number,
    provisioning: number,
    failed: number,
    byEnvironment: string,
    byCloudProvider: string,
  }
}

export class GetDeploymentCostsRequest extends jspb.Message {
  getDeploymentId(): string;
  setDeploymentId(value: string): void;

  getBusinessUnitId(): string;
  setBusinessUnitId(value: string): void;

  getStartDate(): string;
  setStartDate(value: string): void;

  getEndDate(): string;
  setEndDate(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): GetDeploymentCostsRequest.AsObject;
  static toObject(includeInstance: boolean, msg: GetDeploymentCostsRequest): GetDeploymentCostsRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: GetDeploymentCostsRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): GetDeploymentCostsRequest;
  static deserializeBinaryFromReader(message: GetDeploymentCostsRequest, reader: jspb.BinaryReader): GetDeploymentCostsRequest;
}

export namespace GetDeploymentCostsRequest {
  export type AsObject = {
    deploymentId: string,
    businessUnitId: string,
    startDate: string,
    endDate: string,
  }
}

export class DeploymentCostsResponse extends jspb.Message {
  getTotalCost(): string;
  setTotalCost(value: string): void;

  getCurrency(): string;
  setCurrency(value: string): void;

  clearCostsList(): void;
  getCostsList(): Array<DeploymentCostItem>;
  setCostsList(value: Array<DeploymentCostItem>): void;
  addCosts(value?: DeploymentCostItem, index?: number): DeploymentCostItem;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): DeploymentCostsResponse.AsObject;
  static toObject(includeInstance: boolean, msg: DeploymentCostsResponse): DeploymentCostsResponse.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: DeploymentCostsResponse, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): DeploymentCostsResponse;
  static deserializeBinaryFromReader(message: DeploymentCostsResponse, reader: jspb.BinaryReader): DeploymentCostsResponse;
}

export namespace DeploymentCostsResponse {
  export type AsObject = {
    totalCost: string,
    currency: string,
    costsList: Array<DeploymentCostItem.AsObject>,
  }
}

export class DeploymentCostItem extends jspb.Message {
  getDeploymentId(): string;
  setDeploymentId(value: string): void;

  getDeploymentName(): string;
  setDeploymentName(value: string): void;

  getCost(): string;
  setCost(value: string): void;

  getPeriod(): string;
  setPeriod(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): DeploymentCostItem.AsObject;
  static toObject(includeInstance: boolean, msg: DeploymentCostItem): DeploymentCostItem.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: DeploymentCostItem, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): DeploymentCostItem;
  static deserializeBinaryFromReader(message: DeploymentCostItem, reader: jspb.BinaryReader): DeploymentCostItem;
}

export namespace DeploymentCostItem {
  export type AsObject = {
    deploymentId: string,
    deploymentName: string,
    cost: string,
    period: string,
  }
}

