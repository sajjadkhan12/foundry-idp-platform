// package: deployment
// file: deployment.proto

var deployment_pb = require("./deployment_pb");
var grpc = require("@improbable-eng/grpc-web").grpc;

var DeploymentService = (function () {
  function DeploymentService() {}
  DeploymentService.serviceName = "deployment.DeploymentService";
  return DeploymentService;
}());

DeploymentService.CreateDeployment = {
  methodName: "CreateDeployment",
  service: DeploymentService,
  requestStream: false,
  responseStream: false,
  requestType: deployment_pb.CreateDeploymentRequest,
  responseType: deployment_pb.DeploymentResponse
};

DeploymentService.GetDeployment = {
  methodName: "GetDeployment",
  service: DeploymentService,
  requestStream: false,
  responseStream: false,
  requestType: deployment_pb.GetDeploymentRequest,
  responseType: deployment_pb.DeploymentResponse
};

DeploymentService.UpdateDeployment = {
  methodName: "UpdateDeployment",
  service: DeploymentService,
  requestStream: false,
  responseStream: false,
  requestType: deployment_pb.UpdateDeploymentRequest,
  responseType: deployment_pb.DeploymentResponse
};

DeploymentService.DeleteDeployment = {
  methodName: "DeleteDeployment",
  service: DeploymentService,
  requestStream: false,
  responseStream: false,
  requestType: deployment_pb.DeleteDeploymentRequest,
  responseType: deployment_pb.Empty
};

DeploymentService.ListDeployments = {
  methodName: "ListDeployments",
  service: DeploymentService,
  requestStream: false,
  responseStream: false,
  requestType: deployment_pb.ListDeploymentsRequest,
  responseType: deployment_pb.ListDeploymentsResponse
};

DeploymentService.GetDeploymentHistory = {
  methodName: "GetDeploymentHistory",
  service: DeploymentService,
  requestStream: false,
  responseStream: false,
  requestType: deployment_pb.GetDeploymentHistoryRequest,
  responseType: deployment_pb.ListDeploymentHistoryResponse
};

DeploymentService.GetDeploymentHistoryVersion = {
  methodName: "GetDeploymentHistoryVersion",
  service: DeploymentService,
  requestStream: false,
  responseStream: false,
  requestType: deployment_pb.GetDeploymentHistoryVersionRequest,
  responseType: deployment_pb.DeploymentHistoryResponse
};

DeploymentService.AddDeploymentTag = {
  methodName: "AddDeploymentTag",
  service: DeploymentService,
  requestStream: false,
  responseStream: false,
  requestType: deployment_pb.AddDeploymentTagRequest,
  responseType: deployment_pb.Empty
};

DeploymentService.RemoveDeploymentTag = {
  methodName: "RemoveDeploymentTag",
  service: DeploymentService,
  requestStream: false,
  responseStream: false,
  requestType: deployment_pb.RemoveDeploymentTagRequest,
  responseType: deployment_pb.Empty
};

DeploymentService.ListDeploymentTags = {
  methodName: "ListDeploymentTags",
  service: DeploymentService,
  requestStream: false,
  responseStream: false,
  requestType: deployment_pb.ListDeploymentTagsRequest,
  responseType: deployment_pb.ListDeploymentTagsResponse
};

DeploymentService.UpdateCICDStatus = {
  methodName: "UpdateCICDStatus",
  service: DeploymentService,
  requestStream: false,
  responseStream: false,
  requestType: deployment_pb.UpdateCICDStatusRequest,
  responseType: deployment_pb.Empty
};

DeploymentService.GetCICDStatus = {
  methodName: "GetCICDStatus",
  service: DeploymentService,
  requestStream: false,
  responseStream: false,
  requestType: deployment_pb.GetCICDStatusRequest,
  responseType: deployment_pb.CICDStatusResponse
};

DeploymentService.GetDeploymentStats = {
  methodName: "GetDeploymentStats",
  service: DeploymentService,
  requestStream: false,
  responseStream: false,
  requestType: deployment_pb.GetDeploymentStatsRequest,
  responseType: deployment_pb.DeploymentStatsResponse
};

DeploymentService.GetDeploymentCosts = {
  methodName: "GetDeploymentCosts",
  service: DeploymentService,
  requestStream: false,
  responseStream: false,
  requestType: deployment_pb.GetDeploymentCostsRequest,
  responseType: deployment_pb.DeploymentCostsResponse
};

exports.DeploymentService = DeploymentService;

function DeploymentServiceClient(serviceHost, options) {
  this.serviceHost = serviceHost;
  this.options = options || {};
}

DeploymentServiceClient.prototype.createDeployment = function createDeployment(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(DeploymentService.CreateDeployment, {
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

DeploymentServiceClient.prototype.getDeployment = function getDeployment(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(DeploymentService.GetDeployment, {
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

DeploymentServiceClient.prototype.updateDeployment = function updateDeployment(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(DeploymentService.UpdateDeployment, {
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

DeploymentServiceClient.prototype.deleteDeployment = function deleteDeployment(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(DeploymentService.DeleteDeployment, {
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

DeploymentServiceClient.prototype.listDeployments = function listDeployments(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(DeploymentService.ListDeployments, {
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

DeploymentServiceClient.prototype.getDeploymentHistory = function getDeploymentHistory(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(DeploymentService.GetDeploymentHistory, {
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

DeploymentServiceClient.prototype.getDeploymentHistoryVersion = function getDeploymentHistoryVersion(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(DeploymentService.GetDeploymentHistoryVersion, {
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

DeploymentServiceClient.prototype.addDeploymentTag = function addDeploymentTag(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(DeploymentService.AddDeploymentTag, {
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

DeploymentServiceClient.prototype.removeDeploymentTag = function removeDeploymentTag(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(DeploymentService.RemoveDeploymentTag, {
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

DeploymentServiceClient.prototype.listDeploymentTags = function listDeploymentTags(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(DeploymentService.ListDeploymentTags, {
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

DeploymentServiceClient.prototype.updateCICDStatus = function updateCICDStatus(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(DeploymentService.UpdateCICDStatus, {
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

DeploymentServiceClient.prototype.getCICDStatus = function getCICDStatus(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(DeploymentService.GetCICDStatus, {
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

DeploymentServiceClient.prototype.getDeploymentStats = function getDeploymentStats(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(DeploymentService.GetDeploymentStats, {
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

DeploymentServiceClient.prototype.getDeploymentCosts = function getDeploymentCosts(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(DeploymentService.GetDeploymentCosts, {
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

exports.DeploymentServiceClient = DeploymentServiceClient;

