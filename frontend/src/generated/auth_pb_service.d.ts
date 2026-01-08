// package: auth
// file: auth.proto

import * as auth_pb from "./auth_pb";
import {grpc} from "@improbable-eng/grpc-web";

type AuthenticationServiceLogin = {
  readonly methodName: string;
  readonly service: typeof AuthenticationService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof auth_pb.LoginRequest;
  readonly responseType: typeof auth_pb.TokenResponse;
};

type AuthenticationServiceRefreshToken = {
  readonly methodName: string;
  readonly service: typeof AuthenticationService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof auth_pb.RefreshTokenRequest;
  readonly responseType: typeof auth_pb.TokenResponse;
};

type AuthenticationServiceLogout = {
  readonly methodName: string;
  readonly service: typeof AuthenticationService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof auth_pb.LogoutRequest;
  readonly responseType: typeof auth_pb.Empty;
};

type AuthenticationServiceValidateToken = {
  readonly methodName: string;
  readonly service: typeof AuthenticationService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof auth_pb.ValidateTokenRequest;
  readonly responseType: typeof auth_pb.UserInfo;
};

type AuthenticationServiceRegister = {
  readonly methodName: string;
  readonly service: typeof AuthenticationService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof auth_pb.RegisterRequest;
  readonly responseType: typeof auth_pb.UserResponse;
};

export class AuthenticationService {
  static readonly serviceName: string;
  static readonly Login: AuthenticationServiceLogin;
  static readonly RefreshToken: AuthenticationServiceRefreshToken;
  static readonly Logout: AuthenticationServiceLogout;
  static readonly ValidateToken: AuthenticationServiceValidateToken;
  static readonly Register: AuthenticationServiceRegister;
}

type AuthorizationServiceCheckPermission = {
  readonly methodName: string;
  readonly service: typeof AuthorizationService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof auth_pb.PermissionCheckRequest;
  readonly responseType: typeof auth_pb.PermissionCheckResponse;
};

type AuthorizationServiceGetUserRoles = {
  readonly methodName: string;
  readonly service: typeof AuthorizationService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof auth_pb.GetUserRolesRequest;
  readonly responseType: typeof auth_pb.GetUserRolesResponse;
};

type AuthorizationServiceGetUserPermissions = {
  readonly methodName: string;
  readonly service: typeof AuthorizationService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof auth_pb.GetUserPermissionsRequest;
  readonly responseType: typeof auth_pb.GetUserPermissionsResponse;
};

type AuthorizationServiceIsPlatformAdmin = {
  readonly methodName: string;
  readonly service: typeof AuthorizationService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof auth_pb.IsPlatformAdminRequest;
  readonly responseType: typeof auth_pb.IsPlatformAdminResponse;
};

export class AuthorizationService {
  static readonly serviceName: string;
  static readonly CheckPermission: AuthorizationServiceCheckPermission;
  static readonly GetUserRoles: AuthorizationServiceGetUserRoles;
  static readonly GetUserPermissions: AuthorizationServiceGetUserPermissions;
  static readonly IsPlatformAdmin: AuthorizationServiceIsPlatformAdmin;
}

type UserServiceCreateUser = {
  readonly methodName: string;
  readonly service: typeof UserService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof auth_pb.CreateUserRequest;
  readonly responseType: typeof auth_pb.UserResponse;
};

type UserServiceUpdateUser = {
  readonly methodName: string;
  readonly service: typeof UserService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof auth_pb.UpdateUserRequest;
  readonly responseType: typeof auth_pb.UserResponse;
};

type UserServiceDeleteUser = {
  readonly methodName: string;
  readonly service: typeof UserService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof auth_pb.DeleteUserRequest;
  readonly responseType: typeof auth_pb.Empty;
};

type UserServiceGetUser = {
  readonly methodName: string;
  readonly service: typeof UserService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof auth_pb.GetUserRequest;
  readonly responseType: typeof auth_pb.UserResponse;
};

type UserServiceListUsers = {
  readonly methodName: string;
  readonly service: typeof UserService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof auth_pb.ListUsersRequest;
  readonly responseType: typeof auth_pb.ListUsersResponse;
};

type UserServiceGetCurrentUser = {
  readonly methodName: string;
  readonly service: typeof UserService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof auth_pb.GetCurrentUserRequest;
  readonly responseType: typeof auth_pb.UserResponse;
};

type UserServiceUpdateCurrentUser = {
  readonly methodName: string;
  readonly service: typeof UserService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof auth_pb.UpdateCurrentUserRequest;
  readonly responseType: typeof auth_pb.UserResponse;
};

type UserServiceChangePassword = {
  readonly methodName: string;
  readonly service: typeof UserService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof auth_pb.ChangePasswordRequest;
  readonly responseType: typeof auth_pb.Empty;
};

export class UserService {
  static readonly serviceName: string;
  static readonly CreateUser: UserServiceCreateUser;
  static readonly UpdateUser: UserServiceUpdateUser;
  static readonly DeleteUser: UserServiceDeleteUser;
  static readonly GetUser: UserServiceGetUser;
  static readonly ListUsers: UserServiceListUsers;
  static readonly GetCurrentUser: UserServiceGetCurrentUser;
  static readonly UpdateCurrentUser: UserServiceUpdateCurrentUser;
  static readonly ChangePassword: UserServiceChangePassword;
}

