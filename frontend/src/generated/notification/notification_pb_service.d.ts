// package: notification
// file: notification.proto

import * as notification_pb from "./notification_pb";
import {grpc} from "@improbable-eng/grpc-web";

type NotificationServiceCreateNotification = {
  readonly methodName: string;
  readonly service: typeof NotificationService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof notification_pb.CreateNotificationRequest;
  readonly responseType: typeof notification_pb.NotificationResponse;
};

type NotificationServiceGetNotification = {
  readonly methodName: string;
  readonly service: typeof NotificationService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof notification_pb.GetNotificationRequest;
  readonly responseType: typeof notification_pb.NotificationResponse;
};

type NotificationServiceListNotifications = {
  readonly methodName: string;
  readonly service: typeof NotificationService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof notification_pb.ListNotificationsRequest;
  readonly responseType: typeof notification_pb.ListNotificationsResponse;
};

type NotificationServiceUpdateNotification = {
  readonly methodName: string;
  readonly service: typeof NotificationService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof notification_pb.UpdateNotificationRequest;
  readonly responseType: typeof notification_pb.NotificationResponse;
};

type NotificationServiceDeleteNotification = {
  readonly methodName: string;
  readonly service: typeof NotificationService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof notification_pb.DeleteNotificationRequest;
  readonly responseType: typeof notification_pb.Empty;
};

type NotificationServiceMarkAsRead = {
  readonly methodName: string;
  readonly service: typeof NotificationService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof notification_pb.MarkAsReadRequest;
  readonly responseType: typeof notification_pb.NotificationResponse;
};

type NotificationServiceMarkAllAsRead = {
  readonly methodName: string;
  readonly service: typeof NotificationService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof notification_pb.MarkAllAsReadRequest;
  readonly responseType: typeof notification_pb.Empty;
};

type NotificationServiceGetUnreadCount = {
  readonly methodName: string;
  readonly service: typeof NotificationService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof notification_pb.GetUnreadCountRequest;
  readonly responseType: typeof notification_pb.UnreadCountResponse;
};

export class NotificationService {
  static readonly serviceName: string;
  static readonly CreateNotification: NotificationServiceCreateNotification;
  static readonly GetNotification: NotificationServiceGetNotification;
  static readonly ListNotifications: NotificationServiceListNotifications;
  static readonly UpdateNotification: NotificationServiceUpdateNotification;
  static readonly DeleteNotification: NotificationServiceDeleteNotification;
  static readonly MarkAsRead: NotificationServiceMarkAsRead;
  static readonly MarkAllAsRead: NotificationServiceMarkAllAsRead;
  static readonly GetUnreadCount: NotificationServiceGetUnreadCount;
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

export class NotificationServiceClient {
  readonly serviceHost: string;

  constructor(serviceHost: string, options?: grpc.RpcOptions);
  createNotification(
    requestMessage: notification_pb.CreateNotificationRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: notification_pb.NotificationResponse|null) => void
  ): UnaryResponse;
  createNotification(
    requestMessage: notification_pb.CreateNotificationRequest,
    callback: (error: ServiceError|null, responseMessage: notification_pb.NotificationResponse|null) => void
  ): UnaryResponse;
  getNotification(
    requestMessage: notification_pb.GetNotificationRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: notification_pb.NotificationResponse|null) => void
  ): UnaryResponse;
  getNotification(
    requestMessage: notification_pb.GetNotificationRequest,
    callback: (error: ServiceError|null, responseMessage: notification_pb.NotificationResponse|null) => void
  ): UnaryResponse;
  listNotifications(
    requestMessage: notification_pb.ListNotificationsRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: notification_pb.ListNotificationsResponse|null) => void
  ): UnaryResponse;
  listNotifications(
    requestMessage: notification_pb.ListNotificationsRequest,
    callback: (error: ServiceError|null, responseMessage: notification_pb.ListNotificationsResponse|null) => void
  ): UnaryResponse;
  updateNotification(
    requestMessage: notification_pb.UpdateNotificationRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: notification_pb.NotificationResponse|null) => void
  ): UnaryResponse;
  updateNotification(
    requestMessage: notification_pb.UpdateNotificationRequest,
    callback: (error: ServiceError|null, responseMessage: notification_pb.NotificationResponse|null) => void
  ): UnaryResponse;
  deleteNotification(
    requestMessage: notification_pb.DeleteNotificationRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: notification_pb.Empty|null) => void
  ): UnaryResponse;
  deleteNotification(
    requestMessage: notification_pb.DeleteNotificationRequest,
    callback: (error: ServiceError|null, responseMessage: notification_pb.Empty|null) => void
  ): UnaryResponse;
  markAsRead(
    requestMessage: notification_pb.MarkAsReadRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: notification_pb.NotificationResponse|null) => void
  ): UnaryResponse;
  markAsRead(
    requestMessage: notification_pb.MarkAsReadRequest,
    callback: (error: ServiceError|null, responseMessage: notification_pb.NotificationResponse|null) => void
  ): UnaryResponse;
  markAllAsRead(
    requestMessage: notification_pb.MarkAllAsReadRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: notification_pb.Empty|null) => void
  ): UnaryResponse;
  markAllAsRead(
    requestMessage: notification_pb.MarkAllAsReadRequest,
    callback: (error: ServiceError|null, responseMessage: notification_pb.Empty|null) => void
  ): UnaryResponse;
  getUnreadCount(
    requestMessage: notification_pb.GetUnreadCountRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: notification_pb.UnreadCountResponse|null) => void
  ): UnaryResponse;
  getUnreadCount(
    requestMessage: notification_pb.GetUnreadCountRequest,
    callback: (error: ServiceError|null, responseMessage: notification_pb.UnreadCountResponse|null) => void
  ): UnaryResponse;
}

