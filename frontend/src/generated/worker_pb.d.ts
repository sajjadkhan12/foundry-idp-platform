// package: worker
// file: worker.proto

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

export class ProvisionInfrastructureRequest extends jspb.Message {
  getJobId(): string;
  setJobId(value: string): void;

  getPluginId(): string;
  setPluginId(value: string): void;

  getVersion(): string;
  setVersion(value: string): void;

  getInputs(): string;
  setInputs(value: string): void;

  getCredentialName(): string;
  setCredentialName(value: string): void;

  getDeploymentId(): string;
  setDeploymentId(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): ProvisionInfrastructureRequest.AsObject;
  static toObject(includeInstance: boolean, msg: ProvisionInfrastructureRequest): ProvisionInfrastructureRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: ProvisionInfrastructureRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): ProvisionInfrastructureRequest;
  static deserializeBinaryFromReader(message: ProvisionInfrastructureRequest, reader: jspb.BinaryReader): ProvisionInfrastructureRequest;
}

export namespace ProvisionInfrastructureRequest {
  export type AsObject = {
    jobId: string,
    pluginId: string,
    version: string,
    inputs: string,
    credentialName: string,
    deploymentId: string,
  }
}

export class DestroyInfrastructureRequest extends jspb.Message {
  getDeploymentId(): string;
  setDeploymentId(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): DestroyInfrastructureRequest.AsObject;
  static toObject(includeInstance: boolean, msg: DestroyInfrastructureRequest): DestroyInfrastructureRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: DestroyInfrastructureRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): DestroyInfrastructureRequest;
  static deserializeBinaryFromReader(message: DestroyInfrastructureRequest, reader: jspb.BinaryReader): DestroyInfrastructureRequest;
}

export namespace DestroyInfrastructureRequest {
  export type AsObject = {
    deploymentId: string,
  }
}

export class ProvisionMicroserviceRequest extends jspb.Message {
  getJobId(): string;
  setJobId(value: string): void;

  getPluginId(): string;
  setPluginId(value: string): void;

  getVersion(): string;
  setVersion(value: string): void;

  getDeploymentName(): string;
  setDeploymentName(value: string): void;

  getUserId(): string;
  setUserId(value: string): void;

  getDeploymentId(): string;
  setDeploymentId(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): ProvisionMicroserviceRequest.AsObject;
  static toObject(includeInstance: boolean, msg: ProvisionMicroserviceRequest): ProvisionMicroserviceRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: ProvisionMicroserviceRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): ProvisionMicroserviceRequest;
  static deserializeBinaryFromReader(message: ProvisionMicroserviceRequest, reader: jspb.BinaryReader): ProvisionMicroserviceRequest;
}

export namespace ProvisionMicroserviceRequest {
  export type AsObject = {
    jobId: string,
    pluginId: string,
    version: string,
    deploymentName: string,
    userId: string,
    deploymentId: string,
  }
}

export class DestroyMicroserviceRequest extends jspb.Message {
  getDeploymentId(): string;
  setDeploymentId(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): DestroyMicroserviceRequest.AsObject;
  static toObject(includeInstance: boolean, msg: DestroyMicroserviceRequest): DestroyMicroserviceRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: DestroyMicroserviceRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): DestroyMicroserviceRequest;
  static deserializeBinaryFromReader(message: DestroyMicroserviceRequest, reader: jspb.BinaryReader): DestroyMicroserviceRequest;
}

export namespace DestroyMicroserviceRequest {
  export type AsObject = {
    deploymentId: string,
  }
}

export class TaskResponse extends jspb.Message {
  getSuccess(): boolean;
  setSuccess(value: boolean): void;

  getMessage(): string;
  setMessage(value: string): void;

  getTaskId(): string;
  setTaskId(value: string): void;

  getError(): string;
  setError(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): TaskResponse.AsObject;
  static toObject(includeInstance: boolean, msg: TaskResponse): TaskResponse.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: TaskResponse, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): TaskResponse;
  static deserializeBinaryFromReader(message: TaskResponse, reader: jspb.BinaryReader): TaskResponse;
}

export namespace TaskResponse {
  export type AsObject = {
    success: boolean,
    message: string,
    taskId: string,
    error: string,
  }
}

export class GetTaskStatusRequest extends jspb.Message {
  getTaskId(): string;
  setTaskId(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): GetTaskStatusRequest.AsObject;
  static toObject(includeInstance: boolean, msg: GetTaskStatusRequest): GetTaskStatusRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: GetTaskStatusRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): GetTaskStatusRequest;
  static deserializeBinaryFromReader(message: GetTaskStatusRequest, reader: jspb.BinaryReader): GetTaskStatusRequest;
}

export namespace GetTaskStatusRequest {
  export type AsObject = {
    taskId: string,
  }
}

export class TaskStatusResponse extends jspb.Message {
  getStatus(): string;
  setStatus(value: string): void;

  getMessage(): string;
  setMessage(value: string): void;

  getError(): string;
  setError(value: string): void;

  getOutputs(): string;
  setOutputs(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): TaskStatusResponse.AsObject;
  static toObject(includeInstance: boolean, msg: TaskStatusResponse): TaskStatusResponse.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: TaskStatusResponse, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): TaskStatusResponse;
  static deserializeBinaryFromReader(message: TaskStatusResponse, reader: jspb.BinaryReader): TaskStatusResponse;
}

export namespace TaskStatusResponse {
  export type AsObject = {
    status: string,
    message: string,
    error: string,
    outputs: string,
  }
}

export class ProcessGitHubWebhookRequest extends jspb.Message {
  getEventType(): string;
  setEventType(value: string): void;

  getPayload(): string;
  setPayload(value: string): void;

  getSignature(): string;
  setSignature(value: string): void;

  getPayloadBody(): Uint8Array | string;
  getPayloadBody_asU8(): Uint8Array;
  getPayloadBody_asB64(): string;
  setPayloadBody(value: Uint8Array | string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): ProcessGitHubWebhookRequest.AsObject;
  static toObject(includeInstance: boolean, msg: ProcessGitHubWebhookRequest): ProcessGitHubWebhookRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: ProcessGitHubWebhookRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): ProcessGitHubWebhookRequest;
  static deserializeBinaryFromReader(message: ProcessGitHubWebhookRequest, reader: jspb.BinaryReader): ProcessGitHubWebhookRequest;
}

export namespace ProcessGitHubWebhookRequest {
  export type AsObject = {
    eventType: string,
    payload: string,
    signature: string,
    payloadBody: Uint8Array | string,
  }
}

export class ProcessGitHubWebhookResponse extends jspb.Message {
  getSuccess(): boolean;
  setSuccess(value: boolean): void;

  getMessage(): string;
  setMessage(value: string): void;

  getDeploymentUpdated(): boolean;
  setDeploymentUpdated(value: boolean): void;

  getDeploymentId(): string;
  setDeploymentId(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): ProcessGitHubWebhookResponse.AsObject;
  static toObject(includeInstance: boolean, msg: ProcessGitHubWebhookResponse): ProcessGitHubWebhookResponse.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: ProcessGitHubWebhookResponse, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): ProcessGitHubWebhookResponse;
  static deserializeBinaryFromReader(message: ProcessGitHubWebhookResponse, reader: jspb.BinaryReader): ProcessGitHubWebhookResponse;
}

export namespace ProcessGitHubWebhookResponse {
  export type AsObject = {
    success: boolean,
    message: string,
    deploymentUpdated: boolean,
    deploymentId: string,
  }
}

