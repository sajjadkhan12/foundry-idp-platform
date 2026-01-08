// package: notification
// file: notification.proto

var notification_pb = require("./notification_pb");
var grpc = require("@improbable-eng/grpc-web").grpc;

var NotificationService = (function () {
  function NotificationService() {}
  NotificationService.serviceName = "notification.NotificationService";
  return NotificationService;
}());

NotificationService.CreateNotification = {
  methodName: "CreateNotification",
  service: NotificationService,
  requestStream: false,
  responseStream: false,
  requestType: notification_pb.CreateNotificationRequest,
  responseType: notification_pb.NotificationResponse
};

NotificationService.GetNotification = {
  methodName: "GetNotification",
  service: NotificationService,
  requestStream: false,
  responseStream: false,
  requestType: notification_pb.GetNotificationRequest,
  responseType: notification_pb.NotificationResponse
};

NotificationService.ListNotifications = {
  methodName: "ListNotifications",
  service: NotificationService,
  requestStream: false,
  responseStream: false,
  requestType: notification_pb.ListNotificationsRequest,
  responseType: notification_pb.ListNotificationsResponse
};

NotificationService.UpdateNotification = {
  methodName: "UpdateNotification",
  service: NotificationService,
  requestStream: false,
  responseStream: false,
  requestType: notification_pb.UpdateNotificationRequest,
  responseType: notification_pb.NotificationResponse
};

NotificationService.DeleteNotification = {
  methodName: "DeleteNotification",
  service: NotificationService,
  requestStream: false,
  responseStream: false,
  requestType: notification_pb.DeleteNotificationRequest,
  responseType: notification_pb.Empty
};

NotificationService.MarkAsRead = {
  methodName: "MarkAsRead",
  service: NotificationService,
  requestStream: false,
  responseStream: false,
  requestType: notification_pb.MarkAsReadRequest,
  responseType: notification_pb.NotificationResponse
};

NotificationService.MarkAllAsRead = {
  methodName: "MarkAllAsRead",
  service: NotificationService,
  requestStream: false,
  responseStream: false,
  requestType: notification_pb.MarkAllAsReadRequest,
  responseType: notification_pb.Empty
};

NotificationService.GetUnreadCount = {
  methodName: "GetUnreadCount",
  service: NotificationService,
  requestStream: false,
  responseStream: false,
  requestType: notification_pb.GetUnreadCountRequest,
  responseType: notification_pb.UnreadCountResponse
};

exports.NotificationService = NotificationService;

function NotificationServiceClient(serviceHost, options) {
  this.serviceHost = serviceHost;
  this.options = options || {};
}

NotificationServiceClient.prototype.createNotification = function createNotification(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(NotificationService.CreateNotification, {
    request: requestMessage,
    host: this.serviceHost,
    metadata: metadata,
    transport: this.options.transport,
    debug: this.options.debug,
    onEnd: function (response) {
      if (callback) {
        if (response.status !== grpc.Code.OK) {
          var err = new Error(response.statusMessage);
          err.code = response.status;
          err.metadata = response.trailers;
          callback(err, null);
        } else {
          callback(null, response.message);
        }
      }
    }
  });
  return {
    cancel: function () {
      callback = null;
      client.close();
    }
  };
};

NotificationServiceClient.prototype.getNotification = function getNotification(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(NotificationService.GetNotification, {
    request: requestMessage,
    host: this.serviceHost,
    metadata: metadata,
    transport: this.options.transport,
    debug: this.options.debug,
    onEnd: function (response) {
      if (callback) {
        if (response.status !== grpc.Code.OK) {
          var err = new Error(response.statusMessage);
          err.code = response.status;
          err.metadata = response.trailers;
          callback(err, null);
        } else {
          callback(null, response.message);
        }
      }
    }
  });
  return {
    cancel: function () {
      callback = null;
      client.close();
    }
  };
};