type RoleServiceCreateRole = {
  readonly methodName: string;
  readonly service: typeof RoleService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof auth_pb.CreateRoleRequest;
  readonly responseType: typeof auth_pb.RoleResponse;
};

type RoleServiceUpdateRole = {
  readonly methodName: string;
  readonly service: typeof RoleService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof auth_pb.UpdateRoleRequest;
  readonly responseType: typeof auth_pb.RoleResponse;
};

type RoleServiceDeleteRole = {
  readonly methodName: string;
  readonly service: typeof RoleService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof auth_pb.DeleteRoleRequest;
  readonly responseType: typeof auth_pb.Empty;
};

type RoleServiceGetRole = {
  readonly methodName: string;
  readonly service: typeof RoleService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof auth_pb.GetRoleRequest;
  readonly responseType: typeof auth_pb.RoleResponse;
};

type RoleServiceListRoles = {
  readonly methodName: string;
  readonly service: typeof RoleService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof auth_pb.ListRolesRequest;
  readonly responseType: typeof auth_pb.ListRolesResponse;
};

type RoleServiceAssignRole = {
  readonly methodName: string;
  readonly service: typeof RoleService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof auth_pb.AssignRoleRequest;
  readonly responseType: typeof auth_pb.Empty;
};

type RoleServiceRemoveRole = {
  readonly methodName: string;
  readonly service: typeof RoleService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof auth_pb.RemoveRoleRequest;
  readonly responseType: typeof auth_pb.Empty;
};

export class RoleService {
  static readonly serviceName: string;
  static readonly CreateRole: RoleServiceCreateRole;
  static readonly UpdateRole: RoleServiceUpdateRole;
  static readonly DeleteRole: RoleServiceDeleteRole;
  static readonly GetRole: RoleServiceGetRole;
  static readonly ListRoles: RoleServiceListRoles;
  static readonly AssignRole: RoleServiceAssignRole;
  static readonly RemoveRole: RoleServiceRemoveRole;
}

type GroupServiceCreateGroup = {
  readonly methodName: string;
  readonly service: typeof GroupService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof auth_pb.CreateGroupRequest;
  readonly responseType: typeof auth_pb.GroupResponse;
};

type GroupServiceUpdateGroup = {
  readonly methodName: string;
  readonly service: typeof GroupService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof auth_pb.UpdateGroupRequest;
  readonly responseType: typeof auth_pb.GroupResponse;
};

type GroupServiceDeleteGroup = {
  readonly methodName: string;
  readonly service: typeof GroupService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof auth_pb.DeleteGroupRequest;
  readonly responseType: typeof auth_pb.Empty;
};

type GroupServiceGetGroup = {
  readonly methodName: string;
  readonly service: typeof GroupService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof auth_pb.GetGroupRequest;
  readonly responseType: typeof auth_pb.GroupResponse;
};

type GroupServiceListGroups = {
  readonly methodName: string;
  readonly service: typeof GroupService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof auth_pb.ListGroupsRequest;
  readonly responseType: typeof auth_pb.ListGroupsResponse;
};

type GroupServiceAddGroupMember = {
  readonly methodName: string;
  readonly service: typeof GroupService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof auth_pb.AddGroupMemberRequest;
  readonly responseType: typeof auth_pb.Empty;
};

type GroupServiceRemoveGroupMember = {
  readonly methodName: string;
  readonly service: typeof GroupService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof auth_pb.RemoveGroupMemberRequest;
  readonly responseType: typeof auth_pb.Empty;
};

export class GroupService {
  static readonly serviceName: string;
  static readonly CreateGroup: GroupServiceCreateGroup;
  static readonly UpdateGroup: GroupServiceUpdateGroup;
  static readonly DeleteGroup: GroupServiceDeleteGroup;
  static readonly GetGroup: GroupServiceGetGroup;
  static readonly ListGroups: GroupServiceListGroups;
  static readonly AddGroupMember: GroupServiceAddGroupMember;
  static readonly RemoveGroupMember: GroupServiceRemoveGroupMember;
}

type BusinessUnitServiceCreateBusinessUnit = {
  readonly methodName: string;
  readonly service: typeof BusinessUnitService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof auth_pb.CreateBusinessUnitRequest;
  readonly responseType: typeof auth_pb.BusinessUnitResponse;
};

type BusinessUnitServiceUpdateBusinessUnit = {
  readonly methodName: string;
  readonly service: typeof BusinessUnitService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof auth_pb.UpdateBusinessUnitRequest;
  readonly responseType: typeof auth_pb.BusinessUnitResponse;
};

type BusinessUnitServiceDeleteBusinessUnit = {
  readonly methodName: string;
  readonly service: typeof BusinessUnitService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof auth_pb.DeleteBusinessUnitRequest;
  readonly responseType: typeof auth_pb.Empty;
};

type BusinessUnitServiceGetBusinessUnit = {
  readonly methodName: string;
  readonly service: typeof BusinessUnitService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof auth_pb.GetBusinessUnitRequest;
  readonly responseType: typeof auth_pb.BusinessUnitResponse;
};

type BusinessUnitServiceListBusinessUnits = {
  readonly methodName: string;
  readonly service: typeof BusinessUnitService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof auth_pb.ListBusinessUnitsRequest;
  readonly responseType: typeof auth_pb.ListBusinessUnitsResponse;
};

