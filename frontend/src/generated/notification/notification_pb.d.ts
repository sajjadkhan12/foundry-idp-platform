// package: notification
// file: notification.proto

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

export class CreateNotificationRequest extends jspb.Message {
  getUserId(): string;
  setUserId(value: string): void;

  getTitle(): string;
  setTitle(value: string): void;

  getMessage(): string;
  setMessage(value: string): void;

  getType(): string;
  setType(value: string): void;

  getLink(): string;
  setLink(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): CreateNotificationRequest.AsObject;
  static toObject(includeInstance: boolean, msg: CreateNotificationRequest): CreateNotificationRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: CreateNotificationRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): CreateNotificationRequest;
  static deserializeBinaryFromReader(message: CreateNotificationRequest, reader: jspb.BinaryReader): CreateNotificationRequest;
}

export namespace CreateNotificationRequest {
  export type AsObject = {
    userId: string,
    title: string,
    message: string,
    type: string,
    link: string,
  }
}

export class GetNotificationRequest extends jspb.Message {
  getNotificationId(): string;
  setNotificationId(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): GetNotificationRequest.AsObject;
  static toObject(includeInstance: boolean, msg: GetNotificationRequest): GetNotificationRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: GetNotificationRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): GetNotificationRequest;
  static deserializeBinaryFromReader(message: GetNotificationRequest, reader: jspb.BinaryReader): GetNotificationRequest;
}

export namespace GetNotificationRequest {
  export type AsObject = {
    notificationId: string,
  }
}

export class ListNotificationsRequest extends jspb.Message {
  getUserId(): string;
  setUserId(value: string): void;

  getSkip(): number;
  setSkip(value: number): void;

  getLimit(): number;
  setLimit(value: number): void;

  getUnreadOnly(): boolean;
  setUnreadOnly(value: boolean): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): ListNotificationsRequest.AsObject;
  static toObject(includeInstance: boolean, msg: ListNotificationsRequest): ListNotificationsRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: ListNotificationsRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): ListNotificationsRequest;
  static deserializeBinaryFromReader(message: ListNotificationsRequest, reader: jspb.BinaryReader): ListNotificationsRequest;
}

export namespace ListNotificationsRequest {
  export type AsObject = {
    userId: string,
    skip: number,
    limit: number,
    unreadOnly: boolean,
  }
}

export class UpdateNotificationRequest extends jspb.Message {
  getNotificationId(): string;
  setNotificationId(value: string): void;

  getIsRead(): boolean;
  setIsRead(value: boolean): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): UpdateNotificationRequest.AsObject;
  static toObject(includeInstance: boolean, msg: UpdateNotificationRequest): UpdateNotificationRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: UpdateNotificationRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): UpdateNotificationRequest;
  static deserializeBinaryFromReader(message: UpdateNotificationRequest, reader: jspb.BinaryReader): UpdateNotificationRequest;
}

export namespace UpdateNotificationRequest {
  export type AsObject = {
    notificationId: string,
    isRead: boolean,
  }
}

export class DeleteNotificationRequest extends jspb.Message {
  getNotificationId(): string;
  setNotificationId(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): DeleteNotificationRequest.AsObject;
  static toObject(includeInstance: boolean, msg: DeleteNotificationRequest): DeleteNotificationRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: DeleteNotificationRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): DeleteNotificationRequest;
  static deserializeBinaryFromReader(message: DeleteNotificationRequest, reader: jspb.BinaryReader): DeleteNotificationRequest;
}

export namespace DeleteNotificationRequest {
  export type AsObject = {
    notificationId: string,
  }
}

export class MarkAsReadRequest extends jspb.Message {
  getNotificationId(): string;
  setNotificationId(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): MarkAsReadRequest.AsObject;
  static toObject(includeInstance: boolean, msg: MarkAsReadRequest): MarkAsReadRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: MarkAsReadRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): MarkAsReadRequest;
  static deserializeBinaryFromReader(message: MarkAsReadRequest, reader: jspb.BinaryReader): MarkAsReadRequest;
}

