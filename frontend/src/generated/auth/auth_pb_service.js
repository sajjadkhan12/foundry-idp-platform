// package: auth
// file: auth.proto

var auth_pb = require("./auth_pb");
var grpc = require("@improbable-eng/grpc-web").grpc;

var AuthenticationService = (function () {
  function AuthenticationService() {}
  AuthenticationService.serviceName = "auth.AuthenticationService";
  return AuthenticationService;
}());

AuthenticationService.Login = {
  methodName: "Login",
  service: AuthenticationService,
  requestStream: false,
  responseStream: false,
  requestType: auth_pb.LoginRequest,
  responseType: auth_pb.TokenResponse
};

AuthenticationService.RefreshToken = {
  methodName: "RefreshToken",
  service: AuthenticationService,
  requestStream: false,
  responseStream: false,
  requestType: auth_pb.RefreshTokenRequest,
  responseType: auth_pb.TokenResponse
};

AuthenticationService.Logout = {
  methodName: "Logout",
  service: AuthenticationService,
  requestStream: false,
  responseStream: false,
  requestType: auth_pb.LogoutRequest,
  responseType: auth_pb.Empty
};

AuthenticationService.ValidateToken = {
  methodName: "ValidateToken",
  service: AuthenticationService,
  requestStream: false,
  responseStream: false,
  requestType: auth_pb.ValidateTokenRequest,
  responseType: auth_pb.UserInfo
};

AuthenticationService.Register = {
  methodName: "Register",
  service: AuthenticationService,
  requestStream: false,
  responseStream: false,
  requestType: auth_pb.RegisterRequest,
  responseType: auth_pb.UserResponse
};

exports.AuthenticationService = AuthenticationService;

function AuthenticationServiceClient(serviceHost, options) {
  this.serviceHost = serviceHost;
  this.options = options || {};
}

