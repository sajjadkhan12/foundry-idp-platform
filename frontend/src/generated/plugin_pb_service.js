// package: plugin
// file: plugin.proto

var plugin_pb = require("./plugin_pb");
var grpc = require("@improbable-eng/grpc-web").grpc;

var PluginService = (function () {
  function PluginService() {}
  PluginService.serviceName = "plugin.PluginService";
  return PluginService;
}());

PluginService.UploadPlugin = {
  methodName: "UploadPlugin",
  service: PluginService,
  requestStream: false,
  responseStream: false,
  requestType: plugin_pb.UploadPluginRequest,
  responseType: plugin_pb.PluginVersionResponse
};

PluginService.UploadMicroserviceTemplate = {
  methodName: "UploadMicroserviceTemplate",
  service: PluginService,
  requestStream: false,
  responseStream: false,
  requestType: plugin_pb.UploadMicroserviceTemplateRequest,
  responseType: plugin_pb.PluginVersionResponse
};

PluginService.ListPlugins = {
  methodName: "ListPlugins",
  service: PluginService,
  requestStream: false,
  responseStream: false,
  requestType: plugin_pb.ListPluginsRequest,
  responseType: plugin_pb.ListPluginsResponse
};

PluginService.GetPlugin = {
  methodName: "GetPlugin",
  service: PluginService,
  requestStream: false,
  responseStream: false,
  requestType: plugin_pb.GetPluginRequest,
  responseType: plugin_pb.PluginResponse
};

PluginService.DeletePlugin = {
  methodName: "DeletePlugin",
  service: PluginService,
  requestStream: false,
  responseStream: false,
  requestType: plugin_pb.DeletePluginRequest,
  responseType: plugin_pb.Empty
};

PluginService.LockPlugin = {
  methodName: "LockPlugin",
  service: PluginService,
  requestStream: false,
  responseStream: false,
  requestType: plugin_pb.LockPluginRequest,
  responseType: plugin_pb.Empty
};

PluginService.UnlockPlugin = {
  methodName: "UnlockPlugin",
  service: PluginService,
  requestStream: false,
  responseStream: false,
  requestType: plugin_pb.UnlockPluginRequest,
  responseType: plugin_pb.Empty
};

PluginService.ListPluginVersions = {
  methodName: "ListPluginVersions",
  service: PluginService,
  requestStream: false,
  responseStream: false,
  requestType: plugin_pb.ListPluginVersionsRequest,
  responseType: plugin_pb.ListPluginVersionsResponse
};

PluginService.GetPluginVersion = {
  methodName: "GetPluginVersion",
  service: PluginService,
  requestStream: false,
  responseStream: false,
  requestType: plugin_pb.GetPluginVersionRequest,
  responseType: plugin_pb.PluginVersionResponse
};

PluginService.RequestPluginAccess = {
  methodName: "RequestPluginAccess",
  service: PluginService,
  requestStream: false,
  responseStream: false,
  requestType: plugin_pb.RequestPluginAccessRequest,
  responseType: plugin_pb.PluginAccessRequestResponse
};

PluginService.GrantPluginAccess = {
  methodName: "GrantPluginAccess",
  service: PluginService,
  requestStream: false,
  responseStream: false,
  requestType: plugin_pb.GrantPluginAccessRequest,
  responseType: plugin_pb.PluginAccessResponse
};

PluginService.RejectPluginAccess = {
  methodName: "RejectPluginAccess",
  service: PluginService,
  requestStream: false,
  responseStream: false,
  requestType: plugin_pb.RejectPluginAccessRequest,
  responseType: plugin_pb.Empty
};

PluginService.RevokePluginAccess = {
  methodName: "RevokePluginAccess",
  service: PluginService,
  requestStream: false,
  responseStream: false,
  requestType: plugin_pb.RevokePluginAccessRequest,
  responseType: plugin_pb.Empty
};

PluginService.RestorePluginAccess = {
  methodName: "RestorePluginAccess",
  service: PluginService,
  requestStream: false,
  responseStream: false,
  requestType: plugin_pb.RestorePluginAccessRequest,
  responseType: plugin_pb.Empty
};

PluginService.ListAccessRequests = {
  methodName: "ListAccessRequests",
  service: PluginService,
  requestStream: false,
  responseStream: false,
  requestType: plugin_pb.ListAccessRequestsRequest,
  responseType: plugin_pb.ListAccessRequestsResponse
};

PluginService.ListAccessGrants = {
  methodName: "ListAccessGrants",
  service: PluginService,
  requestStream: false,
  responseStream: false,
  requestType: plugin_pb.ListAccessGrantsRequest,
  responseType: plugin_pb.ListAccessGrantsResponse
};