export namespace MarkAsReadRequest {
  export type AsObject = {
    notificationId: string,
  }
}

export class MarkAllAsReadRequest extends jspb.Message {
  getUserId(): string;
  setUserId(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): MarkAllAsReadRequest.AsObject;
  static toObject(includeInstance: boolean, msg: MarkAllAsReadRequest): MarkAllAsReadRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: MarkAllAsReadRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): MarkAllAsReadRequest;
  static deserializeBinaryFromReader(message: MarkAllAsReadRequest, reader: jspb.BinaryReader): MarkAllAsReadRequest;
}

export namespace MarkAllAsReadRequest {
  export type AsObject = {
    userId: string,
  }
}

export class GetUnreadCountRequest extends jspb.Message {
  getUserId(): string;
  setUserId(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): GetUnreadCountRequest.AsObject;
  static toObject(includeInstance: boolean, msg: GetUnreadCountRequest): GetUnreadCountRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: GetUnreadCountRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): GetUnreadCountRequest;
  static deserializeBinaryFromReader(message: GetUnreadCountRequest, reader: jspb.BinaryReader): GetUnreadCountRequest;
}

export namespace GetUnreadCountRequest {
  export type AsObject = {
    userId: string,
  }
}

export class NotificationResponse extends jspb.Message {
  getId(): string;
  setId(value: string): void;

  getUserId(): string;
  setUserId(value: string): void;

  getTitle(): string;
  setTitle(value: string): void;

  getMessage(): string;
  setMessage(value: string): void;

  getType(): string;
  setType(value: string): void;

  getIsRead(): boolean;
  setIsRead(value: boolean): void;

  getLink(): string;
  setLink(value: string): void;

  getCreatedAt(): string;
  setCreatedAt(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): NotificationResponse.AsObject;
  static toObject(includeInstance: boolean, msg: NotificationResponse): NotificationResponse.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: NotificationResponse, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): NotificationResponse;
  static deserializeBinaryFromReader(message: NotificationResponse, reader: jspb.BinaryReader): NotificationResponse;
}

export namespace NotificationResponse {
  export type AsObject = {
    id: string,
    userId: string,
    title: string,
    message: string,
    type: string,
    isRead: boolean,
    link: string,
    createdAt: string,
  }
}

export class ListNotificationsResponse extends jspb.Message {
  clearNotificationsList(): void;
  getNotificationsList(): Array<NotificationResponse>;
  setNotificationsList(value: Array<NotificationResponse>): void;
  addNotifications(value?: NotificationResponse, index?: number): NotificationResponse;

  getTotal(): number;
  setTotal(value: number): void;

  getSkip(): number;
  setSkip(value: number): void;

  getLimit(): number;
  setLimit(value: number): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): ListNotificationsResponse.AsObject;
  static toObject(includeInstance: boolean, msg: ListNotificationsResponse): ListNotificationsResponse.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: ListNotificationsResponse, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): ListNotificationsResponse;
  static deserializeBinaryFromReader(message: ListNotificationsResponse, reader: jspb.BinaryReader): ListNotificationsResponse;
}

export namespace ListNotificationsResponse {
  export type AsObject = {
    notificationsList: Array<NotificationResponse.AsObject>,
    total: number,
    skip: number,
    limit: number,
  }
}

export class UnreadCountResponse extends jspb.Message {
  getCount(): number;
  setCount(value: number): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): UnreadCountResponse.AsObject;
  static toObject(includeInstance: boolean, msg: UnreadCountResponse): UnreadCountResponse.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: UnreadCountResponse, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): UnreadCountResponse;
  static deserializeBinaryFromReader(message: UnreadCountResponse, reader: jspb.BinaryReader): UnreadCountResponse;
}

export namespace UnreadCountResponse {
  export type AsObject = {
    count: number,
  }
}