AuthenticationServiceClient.prototype.login = function login(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(AuthenticationService.Login, {
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

AuthenticationServiceClient.prototype.refreshToken = function refreshToken(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(AuthenticationService.RefreshToken, {
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

AuthenticationServiceClient.prototype.logout = function logout(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(AuthenticationService.Logout, {
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

AuthenticationServiceClient.prototype.validateToken = function validateToken(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(AuthenticationService.ValidateToken, {
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

AuthenticationServiceClient.prototype.register = function register(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(AuthenticationService.Register, {
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

exports.AuthenticationServiceClient = AuthenticationServiceClient;

var AuthorizationService = (function () {
  function AuthorizationService() {}
  AuthorizationService.serviceName = "auth.AuthorizationService";
  return AuthorizationService;
}());

AuthorizationService.CheckPermission = {
  methodName: "CheckPermission",
  service: AuthorizationService,
  requestStream: false,
  responseStream: false,
  requestType: auth_pb.PermissionCheckRequest,
  responseType: auth_pb.PermissionCheckResponse
};

AuthorizationService.GetUserRoles = {
  methodName: "GetUserRoles",
  service: AuthorizationService,
  requestStream: false,
  responseStream: false,
  requestType: auth_pb.GetUserRolesRequest,
  responseType: auth_pb.GetUserRolesResponse
};

AuthorizationService.GetUserPermissions = {
  methodName: "GetUserPermissions",
  service: AuthorizationService,
  requestStream: false,
  responseStream: false,
  requestType: auth_pb.GetUserPermissionsRequest,
  responseType: auth_pb.GetUserPermissionsResponse
};

AuthorizationService.IsPlatformAdmin = {
  methodName: "IsPlatformAdmin",
  service: AuthorizationService,
  requestStream: false,
  responseStream: false,
  requestType: auth_pb.IsPlatformAdminRequest,
  responseType: auth_pb.IsPlatformAdminResponse
};

exports.AuthorizationService = AuthorizationService;

function AuthorizationServiceClient(serviceHost, options) {
  this.serviceHost = serviceHost;
  this.options = options || {};
}

AuthorizationServiceClient.prototype.checkPermission = function checkPermission(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(AuthorizationService.CheckPermission, {
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

AuthorizationServiceClient.prototype.getUserRoles = function getUserRoles(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(AuthorizationService.GetUserRoles, {
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

AuthorizationServiceClient.prototype.getUserPermissions = function getUserPermissions(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(AuthorizationService.GetUserPermissions, {
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

AuthorizationServiceClient.prototype.isPlatformAdmin = function isPlatformAdmin(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(AuthorizationService.IsPlatformAdmin, {
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

exports.AuthorizationServiceClient = AuthorizationServiceClient;

var UserService = (function () {
  function UserService() {}
  UserService.serviceName = "auth.UserService";
  return UserService;
}());

UserService.CreateUser = {
  methodName: "CreateUser",
  service: UserService,
  requestStream: false,
  responseStream: false,
  requestType: auth_pb.CreateUserRequest,
  responseType: auth_pb.UserResponse
};

UserService.UpdateUser = {
  methodName: "UpdateUser",
  service: UserService,
  requestStream: false,
  responseStream: false,
  requestType: auth_pb.UpdateUserRequest,
  responseType: auth_pb.UserResponse
};

UserService.DeleteUser = {
  methodName: "DeleteUser",
  service: UserService,
  requestStream: false,
  responseStream: false,
  requestType: auth_pb.DeleteUserRequest,
  responseType: auth_pb.Empty
};

UserService.GetUser = {
  methodName: "GetUser",
  service: UserService,
  requestStream: false,
  responseStream: false,
  requestType: auth_pb.GetUserRequest,
  responseType: auth_pb.UserResponse
};

UserService.ListUsers = {
  methodName: "ListUsers",
  service: UserService,
  requestStream: false,
  responseStream: false,
  requestType: auth_pb.ListUsersRequest,
  responseType: auth_pb.ListUsersResponse
};

UserService.GetCurrentUser = {
  methodName: "GetCurrentUser",
  service: UserService,
  requestStream: false,
  responseStream: false,
  requestType: auth_pb.GetCurrentUserRequest,
  responseType: auth_pb.UserResponse
};

UserService.UpdateCurrentUser = {
  methodName: "UpdateCurrentUser",
  service: UserService,
  requestStream: false,
  responseStream: false,
  requestType: auth_pb.UpdateCurrentUserRequest,
  responseType: auth_pb.UserResponse
};

UserService.ChangePassword = {
  methodName: "ChangePassword",
  service: UserService,
  requestStream: false,
  responseStream: false,
  requestType: auth_pb.ChangePasswordRequest,
  responseType: auth_pb.Empty
};

exports.UserService = UserService;

function UserServiceClient(serviceHost, options) {
  this.serviceHost = serviceHost;
  this.options = options || {};
}

UserServiceClient.prototype.createUser = function createUser(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(UserService.CreateUser, {
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

UserServiceClient.prototype.updateUser = function updateUser(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(UserService.UpdateUser, {
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

UserServiceClient.prototype.deleteUser = function deleteUser(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(UserService.DeleteUser, {
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

UserServiceClient.prototype.getUser = function getUser(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(UserService.GetUser, {
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

UserServiceClient.prototype.listUsers = function listUsers(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(UserService.ListUsers, {
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

UserServiceClient.prototype.getCurrentUser = function getCurrentUser(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(UserService.GetCurrentUser, {
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

UserServiceClient.prototype.updateCurrentUser = function updateCurrentUser(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(UserService.UpdateCurrentUser, {
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

UserServiceClient.prototype.changePassword = function changePassword(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(UserService.ChangePassword, {
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

exports.UserServiceClient = UserServiceClient;

var RoleService = (function () {
  function RoleService() {}
  RoleService.serviceName = "auth.RoleService";
  return RoleService;
}());

RoleService.CreateRole = {
  methodName: "CreateRole",
  service: RoleService,
  requestStream: false,
  responseStream: false,
  requestType: auth_pb.CreateRoleRequest,
  responseType: auth_pb.RoleResponse
};

RoleService.UpdateRole = {
  methodName: "UpdateRole",
  service: RoleService,
  requestStream: false,
  responseStream: false,
  requestType: auth_pb.UpdateRoleRequest,
  responseType: auth_pb.RoleResponse
};

RoleService.DeleteRole = {
  methodName: "DeleteRole",
  service: RoleService,
  requestStream: false,
  responseStream: false,
  requestType: auth_pb.DeleteRoleRequest,
  responseType: auth_pb.Empty
};

RoleService.GetRole = {
  methodName: "GetRole",
  service: RoleService,
  requestStream: false,
  responseStream: false,
  requestType: auth_pb.GetRoleRequest,
  responseType: auth_pb.RoleResponse
};

RoleService.ListRoles = {
  methodName: "ListRoles",
  service: RoleService,
  requestStream: false,
  responseStream: false,
  requestType: auth_pb.ListRolesRequest,
  responseType: auth_pb.ListRolesResponse
};

RoleService.AssignRole = {
  methodName: "AssignRole",
  service: RoleService,
  requestStream: false,
  responseStream: false,
  requestType: auth_pb.AssignRoleRequest,
  responseType: auth_pb.Empty
};

RoleService.RemoveRole = {
  methodName: "RemoveRole",
  service: RoleService,
  requestStream: false,
  responseStream: false,
  requestType: auth_pb.RemoveRoleRequest,
  responseType: auth_pb.Empty
};

exports.RoleService = RoleService;

function RoleServiceClient(serviceHost, options) {
  this.serviceHost = serviceHost;
  this.options = options || {};
}

RoleServiceClient.prototype.createRole = function createRole(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(RoleService.CreateRole, {
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

RoleServiceClient.prototype.updateRole = function updateRole(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(RoleService.UpdateRole, {
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

RoleServiceClient.prototype.deleteRole = function deleteRole(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(RoleService.DeleteRole, {
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

RoleServiceClient.prototype.getRole = function getRole(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(RoleService.GetRole, {
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

RoleServiceClient.prototype.listRoles = function listRoles(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(RoleService.ListRoles, {
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

RoleServiceClient.prototype.assignRole = function assignRole(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(RoleService.AssignRole, {
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

RoleServiceClient.prototype.removeRole = function removeRole(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(RoleService.RemoveRole, {
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

exports.RoleServiceClient = RoleServiceClient;

var GroupService = (function () {
  function GroupService() {}
  GroupService.serviceName = "auth.GroupService";
  return GroupService;
}());

GroupService.CreateGroup = {
  methodName: "CreateGroup",
  service: GroupService,
  requestStream: false,
  responseStream: false,
  requestType: auth_pb.CreateGroupRequest,
  responseType: auth_pb.GroupResponse
};

GroupService.UpdateGroup = {
  methodName: "UpdateGroup",
  service: GroupService,
  requestStream: false,
  responseStream: false,
  requestType: auth_pb.UpdateGroupRequest,
  responseType: auth_pb.GroupResponse
};

GroupService.DeleteGroup = {
  methodName: "DeleteGroup",
  service: GroupService,
  requestStream: false,
  responseStream: false,
  requestType: auth_pb.DeleteGroupRequest,
  responseType: auth_pb.Empty
};

GroupService.GetGroup = {
  methodName: "GetGroup",
  service: GroupService,
  requestStream: false,
  responseStream: false,
  requestType: auth_pb.GetGroupRequest,
  responseType: auth_pb.GroupResponse
};

GroupService.ListGroups = {
  methodName: "ListGroups",
  service: GroupService,
  requestStream: false,
  responseStream: false,
  requestType: auth_pb.ListGroupsRequest,
  responseType: auth_pb.ListGroupsResponse
};

GroupService.AddGroupMember = {
  methodName: "AddGroupMember",
  service: GroupService,
  requestStream: false,
  responseStream: false,
  requestType: auth_pb.AddGroupMemberRequest,
  responseType: auth_pb.Empty
};

GroupService.RemoveGroupMember = {
  methodName: "RemoveGroupMember",
  service: GroupService,
  requestStream: false,
  responseStream: false,
  requestType: auth_pb.RemoveGroupMemberRequest,
  responseType: auth_pb.Empty
};

exports.GroupService = GroupService;

function GroupServiceClient(serviceHost, options) {
  this.serviceHost = serviceHost;
  this.options = options || {};
}

GroupServiceClient.prototype.createGroup = function createGroup(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(GroupService.CreateGroup, {
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

GroupServiceClient.prototype.updateGroup = function updateGroup(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(GroupService.UpdateGroup, {
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

GroupServiceClient.prototype.deleteGroup = function deleteGroup(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(GroupService.DeleteGroup, {
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

GroupServiceClient.prototype.getGroup = function getGroup(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(GroupService.GetGroup, {
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

GroupServiceClient.prototype.listGroups = function listGroups(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(GroupService.ListGroups, {
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

GroupServiceClient.prototype.addGroupMember = function addGroupMember(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(GroupService.AddGroupMember, {
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

GroupServiceClient.prototype.removeGroupMember = function removeGroupMember(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(GroupService.RemoveGroupMember, {
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

exports.GroupServiceClient = GroupServiceClient;

var BusinessUnitService = (function () {
  function BusinessUnitService() {}
  BusinessUnitService.serviceName = "auth.BusinessUnitService";
  return BusinessUnitService;
}());

BusinessUnitService.CreateBusinessUnit = {
  methodName: "CreateBusinessUnit",
  service: BusinessUnitService,
  requestStream: false,
  responseStream: false,
  requestType: auth_pb.CreateBusinessUnitRequest,
  responseType: auth_pb.BusinessUnitResponse
};

BusinessUnitService.UpdateBusinessUnit = {
  methodName: "UpdateBusinessUnit",
  service: BusinessUnitService,
  requestStream: false,
  responseStream: false,
  requestType: auth_pb.UpdateBusinessUnitRequest,
  responseType: auth_pb.BusinessUnitResponse
};

BusinessUnitService.DeleteBusinessUnit = {
  methodName: "DeleteBusinessUnit",
  service: BusinessUnitService,
  requestStream: false,
  responseStream: false,
  requestType: auth_pb.DeleteBusinessUnitRequest,
  responseType: auth_pb.Empty
};

BusinessUnitService.GetBusinessUnit = {
  methodName: "GetBusinessUnit",
  service: BusinessUnitService,
  requestStream: false,
  responseStream: false,
  requestType: auth_pb.GetBusinessUnitRequest,
  responseType: auth_pb.BusinessUnitResponse
};

BusinessUnitService.ListBusinessUnits = {
  methodName: "ListBusinessUnits",
  service: BusinessUnitService,
  requestStream: false,
  responseStream: false,
  requestType: auth_pb.ListBusinessUnitsRequest,
  responseType: auth_pb.ListBusinessUnitsResponse
};

BusinessUnitService.AddBusinessUnitMember = {
  methodName: "AddBusinessUnitMember",
  service: BusinessUnitService,
  requestStream: false,
  responseStream: false,
  requestType: auth_pb.AddBusinessUnitMemberRequest,
  responseType: auth_pb.Empty
};

BusinessUnitService.RemoveBusinessUnitMember = {
  methodName: "RemoveBusinessUnitMember",
  service: BusinessUnitService,
  requestStream: false,
  responseStream: false,
  requestType: auth_pb.RemoveBusinessUnitMemberRequest,
  responseType: auth_pb.Empty
};

BusinessUnitService.ListBusinessUnitMembers = {
  methodName: "ListBusinessUnitMembers",
  service: BusinessUnitService,
  requestStream: false,
  responseStream: false,
  requestType: auth_pb.ListBusinessUnitMembersRequest,
  responseType: auth_pb.ListBusinessUnitMembersResponse
};

exports.BusinessUnitService = BusinessUnitService;

function BusinessUnitServiceClient(serviceHost, options) {
  this.serviceHost = serviceHost;
  this.options = options || {};
}

BusinessUnitServiceClient.prototype.createBusinessUnit = function createBusinessUnit(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(BusinessUnitService.CreateBusinessUnit, {
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

BusinessUnitServiceClient.prototype.updateBusinessUnit = function updateBusinessUnit(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(BusinessUnitService.UpdateBusinessUnit, {
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

BusinessUnitServiceClient.prototype.deleteBusinessUnit = function deleteBusinessUnit(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(BusinessUnitService.DeleteBusinessUnit, {
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

BusinessUnitServiceClient.prototype.getBusinessUnit = function getBusinessUnit(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(BusinessUnitService.GetBusinessUnit, {
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

BusinessUnitServiceClient.prototype.listBusinessUnits = function listBusinessUnits(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(BusinessUnitService.ListBusinessUnits, {
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

BusinessUnitServiceClient.prototype.addBusinessUnitMember = function addBusinessUnitMember(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(BusinessUnitService.AddBusinessUnitMember, {
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

BusinessUnitServiceClient.prototype.removeBusinessUnitMember = function removeBusinessUnitMember(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(BusinessUnitService.RemoveBusinessUnitMember, {
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

BusinessUnitServiceClient.prototype.listBusinessUnitMembers = function listBusinessUnitMembers(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(BusinessUnitService.ListBusinessUnitMembers, {
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

exports.BusinessUnitServiceClient = BusinessUnitServiceClient;

var OrganizationService = (function () {
  function OrganizationService() {}
  OrganizationService.serviceName = "auth.OrganizationService";
  return OrganizationService;
}());

OrganizationService.CreateOrganization = {
  methodName: "CreateOrganization",
  service: OrganizationService,
  requestStream: false,
  responseStream: false,
  requestType: auth_pb.CreateOrganizationRequest,
  responseType: auth_pb.OrganizationResponse
};

OrganizationService.UpdateOrganization = {
  methodName: "UpdateOrganization",
  service: OrganizationService,
  requestStream: false,
  responseStream: false,
  requestType: auth_pb.UpdateOrganizationRequest,
  responseType: auth_pb.OrganizationResponse
};

OrganizationService.DeleteOrganization = {
  methodName: "DeleteOrganization",
  service: OrganizationService,
  requestStream: false,
  responseStream: false,
  requestType: auth_pb.DeleteOrganizationRequest,
  responseType: auth_pb.Empty
};

OrganizationService.GetOrganization = {
  methodName: "GetOrganization",
  service: OrganizationService,
  requestStream: false,
  responseStream: false,
  requestType: auth_pb.GetOrganizationRequest,
  responseType: auth_pb.OrganizationResponse
};

OrganizationService.ListOrganizations = {
  methodName: "ListOrganizations",
  service: OrganizationService,
  requestStream: false,
  responseStream: false,
  requestType: auth_pb.ListOrganizationsRequest,
  responseType: auth_pb.ListOrganizationsResponse
};

OrganizationService.GetCurrentOrganization = {
  methodName: "GetCurrentOrganization",
  service: OrganizationService,
  requestStream: false,
  responseStream: false,
  requestType: auth_pb.GetCurrentOrganizationRequest,
  responseType: auth_pb.OrganizationResponse
};

exports.OrganizationService = OrganizationService;

function OrganizationServiceClient(serviceHost, options) {
  this.serviceHost = serviceHost;
  this.options = options || {};
}

OrganizationServiceClient.prototype.createOrganization = function createOrganization(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(OrganizationService.CreateOrganization, {
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

OrganizationServiceClient.prototype.updateOrganization = function updateOrganization(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(OrganizationService.UpdateOrganization, {
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

OrganizationServiceClient.prototype.deleteOrganization = function deleteOrganization(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(OrganizationService.DeleteOrganization, {
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

OrganizationServiceClient.prototype.getOrganization = function getOrganization(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(OrganizationService.GetOrganization, {
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

OrganizationServiceClient.prototype.listOrganizations = function listOrganizations(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(OrganizationService.ListOrganizations, {
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

OrganizationServiceClient.prototype.getCurrentOrganization = function getCurrentOrganization(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(OrganizationService.GetCurrentOrganization, {
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

exports.OrganizationServiceClient = OrganizationServiceClient;

var BusinessUnitGroupService = (function () {
  function BusinessUnitGroupService() {}
  BusinessUnitGroupService.serviceName = "auth.BusinessUnitGroupService";
  return BusinessUnitGroupService;
}());

BusinessUnitGroupService.CreateBusinessUnitGroup = {
  methodName: "CreateBusinessUnitGroup",
  service: BusinessUnitGroupService,
  requestStream: false,
  responseStream: false,
  requestType: auth_pb.CreateBusinessUnitGroupRequest,
  responseType: auth_pb.BusinessUnitGroupResponse
};

BusinessUnitGroupService.UpdateBusinessUnitGroup = {
  methodName: "UpdateBusinessUnitGroup",
  service: BusinessUnitGroupService,
  requestStream: false,
  responseStream: false,
  requestType: auth_pb.UpdateBusinessUnitGroupRequest,
  responseType: auth_pb.BusinessUnitGroupResponse
};

BusinessUnitGroupService.DeleteBusinessUnitGroup = {
  methodName: "DeleteBusinessUnitGroup",
  service: BusinessUnitGroupService,
  requestStream: false,
  responseStream: false,
  requestType: auth_pb.DeleteBusinessUnitGroupRequest,
  responseType: auth_pb.Empty
};

BusinessUnitGroupService.GetBusinessUnitGroup = {
  methodName: "GetBusinessUnitGroup",
  service: BusinessUnitGroupService,
  requestStream: false,
  responseStream: false,
  requestType: auth_pb.GetBusinessUnitGroupRequest,
  responseType: auth_pb.BusinessUnitGroupResponse
};

BusinessUnitGroupService.ListBusinessUnitGroups = {
  methodName: "ListBusinessUnitGroups",
  service: BusinessUnitGroupService,
  requestStream: false,
  responseStream: false,
  requestType: auth_pb.ListBusinessUnitGroupsRequest,
  responseType: auth_pb.ListBusinessUnitGroupsResponse
};

BusinessUnitGroupService.AddBusinessUnitGroupMember = {
  methodName: "AddBusinessUnitGroupMember",
  service: BusinessUnitGroupService,
  requestStream: false,
  responseStream: false,
  requestType: auth_pb.AddBusinessUnitGroupMemberRequest,
  responseType: auth_pb.Empty
};

BusinessUnitGroupService.RemoveBusinessUnitGroupMember = {
  methodName: "RemoveBusinessUnitGroupMember",
  service: BusinessUnitGroupService,
  requestStream: false,
  responseStream: false,
  requestType: auth_pb.RemoveBusinessUnitGroupMemberRequest,
  responseType: auth_pb.Empty
};

BusinessUnitGroupService.ListBusinessUnitGroupMembers = {
  methodName: "ListBusinessUnitGroupMembers",
  service: BusinessUnitGroupService,
  requestStream: false,
  responseStream: false,
  requestType: auth_pb.ListBusinessUnitGroupMembersRequest,
  responseType: auth_pb.ListBusinessUnitGroupMembersResponse
};

exports.BusinessUnitGroupService = BusinessUnitGroupService;

function BusinessUnitGroupServiceClient(serviceHost, options) {
  this.serviceHost = serviceHost;
  this.options = options || {};
}

BusinessUnitGroupServiceClient.prototype.createBusinessUnitGroup = function createBusinessUnitGroup(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(BusinessUnitGroupService.CreateBusinessUnitGroup, {
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

BusinessUnitGroupServiceClient.prototype.updateBusinessUnitGroup = function updateBusinessUnitGroup(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(BusinessUnitGroupService.UpdateBusinessUnitGroup, {
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

BusinessUnitGroupServiceClient.prototype.deleteBusinessUnitGroup = function deleteBusinessUnitGroup(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(BusinessUnitGroupService.DeleteBusinessUnitGroup, {
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

BusinessUnitGroupServiceClient.prototype.getBusinessUnitGroup = function getBusinessUnitGroup(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(BusinessUnitGroupService.GetBusinessUnitGroup, {
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

BusinessUnitGroupServiceClient.prototype.listBusinessUnitGroups = function listBusinessUnitGroups(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(BusinessUnitGroupService.ListBusinessUnitGroups, {
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

BusinessUnitGroupServiceClient.prototype.addBusinessUnitGroupMember = function addBusinessUnitGroupMember(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(BusinessUnitGroupService.AddBusinessUnitGroupMember, {
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

BusinessUnitGroupServiceClient.prototype.removeBusinessUnitGroupMember = function removeBusinessUnitGroupMember(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(BusinessUnitGroupService.RemoveBusinessUnitGroupMember, {
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

BusinessUnitGroupServiceClient.prototype.listBusinessUnitGroupMembers = function listBusinessUnitGroupMembers(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(BusinessUnitGroupService.ListBusinessUnitGroupMembers, {
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

exports.BusinessUnitGroupServiceClient = BusinessUnitGroupServiceClient;

var CredentialService = (function () {
  function CredentialService() {}
  CredentialService.serviceName = "auth.CredentialService";
  return CredentialService;
}());

CredentialService.CreateCredential = {
  methodName: "CreateCredential",
  service: CredentialService,
  requestStream: false,
  responseStream: false,
  requestType: auth_pb.CreateCredentialRequest,
  responseType: auth_pb.CredentialResponse
};

CredentialService.UpdateCredential = {
  methodName: "UpdateCredential",
  service: CredentialService,
  requestStream: false,
  responseStream: false,
  requestType: auth_pb.UpdateCredentialRequest,
  responseType: auth_pb.CredentialResponse
};

CredentialService.DeleteCredential = {
  methodName: "DeleteCredential",
  service: CredentialService,
  requestStream: false,
  responseStream: false,
  requestType: auth_pb.DeleteCredentialRequest,
  responseType: auth_pb.Empty
};

CredentialService.GetCredential = {
  methodName: "GetCredential",
  service: CredentialService,
  requestStream: false,
  responseStream: false,
  requestType: auth_pb.GetCredentialRequest,
  responseType: auth_pb.CredentialResponse
};

CredentialService.ListCredentials = {
  methodName: "ListCredentials",
  service: CredentialService,
  requestStream: false,
  responseStream: false,
  requestType: auth_pb.ListCredentialsRequest,
  responseType: auth_pb.ListCredentialsResponse
};

exports.CredentialService = CredentialService;

function CredentialServiceClient(serviceHost, options) {
  this.serviceHost = serviceHost;
  this.options = options || {};
}

CredentialServiceClient.prototype.createCredential = function createCredential(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(CredentialService.CreateCredential, {
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

CredentialServiceClient.prototype.updateCredential = function updateCredential(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(CredentialService.UpdateCredential, {
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

CredentialServiceClient.prototype.deleteCredential = function deleteCredential(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(CredentialService.DeleteCredential, {
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

CredentialServiceClient.prototype.getCredential = function getCredential(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(CredentialService.GetCredential, {
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

CredentialServiceClient.prototype.listCredentials = function listCredentials(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(CredentialService.ListCredentials, {
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

exports.CredentialServiceClient = CredentialServiceClient;