type BusinessUnitServiceAddBusinessUnitMember = {
  readonly methodName: string;
  readonly service: typeof BusinessUnitService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof auth_pb.AddBusinessUnitMemberRequest;
  readonly responseType: typeof auth_pb.Empty;
};

type BusinessUnitServiceRemoveBusinessUnitMember = {
  readonly methodName: string;
  readonly service: typeof BusinessUnitService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof auth_pb.RemoveBusinessUnitMemberRequest;
  readonly responseType: typeof auth_pb.Empty;
};

type BusinessUnitServiceListBusinessUnitMembers = {
  readonly methodName: string;
  readonly service: typeof BusinessUnitService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof auth_pb.ListBusinessUnitMembersRequest;
  readonly responseType: typeof auth_pb.ListBusinessUnitMembersResponse;
};

export class BusinessUnitService {
  static readonly serviceName: string;
  static readonly CreateBusinessUnit: BusinessUnitServiceCreateBusinessUnit;
  static readonly UpdateBusinessUnit: BusinessUnitServiceUpdateBusinessUnit;
  static readonly DeleteBusinessUnit: BusinessUnitServiceDeleteBusinessUnit;
  static readonly GetBusinessUnit: BusinessUnitServiceGetBusinessUnit;
  static readonly ListBusinessUnits: BusinessUnitServiceListBusinessUnits;
  static readonly AddBusinessUnitMember: BusinessUnitServiceAddBusinessUnitMember;
  static readonly RemoveBusinessUnitMember: BusinessUnitServiceRemoveBusinessUnitMember;
  static readonly ListBusinessUnitMembers: BusinessUnitServiceListBusinessUnitMembers;
}

type OrganizationServiceCreateOrganization = {
  readonly methodName: string;
  readonly service: typeof OrganizationService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof auth_pb.CreateOrganizationRequest;
  readonly responseType: typeof auth_pb.OrganizationResponse;
};

type OrganizationServiceUpdateOrganization = {
  readonly methodName: string;
  readonly service: typeof OrganizationService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof auth_pb.UpdateOrganizationRequest;
  readonly responseType: typeof auth_pb.OrganizationResponse;
};

type OrganizationServiceDeleteOrganization = {
  readonly methodName: string;
  readonly service: typeof OrganizationService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof auth_pb.DeleteOrganizationRequest;
  readonly responseType: typeof auth_pb.Empty;
};

type OrganizationServiceGetOrganization = {
  readonly methodName: string;
  readonly service: typeof OrganizationService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof auth_pb.GetOrganizationRequest;
  readonly responseType: typeof auth_pb.OrganizationResponse;
};

type OrganizationServiceListOrganizations = {
  readonly methodName: string;
  readonly service: typeof OrganizationService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof auth_pb.ListOrganizationsRequest;
  readonly responseType: typeof auth_pb.ListOrganizationsResponse;
};

type OrganizationServiceGetCurrentOrganization = {
  readonly methodName: string;
  readonly service: typeof OrganizationService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof auth_pb.GetCurrentOrganizationRequest;
  readonly responseType: typeof auth_pb.OrganizationResponse;
};

export class OrganizationService {
  static readonly serviceName: string;
  static readonly CreateOrganization: OrganizationServiceCreateOrganization;
  static readonly UpdateOrganization: OrganizationServiceUpdateOrganization;
  static readonly DeleteOrganization: OrganizationServiceDeleteOrganization;
  static readonly GetOrganization: OrganizationServiceGetOrganization;
  static readonly ListOrganizations: OrganizationServiceListOrganizations;
  static readonly GetCurrentOrganization: OrganizationServiceGetCurrentOrganization;
}

type BusinessUnitGroupServiceCreateBusinessUnitGroup = {
  readonly methodName: string;
  readonly service: typeof BusinessUnitGroupService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof auth_pb.CreateBusinessUnitGroupRequest;
  readonly responseType: typeof auth_pb.BusinessUnitGroupResponse;
};

type BusinessUnitGroupServiceUpdateBusinessUnitGroup = {
  readonly methodName: string;
  readonly service: typeof BusinessUnitGroupService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof auth_pb.UpdateBusinessUnitGroupRequest;
  readonly responseType: typeof auth_pb.BusinessUnitGroupResponse;
};

type BusinessUnitGroupServiceDeleteBusinessUnitGroup = {
  readonly methodName: string;
  readonly service: typeof BusinessUnitGroupService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof auth_pb.DeleteBusinessUnitGroupRequest;
  readonly responseType: typeof auth_pb.Empty;
};

type BusinessUnitGroupServiceGetBusinessUnitGroup = {
  readonly methodName: string;
  readonly service: typeof BusinessUnitGroupService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof auth_pb.GetBusinessUnitGroupRequest;
  readonly responseType: typeof auth_pb.BusinessUnitGroupResponse;
};

type BusinessUnitGroupServiceListBusinessUnitGroups = {
  readonly methodName: string;
  readonly service: typeof BusinessUnitGroupService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof auth_pb.ListBusinessUnitGroupsRequest;
  readonly responseType: typeof auth_pb.ListBusinessUnitGroupsResponse;
};

type BusinessUnitGroupServiceAddBusinessUnitGroupMember = {
  readonly methodName: string;
  readonly service: typeof BusinessUnitGroupService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof auth_pb.AddBusinessUnitGroupMemberRequest;
  readonly responseType: typeof auth_pb.Empty;
};