NotificationServiceClient.prototype.listNotifications = function listNotifications(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(NotificationService.ListNotifications, {
    request: requestMessage,
    host: this.serviceHost,
    metadata: metadata,
    transport: this.options.transport,
    debug: this.options.debug,
    onEnd: function (response) {
      if (callback) {
        if (response.status !== grpc.Code.OK) {
          var err = new Error(response.statusMessage);
          err.code = response.status;
          err.metadata = response.trailers;
          callback(err, null);
        } else {
          callback(null, response.message);
        }
      }
    }
  });
  return {
    cancel: function () {
      callback = null;
      client.close();
    }
  };
};

NotificationServiceClient.prototype.updateNotification = function updateNotification(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(NotificationService.UpdateNotification, {
    request: requestMessage,
    host: this.serviceHost,
    metadata: metadata,
    transport: this.options.transport,
    debug: this.options.debug,
    onEnd: function (response) {
      if (callback) {
        if (response.status !== grpc.Code.OK) {
          var err = new Error(response.statusMessage);
          err.code = response.status;
          err.metadata = response.trailers;
          callback(err, null);
        } else {
          callback(null, response.message);
        }
      }
    }
  });
  return {
    cancel: function () {
      callback = null;
      client.close();
    }
  };
};

NotificationServiceClient.prototype.deleteNotification = function deleteNotification(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(NotificationService.DeleteNotification, {
    request: requestMessage,
    host: this.serviceHost,
    metadata: metadata,
    transport: this.options.transport,
    debug: this.options.debug,
    onEnd: function (response) {
      if (callback) {
        if (response.status !== grpc.Code.OK) {
          var err = new Error(response.statusMessage);
          err.code = response.status;
          err.metadata = response.trailers;
          callback(err, null);
        } else {
          callback(null, response.message);
        }
      }
    }
  });
  return {
    cancel: function () {
      callback = null;
      client.close();
    }
  };
};

NotificationServiceClient.prototype.markAsRead = function markAsRead(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(NotificationService.MarkAsRead, {
    request: requestMessage,
    host: this.serviceHost,
    metadata: metadata,
    transport: this.options.transport,
    debug: this.options.debug,
    onEnd: function (response) {
      if (callback) {
        if (response.status !== grpc.Code.OK) {
          var err = new Error(response.statusMessage);
          err.code = response.status;
          err.metadata = response.trailers;
          callback(err, null);
        } else {
          callback(null, response.message);
        }
      }
    }
  });
  return {
    cancel: function () {
      callback = null;
      client.close();
    }
  };
};

NotificationServiceClient.prototype.markAllAsRead = function markAllAsRead(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(NotificationService.MarkAllAsRead, {
    request: requestMessage,
    host: this.serviceHost,
    metadata: metadata,
    transport: this.options.transport,
    debug: this.options.debug,
    onEnd: function (response) {
      if (callback) {
        if (response.status !== grpc.Code.OK) {
          var err = new Error(response.statusMessage);
          err.code = response.status;
          err.metadata = response.trailers;
          callback(err, null);
        } else {
          callback(null, response.message);
        }
      }
    }
  });
  return {
    cancel: function () {
      callback = null;
      client.close();
    }
  };
};

NotificationServiceClient.prototype.getUnreadCount = function getUnreadCount(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(NotificationService.GetUnreadCount, {
    request: requestMessage,
    host: this.serviceHost,
    metadata: metadata,
    transport: this.options.transport,
    debug: this.options.debug,
    onEnd: function (response) {
      if (callback) {
        if (response.status !== grpc.Code.OK) {
          var err = new Error(response.statusMessage);
          err.code = response.status;
          err.metadata = response.trailers;
          callback(err, null);
        } else {
          callback(null, response.message);
        }
      }
    }
  });
  return {
    cancel: function () {
      callback = null;
      client.close();
    }
  };
};

exports.NotificationServiceClient = NotificationServiceClient;

