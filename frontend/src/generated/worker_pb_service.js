// package: worker
// file: worker.proto

var worker_pb = require("./worker_pb");
var grpc = require("@improbable-eng/grpc-web").grpc;

var WorkerService = (function () {
  function WorkerService() {}
  WorkerService.serviceName = "worker.WorkerService";
  return WorkerService;
}());

WorkerService.ProvisionInfrastructure = {
  methodName: "ProvisionInfrastructure",
  service: WorkerService,
  requestStream: false,
  responseStream: false,
  requestType: worker_pb.ProvisionInfrastructureRequest,
  responseType: worker_pb.TaskResponse
};

WorkerService.DestroyInfrastructure = {
  methodName: "DestroyInfrastructure",
  service: WorkerService,
  requestStream: false,
  responseStream: false,
  requestType: worker_pb.DestroyInfrastructureRequest,
  responseType: worker_pb.TaskResponse
};

WorkerService.ProvisionMicroservice = {
  methodName: "ProvisionMicroservice",
  service: WorkerService,
  requestStream: false,
  responseStream: false,
  requestType: worker_pb.ProvisionMicroserviceRequest,
  responseType: worker_pb.TaskResponse
};

WorkerService.DestroyMicroservice = {
  methodName: "DestroyMicroservice",
  service: WorkerService,
  requestStream: false,
  responseStream: false,
  requestType: worker_pb.DestroyMicroserviceRequest,
  responseType: worker_pb.TaskResponse
};

WorkerService.CleanupStuckDeployments = {
  methodName: "CleanupStuckDeployments",
  service: WorkerService,
  requestStream: false,
  responseStream: false,
  requestType: worker_pb.Empty,
  responseType: worker_pb.TaskResponse
};

WorkerService.CleanupExpiredRefreshTokens = {
  methodName: "CleanupExpiredRefreshTokens",
  service: WorkerService,
  requestStream: false,
  responseStream: false,
  requestType: worker_pb.Empty,
  responseType: worker_pb.TaskResponse
};

WorkerService.PollGitHubActionsStatus = {
  methodName: "PollGitHubActionsStatus",
  service: WorkerService,
  requestStream: false,
  responseStream: false,
  requestType: worker_pb.Empty,
  responseType: worker_pb.TaskResponse
};

WorkerService.ProcessGitHubWebhook = {
  methodName: "ProcessGitHubWebhook",
  service: WorkerService,
  requestStream: false,
  responseStream: false,
  requestType: worker_pb.ProcessGitHubWebhookRequest,
  responseType: worker_pb.ProcessGitHubWebhookResponse
};

WorkerService.GetTaskStatus = {
  methodName: "GetTaskStatus",
  service: WorkerService,
  requestStream: false,
  responseStream: false,
  requestType: worker_pb.GetTaskStatusRequest,
  responseType: worker_pb.TaskStatusResponse
};

exports.WorkerService = WorkerService;

function WorkerServiceClient(serviceHost, options) {
  this.serviceHost = serviceHost;
  this.options = options || {};
}

WorkerServiceClient.prototype.provisionInfrastructure = function provisionInfrastructure(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(WorkerService.ProvisionInfrastructure, {
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

WorkerServiceClient.prototype.destroyInfrastructure = function destroyInfrastructure(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(WorkerService.DestroyInfrastructure, {
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

WorkerServiceClient.prototype.provisionMicroservice = function provisionMicroservice(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(WorkerService.ProvisionMicroservice, {
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

WorkerServiceClient.prototype.destroyMicroservice = function destroyMicroservice(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(WorkerService.DestroyMicroservice, {
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

WorkerServiceClient.prototype.cleanupStuckDeployments = function cleanupStuckDeployments(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(WorkerService.CleanupStuckDeployments, {
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

WorkerServiceClient.prototype.cleanupExpiredRefreshTokens = function cleanupExpiredRefreshTokens(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(WorkerService.CleanupExpiredRefreshTokens, {
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

WorkerServiceClient.prototype.pollGitHubActionsStatus = function pollGitHubActionsStatus(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(WorkerService.PollGitHubActionsStatus, {
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

WorkerServiceClient.prototype.processGitHubWebhook = function processGitHubWebhook(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(WorkerService.ProcessGitHubWebhook, {
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

WorkerServiceClient.prototype.getTaskStatus = function getTaskStatus(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(WorkerService.GetTaskStatus, {
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

exports.WorkerServiceClient = WorkerServiceClient;