type BusinessUnitGroupServiceRemoveBusinessUnitGroupMember = {
  readonly methodName: string;
  readonly service: typeof BusinessUnitGroupService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof auth_pb.RemoveBusinessUnitGroupMemberRequest;
  readonly responseType: typeof auth_pb.Empty;
};

type BusinessUnitGroupServiceListBusinessUnitGroupMembers = {
  readonly methodName: string;
  readonly service: typeof BusinessUnitGroupService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof auth_pb.ListBusinessUnitGroupMembersRequest;
  readonly responseType: typeof auth_pb.ListBusinessUnitGroupMembersResponse;
};

export class BusinessUnitGroupService {
  static readonly serviceName: string;
  static readonly CreateBusinessUnitGroup: BusinessUnitGroupServiceCreateBusinessUnitGroup;
  static readonly UpdateBusinessUnitGroup: BusinessUnitGroupServiceUpdateBusinessUnitGroup;
  static readonly DeleteBusinessUnitGroup: BusinessUnitGroupServiceDeleteBusinessUnitGroup;
  static readonly GetBusinessUnitGroup: BusinessUnitGroupServiceGetBusinessUnitGroup;
  static readonly ListBusinessUnitGroups: BusinessUnitGroupServiceListBusinessUnitGroups;
  static readonly AddBusinessUnitGroupMember: BusinessUnitGroupServiceAddBusinessUnitGroupMember;
  static readonly RemoveBusinessUnitGroupMember: BusinessUnitGroupServiceRemoveBusinessUnitGroupMember;
  static readonly ListBusinessUnitGroupMembers: BusinessUnitGroupServiceListBusinessUnitGroupMembers;
}

type CredentialServiceCreateCredential = {
  readonly methodName: string;
  readonly service: typeof CredentialService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof auth_pb.CreateCredentialRequest;
  readonly responseType: typeof auth_pb.CredentialResponse;
};

type CredentialServiceUpdateCredential = {
  readonly methodName: string;
  readonly service: typeof CredentialService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof auth_pb.UpdateCredentialRequest;
  readonly responseType: typeof auth_pb.CredentialResponse;
};

type CredentialServiceDeleteCredential = {
  readonly methodName: string;
  readonly service: typeof CredentialService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof auth_pb.DeleteCredentialRequest;
  readonly responseType: typeof auth_pb.Empty;
};

type CredentialServiceGetCredential = {
  readonly methodName: string;
  readonly service: typeof CredentialService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof auth_pb.GetCredentialRequest;
  readonly responseType: typeof auth_pb.CredentialResponse;
};

type CredentialServiceListCredentials = {
  readonly methodName: string;
  readonly service: typeof CredentialService;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof auth_pb.ListCredentialsRequest;
  readonly responseType: typeof auth_pb.ListCredentialsResponse;
};

export class CredentialService {
  static readonly serviceName: string;
  static readonly CreateCredential: CredentialServiceCreateCredential;
  static readonly UpdateCredential: CredentialServiceUpdateCredential;
  static readonly DeleteCredential: CredentialServiceDeleteCredential;
  static readonly GetCredential: CredentialServiceGetCredential;
  static readonly ListCredentials: CredentialServiceListCredentials;
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

export class AuthenticationServiceClient {
  readonly serviceHost: string;

  constructor(serviceHost: string, options?: grpc.RpcOptions);
  login(
    requestMessage: auth_pb.LoginRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: auth_pb.TokenResponse|null) => void
  ): UnaryResponse;
  login(
    requestMessage: auth_pb.LoginRequest,
    callback: (error: ServiceError|null, responseMessage: auth_pb.TokenResponse|null) => void
  ): UnaryResponse;
  refreshToken(
    requestMessage: auth_pb.RefreshTokenRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: auth_pb.TokenResponse|null) => void
  ): UnaryResponse;
  refreshToken(
    requestMessage: auth_pb.RefreshTokenRequest,
    callback: (error: ServiceError|null, responseMessage: auth_pb.TokenResponse|null) => void
  ): UnaryResponse;
  logout(
    requestMessage: auth_pb.LogoutRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: auth_pb.Empty|null) => void
  ): UnaryResponse;
  logout(
    requestMessage: auth_pb.LogoutRequest,
    callback: (error: ServiceError|null, responseMessage: auth_pb.Empty|null) => void
  ): UnaryResponse;
  validateToken(
    requestMessage: auth_pb.ValidateTokenRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: auth_pb.UserInfo|null) => void
  ): UnaryResponse;
  validateToken(
    requestMessage: auth_pb.ValidateTokenRequest,
    callback: (error: ServiceError|null, responseMessage: auth_pb.UserInfo|null) => void
  ): UnaryResponse;
  register(
    requestMessage: auth_pb.RegisterRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: auth_pb.UserResponse|null) => void
  ): UnaryResponse;
  register(
    requestMessage: auth_pb.RegisterRequest,
    callback: (error: ServiceError|null, responseMessage: auth_pb.UserResponse|null) => void
  ): UnaryResponse;
}

export class AuthorizationServiceClient {
  readonly serviceHost: string;