PluginService.ProvisionPlugin = {
  methodName: "ProvisionPlugin",
  service: PluginService,
  requestStream: false,
  responseStream: false,
  requestType: plugin_pb.ProvisionPluginRequest,
  responseType: plugin_pb.ProvisionResponse
};

PluginService.GetJob = {
  methodName: "GetJob",
  service: PluginService,
  requestStream: false,
  responseStream: false,
  requestType: plugin_pb.GetJobRequest,
  responseType: plugin_pb.JobResponse
};

PluginService.ListJobs = {
  methodName: "ListJobs",
  service: PluginService,
  requestStream: false,
  responseStream: false,
  requestType: plugin_pb.ListJobsRequest,
  responseType: plugin_pb.ListJobsResponse
};

PluginService.GetJobLogs = {
  methodName: "GetJobLogs",
  service: PluginService,
  requestStream: false,
  responseStream: false,
  requestType: plugin_pb.GetJobLogsRequest,
  responseType: plugin_pb.JobLogsResponse
};

PluginService.CancelJob = {
  methodName: "CancelJob",
  service: PluginService,
  requestStream: false,
  responseStream: false,
  requestType: plugin_pb.CancelJobRequest,
  responseType: plugin_pb.Empty
};

PluginService.DeleteJob = {
  methodName: "DeleteJob",
  service: PluginService,
  requestStream: false,
  responseStream: false,
  requestType: plugin_pb.DeleteJobRequest,
  responseType: plugin_pb.Empty
};

exports.PluginService = PluginService;

function PluginServiceClient(serviceHost, options) {
  this.serviceHost = serviceHost;
  this.options = options || {};
}

PluginServiceClient.prototype.uploadPlugin = function uploadPlugin(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(PluginService.UploadPlugin, {
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

PluginServiceClient.prototype.uploadMicroserviceTemplate = function uploadMicroserviceTemplate(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(PluginService.UploadMicroserviceTemplate, {
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

PluginServiceClient.prototype.listPlugins = function listPlugins(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(PluginService.ListPlugins, {
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

PluginServiceClient.prototype.getPlugin = function getPlugin(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(PluginService.GetPlugin, {
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

PluginServiceClient.prototype.deletePlugin = function deletePlugin(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(PluginService.DeletePlugin, {
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

PluginServiceClient.prototype.lockPlugin = function lockPlugin(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(PluginService.LockPlugin, {
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

PluginServiceClient.prototype.unlockPlugin = function unlockPlugin(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(PluginService.UnlockPlugin, {
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

PluginServiceClient.prototype.listPluginVersions = function listPluginVersions(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(PluginService.ListPluginVersions, {
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

PluginServiceClient.prototype.getPluginVersion = function getPluginVersion(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(PluginService.GetPluginVersion, {
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

PluginServiceClient.prototype.requestPluginAccess = function requestPluginAccess(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(PluginService.RequestPluginAccess, {
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

PluginServiceClient.prototype.grantPluginAccess = function grantPluginAccess(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(PluginService.GrantPluginAccess, {
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

PluginServiceClient.prototype.rejectPluginAccess = function rejectPluginAccess(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(PluginService.RejectPluginAccess, {
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

PluginServiceClient.prototype.revokePluginAccess = function revokePluginAccess(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(PluginService.RevokePluginAccess, {
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

PluginServiceClient.prototype.restorePluginAccess = function restorePluginAccess(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(PluginService.RestorePluginAccess, {
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

PluginServiceClient.prototype.listAccessRequests = function listAccessRequests(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(PluginService.ListAccessRequests, {
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

PluginServiceClient.prototype.listAccessGrants = function listAccessGrants(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(PluginService.ListAccessGrants, {
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

PluginServiceClient.prototype.provisionPlugin = function provisionPlugin(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(PluginService.ProvisionPlugin, {
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

PluginServiceClient.prototype.getJob = function getJob(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(PluginService.GetJob, {
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

PluginServiceClient.prototype.listJobs = function listJobs(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(PluginService.ListJobs, {
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

PluginServiceClient.prototype.getJobLogs = function getJobLogs(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(PluginService.GetJobLogs, {
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

PluginServiceClient.prototype.cancelJob = function cancelJob(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(PluginService.CancelJob, {
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

PluginServiceClient.prototype.deleteJob = function deleteJob(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(PluginService.DeleteJob, {
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

exports.PluginServiceClient = PluginServiceClient;