  constructor(serviceHost: string, options?: grpc.RpcOptions);
  checkPermission(
    requestMessage: auth_pb.PermissionCheckRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: auth_pb.PermissionCheckResponse|null) => void
  ): UnaryResponse;
  checkPermission(
    requestMessage: auth_pb.PermissionCheckRequest,
    callback: (error: ServiceError|null, responseMessage: auth_pb.PermissionCheckResponse|null) => void
  ): UnaryResponse;
  getUserRoles(
    requestMessage: auth_pb.GetUserRolesRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: auth_pb.GetUserRolesResponse|null) => void
  ): UnaryResponse;
  getUserRoles(
    requestMessage: auth_pb.GetUserRolesRequest,
    callback: (error: ServiceError|null, responseMessage: auth_pb.GetUserRolesResponse|null) => void
  ): UnaryResponse;
  getUserPermissions(
    requestMessage: auth_pb.GetUserPermissionsRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: auth_pb.GetUserPermissionsResponse|null) => void
  ): UnaryResponse;
  getUserPermissions(
    requestMessage: auth_pb.GetUserPermissionsRequest,
    callback: (error: ServiceError|null, responseMessage: auth_pb.GetUserPermissionsResponse|null) => void
  ): UnaryResponse;
  isPlatformAdmin(
    requestMessage: auth_pb.IsPlatformAdminRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: auth_pb.IsPlatformAdminResponse|null) => void
  ): UnaryResponse;
  isPlatformAdmin(
    requestMessage: auth_pb.IsPlatformAdminRequest,
    callback: (error: ServiceError|null, responseMessage: auth_pb.IsPlatformAdminResponse|null) => void
  ): UnaryResponse;
}

export class UserServiceClient {
  readonly serviceHost: string;

  constructor(serviceHost: string, options?: grpc.RpcOptions);
  createUser(
    requestMessage: auth_pb.CreateUserRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: auth_pb.UserResponse|null) => void
  ): UnaryResponse;
  createUser(
    requestMessage: auth_pb.CreateUserRequest,
    callback: (error: ServiceError|null, responseMessage: auth_pb.UserResponse|null) => void
  ): UnaryResponse;
  updateUser(
    requestMessage: auth_pb.UpdateUserRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: auth_pb.UserResponse|null) => void
  ): UnaryResponse;
  updateUser(
    requestMessage: auth_pb.UpdateUserRequest,
    callback: (error: ServiceError|null, responseMessage: auth_pb.UserResponse|null) => void
  ): UnaryResponse;
  deleteUser(
    requestMessage: auth_pb.DeleteUserRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: auth_pb.Empty|null) => void
  ): UnaryResponse;
  deleteUser(
    requestMessage: auth_pb.DeleteUserRequest,
    callback: (error: ServiceError|null, responseMessage: auth_pb.Empty|null) => void
  ): UnaryResponse;
  getUser(
    requestMessage: auth_pb.GetUserRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: auth_pb.UserResponse|null) => void
  ): UnaryResponse;
  getUser(
    requestMessage: auth_pb.GetUserRequest,
    callback: (error: ServiceError|null, responseMessage: auth_pb.UserResponse|null) => void
  ): UnaryResponse;
  listUsers(
    requestMessage: auth_pb.ListUsersRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: auth_pb.ListUsersResponse|null) => void
  ): UnaryResponse;
  listUsers(
    requestMessage: auth_pb.ListUsersRequest,
    callback: (error: ServiceError|null, responseMessage: auth_pb.ListUsersResponse|null) => void
  ): UnaryResponse;
  getCurrentUser(
    requestMessage: auth_pb.GetCurrentUserRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: auth_pb.UserResponse|null) => void
  ): UnaryResponse;
  getCurrentUser(
    requestMessage: auth_pb.GetCurrentUserRequest,
    callback: (error: ServiceError|null, responseMessage: auth_pb.UserResponse|null) => void
  ): UnaryResponse;
  updateCurrentUser(
    requestMessage: auth_pb.UpdateCurrentUserRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: auth_pb.UserResponse|null) => void
  ): UnaryResponse;
  updateCurrentUser(
    requestMessage: auth_pb.UpdateCurrentUserRequest,
    callback: (error: ServiceError|null, responseMessage: auth_pb.UserResponse|null) => void
  ): UnaryResponse;
  changePassword(
    requestMessage: auth_pb.ChangePasswordRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: auth_pb.Empty|null) => void
  ): UnaryResponse;
  changePassword(
    requestMessage: auth_pb.ChangePasswordRequest,
    callback: (error: ServiceError|null, responseMessage: auth_pb.Empty|null) => void
  ): UnaryResponse;
}

export class RoleServiceClient {
  readonly serviceHost: string;

  constructor(serviceHost: string, options?: grpc.RpcOptions);
  createRole(
    requestMessage: auth_pb.CreateRoleRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: auth_pb.RoleResponse|null) => void
  ): UnaryResponse;
  createRole(
    requestMessage: auth_pb.CreateRoleRequest,
    callback: (error: ServiceError|null, responseMessage: auth_pb.RoleResponse|null) => void
  ): UnaryResponse;
  updateRole(
    requestMessage: auth_pb.UpdateRoleRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: auth_pb.RoleResponse|null) => void
  ): UnaryResponse;
  updateRole(
    requestMessage: auth_pb.UpdateRoleRequest,
    callback: (error: ServiceError|null, responseMessage: auth_pb.RoleResponse|null) => void
  ): UnaryResponse;
  deleteRole(
    requestMessage: auth_pb.DeleteRoleRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: auth_pb.Empty|null) => void
  ): UnaryResponse;
  deleteRole(
    requestMessage: auth_pb.DeleteRoleRequest,
    callback: (error: ServiceError|null, responseMessage: auth_pb.Empty|null) => void
  ): UnaryResponse;
  getRole(
    requestMessage: auth_pb.GetRoleRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: auth_pb.RoleResponse|null) => void
  ): UnaryResponse;
  getRole(
    requestMessage: auth_pb.GetRoleRequest,
    callback: (error: ServiceError|null, responseMessage: auth_pb.RoleResponse|null) => void
  ): UnaryResponse;
  listRoles(
    requestMessage: auth_pb.ListRolesRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: auth_pb.ListRolesResponse|null) => void
  ): UnaryResponse;
  listRoles(
    requestMessage: auth_pb.ListRolesRequest,
    callback: (error: ServiceError|null, responseMessage: auth_pb.ListRolesResponse|null) => void
  ): UnaryResponse;
  assignRole(
    requestMessage: auth_pb.AssignRoleRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: auth_pb.Empty|null) => void
  ): UnaryResponse;
  assignRole(
    requestMessage: auth_pb.AssignRoleRequest,
    callback: (error: ServiceError|null, responseMessage: auth_pb.Empty|null) => void
  ): UnaryResponse;
  removeRole(
    requestMessage: auth_pb.RemoveRoleRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: auth_pb.Empty|null) => void
  ): UnaryResponse;
  removeRole(
    requestMessage: auth_pb.RemoveRoleRequest,
    callback: (error: ServiceError|null, responseMessage: auth_pb.Empty|null) => void
  ): UnaryResponse;
}

export class GroupServiceClient {
  readonly serviceHost: string;

  constructor(serviceHost: string, options?: grpc.RpcOptions);
  createGroup(
    requestMessage: auth_pb.CreateGroupRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: auth_pb.GroupResponse|null) => void
  ): UnaryResponse;
  createGroup(
    requestMessage: auth_pb.CreateGroupRequest,
    callback: (error: ServiceError|null, responseMessage: auth_pb.GroupResponse|null) => void
  ): UnaryResponse;
  updateGroup(
    requestMessage: auth_pb.UpdateGroupRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: auth_pb.GroupResponse|null) => void
  ): UnaryResponse;
  updateGroup(
    requestMessage: auth_pb.UpdateGroupRequest,
    callback: (error: ServiceError|null, responseMessage: auth_pb.GroupResponse|null) => void
  ): UnaryResponse;
  deleteGroup(
    requestMessage: auth_pb.DeleteGroupRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: auth_pb.Empty|null) => void
  ): UnaryResponse;
  deleteGroup(
    requestMessage: auth_pb.DeleteGroupRequest,
    callback: (error: ServiceError|null, responseMessage: auth_pb.Empty|null) => void
  ): UnaryResponse;
  getGroup(
    requestMessage: auth_pb.GetGroupRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: auth_pb.GroupResponse|null) => void
  ): UnaryResponse;
  getGroup(
    requestMessage: auth_pb.GetGroupRequest,
    callback: (error: ServiceError|null, responseMessage: auth_pb.GroupResponse|null) => void
  ): UnaryResponse;
  listGroups(
    requestMessage: auth_pb.ListGroupsRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: auth_pb.ListGroupsResponse|null) => void
  ): UnaryResponse;
  listGroups(
    requestMessage: auth_pb.ListGroupsRequest,
    callback: (error: ServiceError|null, responseMessage: auth_pb.ListGroupsResponse|null) => void
  ): UnaryResponse;
  addGroupMember(
    requestMessage: auth_pb.AddGroupMemberRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: auth_pb.Empty|null) => void
  ): UnaryResponse;
  addGroupMember(
    requestMessage: auth_pb.AddGroupMemberRequest,
    callback: (error: ServiceError|null, responseMessage: auth_pb.Empty|null) => void
  ): UnaryResponse;
  removeGroupMember(
    requestMessage: auth_pb.RemoveGroupMemberRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: auth_pb.Empty|null) => void
  ): UnaryResponse;
  removeGroupMember(
    requestMessage: auth_pb.RemoveGroupMemberRequest,
    callback: (error: ServiceError|null, responseMessage: auth_pb.Empty|null) => void
  ): UnaryResponse;
}

export class BusinessUnitServiceClient {
  readonly serviceHost: string;

  constructor(serviceHost: string, options?: grpc.RpcOptions);
  createBusinessUnit(
    requestMessage: auth_pb.CreateBusinessUnitRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: auth_pb.BusinessUnitResponse|null) => void
  ): UnaryResponse;
  createBusinessUnit(
    requestMessage: auth_pb.CreateBusinessUnitRequest,
    callback: (error: ServiceError|null, responseMessage: auth_pb.BusinessUnitResponse|null) => void
  ): UnaryResponse;
  updateBusinessUnit(
    requestMessage: auth_pb.UpdateBusinessUnitRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: auth_pb.BusinessUnitResponse|null) => void
  ): UnaryResponse;
  updateBusinessUnit(
    requestMessage: auth_pb.UpdateBusinessUnitRequest,
    callback: (error: ServiceError|null, responseMessage: auth_pb.BusinessUnitResponse|null) => void
  ): UnaryResponse;
  deleteBusinessUnit(
    requestMessage: auth_pb.DeleteBusinessUnitRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: auth_pb.Empty|null) => void
  ): UnaryResponse;
  deleteBusinessUnit(
    requestMessage: auth_pb.DeleteBusinessUnitRequest,
    callback: (error: ServiceError|null, responseMessage: auth_pb.Empty|null) => void
  ): UnaryResponse;
  getBusinessUnit(
    requestMessage: auth_pb.GetBusinessUnitRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: auth_pb.BusinessUnitResponse|null) => void
  ): UnaryResponse;
  getBusinessUnit(
    requestMessage: auth_pb.GetBusinessUnitRequest,
    callback: (error: ServiceError|null, responseMessage: auth_pb.BusinessUnitResponse|null) => void
  ): UnaryResponse;
  listBusinessUnits(
    requestMessage: auth_pb.ListBusinessUnitsRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: auth_pb.ListBusinessUnitsResponse|null) => void
  ): UnaryResponse;
  listBusinessUnits(
    requestMessage: auth_pb.ListBusinessUnitsRequest,
    callback: (error: ServiceError|null, responseMessage: auth_pb.ListBusinessUnitsResponse|null) => void
  ): UnaryResponse;
  addBusinessUnitMember(
    requestMessage: auth_pb.AddBusinessUnitMemberRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: auth_pb.Empty|null) => void
  ): UnaryResponse;
  addBusinessUnitMember(
    requestMessage: auth_pb.AddBusinessUnitMemberRequest,
    callback: (error: ServiceError|null, responseMessage: auth_pb.Empty|null) => void
  ): UnaryResponse;
  removeBusinessUnitMember(
    requestMessage: auth_pb.RemoveBusinessUnitMemberRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: auth_pb.Empty|null) => void
  ): UnaryResponse;
  removeBusinessUnitMember(
    requestMessage: auth_pb.RemoveBusinessUnitMemberRequest,
    callback: (error: ServiceError|null, responseMessage: auth_pb.Empty|null) => void
  ): UnaryResponse;
  listBusinessUnitMembers(
    requestMessage: auth_pb.ListBusinessUnitMembersRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: auth_pb.ListBusinessUnitMembersResponse|null) => void
  ): UnaryResponse;
  listBusinessUnitMembers(
    requestMessage: auth_pb.ListBusinessUnitMembersRequest,
    callback: (error: ServiceError|null, responseMessage: auth_pb.ListBusinessUnitMembersResponse|null) => void
  ): UnaryResponse;
}

export class OrganizationServiceClient {
  readonly serviceHost: string;

  constructor(serviceHost: string, options?: grpc.RpcOptions);
  createOrganization(
    requestMessage: auth_pb.CreateOrganizationRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: auth_pb.OrganizationResponse|null) => void
  ): UnaryResponse;
  createOrganization(
    requestMessage: auth_pb.CreateOrganizationRequest,
    callback: (error: ServiceError|null, responseMessage: auth_pb.OrganizationResponse|null) => void
  ): UnaryResponse;
  updateOrganization(
    requestMessage: auth_pb.UpdateOrganizationRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: auth_pb.OrganizationResponse|null) => void
  ): UnaryResponse;
  updateOrganization(
    requestMessage: auth_pb.UpdateOrganizationRequest,
    callback: (error: ServiceError|null, responseMessage: auth_pb.OrganizationResponse|null) => void
  ): UnaryResponse;
  deleteOrganization(
    requestMessage: auth_pb.DeleteOrganizationRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: auth_pb.Empty|null) => void
  ): UnaryResponse;
  deleteOrganization(
    requestMessage: auth_pb.DeleteOrganizationRequest,
    callback: (error: ServiceError|null, responseMessage: auth_pb.Empty|null) => void
  ): UnaryResponse;
  getOrganization(
    requestMessage: auth_pb.GetOrganizationRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: auth_pb.OrganizationResponse|null) => void
  ): UnaryResponse;
  getOrganization(
    requestMessage: auth_pb.GetOrganizationRequest,
    callback: (error: ServiceError|null, responseMessage: auth_pb.OrganizationResponse|null) => void
  ): UnaryResponse;
  listOrganizations(
    requestMessage: auth_pb.ListOrganizationsRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: auth_pb.ListOrganizationsResponse|null) => void
  ): UnaryResponse;
  listOrganizations(
    requestMessage: auth_pb.ListOrganizationsRequest,
    callback: (error: ServiceError|null, responseMessage: auth_pb.ListOrganizationsResponse|null) => void
  ): UnaryResponse;
  getCurrentOrganization(
    requestMessage: auth_pb.GetCurrentOrganizationRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: auth_pb.OrganizationResponse|null) => void
  ): UnaryResponse;
  getCurrentOrganization(
    requestMessage: auth_pb.GetCurrentOrganizationRequest,
    callback: (error: ServiceError|null, responseMessage: auth_pb.OrganizationResponse|null) => void
  ): UnaryResponse;
}

export class BusinessUnitGroupServiceClient {
  readonly serviceHost: string;

  constructor(serviceHost: string, options?: grpc.RpcOptions);
  createBusinessUnitGroup(
    requestMessage: auth_pb.CreateBusinessUnitGroupRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: auth_pb.BusinessUnitGroupResponse|null) => void
  ): UnaryResponse;
  createBusinessUnitGroup(
    requestMessage: auth_pb.CreateBusinessUnitGroupRequest,
    callback: (error: ServiceError|null, responseMessage: auth_pb.BusinessUnitGroupResponse|null) => void
  ): UnaryResponse;
  updateBusinessUnitGroup(
    requestMessage: auth_pb.UpdateBusinessUnitGroupRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: auth_pb.BusinessUnitGroupResponse|null) => void
  ): UnaryResponse;
  updateBusinessUnitGroup(
    requestMessage: auth_pb.UpdateBusinessUnitGroupRequest,
    callback: (error: ServiceError|null, responseMessage: auth_pb.BusinessUnitGroupResponse|null) => void
  ): UnaryResponse;
  deleteBusinessUnitGroup(
    requestMessage: auth_pb.DeleteBusinessUnitGroupRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: auth_pb.Empty|null) => void
  ): UnaryResponse;
  deleteBusinessUnitGroup(
    requestMessage: auth_pb.DeleteBusinessUnitGroupRequest,
    callback: (error: ServiceError|null, responseMessage: auth_pb.Empty|null) => void
  ): UnaryResponse;
  getBusinessUnitGroup(
    requestMessage: auth_pb.GetBusinessUnitGroupRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: auth_pb.BusinessUnitGroupResponse|null) => void
  ): UnaryResponse;
  getBusinessUnitGroup(
    requestMessage: auth_pb.GetBusinessUnitGroupRequest,
    callback: (error: ServiceError|null, responseMessage: auth_pb.BusinessUnitGroupResponse|null) => void
  ): UnaryResponse;
  listBusinessUnitGroups(
    requestMessage: auth_pb.ListBusinessUnitGroupsRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: auth_pb.ListBusinessUnitGroupsResponse|null) => void
  ): UnaryResponse;
  listBusinessUnitGroups(
    requestMessage: auth_pb.ListBusinessUnitGroupsRequest,
    callback: (error: ServiceError|null, responseMessage: auth_pb.ListBusinessUnitGroupsResponse|null) => void
  ): UnaryResponse;
  addBusinessUnitGroupMember(
    requestMessage: auth_pb.AddBusinessUnitGroupMemberRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: auth_pb.Empty|null) => void
  ): UnaryResponse;
  addBusinessUnitGroupMember(
    requestMessage: auth_pb.AddBusinessUnitGroupMemberRequest,
    callback: (error: ServiceError|null, responseMessage: auth_pb.Empty|null) => void
  ): UnaryResponse;
  removeBusinessUnitGroupMember(
    requestMessage: auth_pb.RemoveBusinessUnitGroupMemberRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: auth_pb.Empty|null) => void
  ): UnaryResponse;
  removeBusinessUnitGroupMember(
    requestMessage: auth_pb.RemoveBusinessUnitGroupMemberRequest,
    callback: (error: ServiceError|null, responseMessage: auth_pb.Empty|null) => void
  ): UnaryResponse;
  listBusinessUnitGroupMembers(
    requestMessage: auth_pb.ListBusinessUnitGroupMembersRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: auth_pb.ListBusinessUnitGroupMembersResponse|null) => void
  ): UnaryResponse;
  listBusinessUnitGroupMembers(
    requestMessage: auth_pb.ListBusinessUnitGroupMembersRequest,
    callback: (error: ServiceError|null, responseMessage: auth_pb.ListBusinessUnitGroupMembersResponse|null) => void
  ): UnaryResponse;
}

export class CredentialServiceClient {
  readonly serviceHost: string;

  constructor(serviceHost: string, options?: grpc.RpcOptions);
  createCredential(
    requestMessage: auth_pb.CreateCredentialRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: auth_pb.CredentialResponse|null) => void
  ): UnaryResponse;
  createCredential(
    requestMessage: auth_pb.CreateCredentialRequest,
    callback: (error: ServiceError|null, responseMessage: auth_pb.CredentialResponse|null) => void
  ): UnaryResponse;
  updateCredential(
    requestMessage: auth_pb.UpdateCredentialRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: auth_pb.CredentialResponse|null) => void
  ): UnaryResponse;
  updateCredential(
    requestMessage: auth_pb.UpdateCredentialRequest,
    callback: (error: ServiceError|null, responseMessage: auth_pb.CredentialResponse|null) => void
  ): UnaryResponse;
  deleteCredential(
    requestMessage: auth_pb.DeleteCredentialRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: auth_pb.Empty|null) => void
  ): UnaryResponse;
  deleteCredential(
    requestMessage: auth_pb.DeleteCredentialRequest,
    callback: (error: ServiceError|null, responseMessage: auth_pb.Empty|null) => void
  ): UnaryResponse;
  getCredential(
    requestMessage: auth_pb.GetCredentialRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: auth_pb.CredentialResponse|null) => void
  ): UnaryResponse;
  getCredential(
    requestMessage: auth_pb.GetCredentialRequest,
    callback: (error: ServiceError|null, responseMessage: auth_pb.CredentialResponse|null) => void
  ): UnaryResponse;
  listCredentials(
    requestMessage: auth_pb.ListCredentialsRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: auth_pb.ListCredentialsResponse|null) => void
  ): UnaryResponse;
  listCredentials(
    requestMessage: auth_pb.ListCredentialsRequest,
    callback: (error: ServiceError|null, responseMessage: auth_pb.ListCredentialsResponse|null) => void
  ): UnaryResponse;
}

