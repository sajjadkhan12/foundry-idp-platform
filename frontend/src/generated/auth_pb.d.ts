// package: auth
// file: auth.proto

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

export class Error extends jspb.Message {
  getMessage(): string;
  setMessage(value: string): void;

  getCode(): number;
  setCode(value: number): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): Error.AsObject;
  static toObject(includeInstance: boolean, msg: Error): Error.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: Error, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): Error;
  static deserializeBinaryFromReader(message: Error, reader: jspb.BinaryReader): Error;
}

export namespace Error {
  export type AsObject = {
    message: string,
    code: number,
  }
}

export class LoginRequest extends jspb.Message {
  getIdentifier(): string;
  setIdentifier(value: string): void;

  getPassword(): string;
  setPassword(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): LoginRequest.AsObject;
  static toObject(includeInstance: boolean, msg: LoginRequest): LoginRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: LoginRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): LoginRequest;
  static deserializeBinaryFromReader(message: LoginRequest, reader: jspb.BinaryReader): LoginRequest;
}

export namespace LoginRequest {
  export type AsObject = {
    identifier: string,
    password: string,
  }
}

export class RefreshTokenRequest extends jspb.Message {
  getRefreshToken(): string;
  setRefreshToken(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): RefreshTokenRequest.AsObject;
  static toObject(includeInstance: boolean, msg: RefreshTokenRequest): RefreshTokenRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: RefreshTokenRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): RefreshTokenRequest;
  static deserializeBinaryFromReader(message: RefreshTokenRequest, reader: jspb.BinaryReader): RefreshTokenRequest;
}

export namespace RefreshTokenRequest {
  export type AsObject = {
    refreshToken: string,
  }
}

export class LogoutRequest extends jspb.Message {
  getRefreshToken(): string;
  setRefreshToken(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): LogoutRequest.AsObject;
  static toObject(includeInstance: boolean, msg: LogoutRequest): LogoutRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: LogoutRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): LogoutRequest;
  static deserializeBinaryFromReader(message: LogoutRequest, reader: jspb.BinaryReader): LogoutRequest;
}

export namespace LogoutRequest {
  export type AsObject = {
    refreshToken: string,
  }
}

export class ValidateTokenRequest extends jspb.Message {
  getToken(): string;
  setToken(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): ValidateTokenRequest.AsObject;
  static toObject(includeInstance: boolean, msg: ValidateTokenRequest): ValidateTokenRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: ValidateTokenRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): ValidateTokenRequest;
  static deserializeBinaryFromReader(message: ValidateTokenRequest, reader: jspb.BinaryReader): ValidateTokenRequest;
}

export namespace ValidateTokenRequest {
  export type AsObject = {
    token: string,
  }
}

export class RegisterRequest extends jspb.Message {
  getEmail(): string;
  setEmail(value: string): void;

  getUsername(): string;
  setUsername(value: string): void;

  getPassword(): string;
  setPassword(value: string): void;

  getFullName(): string;
  setFullName(value: string): void;

  getOrganizationSlug(): string;
  setOrganizationSlug(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): RegisterRequest.AsObject;
  static toObject(includeInstance: boolean, msg: RegisterRequest): RegisterRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: RegisterRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): RegisterRequest;
  static deserializeBinaryFromReader(message: RegisterRequest, reader: jspb.BinaryReader): RegisterRequest;
}

export namespace RegisterRequest {
  export type AsObject = {
    email: string,
    username: string,
    password: string,
    fullName: string,
    organizationSlug: string,
  }
}

export class TokenResponse extends jspb.Message {
  getAccessToken(): string;
  setAccessToken(value: string): void;

  getTokenType(): string;
  setTokenType(value: string): void;

  hasUser(): boolean;
  clearUser(): void;
  getUser(): UserResponse | undefined;
  setUser(value?: UserResponse): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): TokenResponse.AsObject;
  static toObject(includeInstance: boolean, msg: TokenResponse): TokenResponse.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: TokenResponse, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): TokenResponse;
  static deserializeBinaryFromReader(message: TokenResponse, reader: jspb.BinaryReader): TokenResponse;
}

export namespace TokenResponse {
  export type AsObject = {
    accessToken: string,
    tokenType: string,
    user?: UserResponse.AsObject,
  }
}

export class UserInfo extends jspb.Message {
  getUserId(): string;
  setUserId(value: string): void;

  getEmail(): string;
  setEmail(value: string): void;

  getUsername(): string;
  setUsername(value: string): void;

  getOrganizationId(): string;
  setOrganizationId(value: string): void;

  getIsActive(): boolean;
  setIsActive(value: boolean): void;

  clearRolesList(): void;
  getRolesList(): Array<string>;
  setRolesList(value: Array<string>): void;
  addRoles(value: string, index?: number): string;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): UserInfo.AsObject;
  static toObject(includeInstance: boolean, msg: UserInfo): UserInfo.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: UserInfo, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): UserInfo;
  static deserializeBinaryFromReader(message: UserInfo, reader: jspb.BinaryReader): UserInfo;
}

export namespace UserInfo {
  export type AsObject = {
    userId: string,
    email: string,
    username: string,
    organizationId: string,
    isActive: boolean,
    rolesList: Array<string>,
  }
}

export class PermissionCheckRequest extends jspb.Message {
  getUserId(): string;
  setUserId(value: string): void;

  getPermissionSlug(): string;
  setPermissionSlug(value: string): void;

  getBusinessUnitId(): string;
  setBusinessUnitId(value: string): void;

  getOrganizationId(): string;
  setOrganizationId(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): PermissionCheckRequest.AsObject;
  static toObject(includeInstance: boolean, msg: PermissionCheckRequest): PermissionCheckRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: PermissionCheckRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): PermissionCheckRequest;
  static deserializeBinaryFromReader(message: PermissionCheckRequest, reader: jspb.BinaryReader): PermissionCheckRequest;
}

export namespace PermissionCheckRequest {
  export type AsObject = {
    userId: string,
    permissionSlug: string,
    businessUnitId: string,
    organizationId: string,
  }
}

export class PermissionCheckResponse extends jspb.Message {
  getAllowed(): boolean;
  setAllowed(value: boolean): void;

  getMessage(): string;
  setMessage(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): PermissionCheckResponse.AsObject;
  static toObject(includeInstance: boolean, msg: PermissionCheckResponse): PermissionCheckResponse.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: PermissionCheckResponse, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): PermissionCheckResponse;
  static deserializeBinaryFromReader(message: PermissionCheckResponse, reader: jspb.BinaryReader): PermissionCheckResponse;
}

export namespace PermissionCheckResponse {
  export type AsObject = {
    allowed: boolean,
    message: string,
  }
}

export class GetUserRolesRequest extends jspb.Message {
  getUserId(): string;
  setUserId(value: string): void;

  getOrganizationId(): string;
  setOrganizationId(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): GetUserRolesRequest.AsObject;
  static toObject(includeInstance: boolean, msg: GetUserRolesRequest): GetUserRolesRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: GetUserRolesRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): GetUserRolesRequest;
  static deserializeBinaryFromReader(message: GetUserRolesRequest, reader: jspb.BinaryReader): GetUserRolesRequest;
}

export namespace GetUserRolesRequest {
  export type AsObject = {
    userId: string,
    organizationId: string,
  }
}

export class GetUserRolesResponse extends jspb.Message {
  clearRolesList(): void;
  getRolesList(): Array<string>;
  setRolesList(value: Array<string>): void;
  addRoles(value: string, index?: number): string;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): GetUserRolesResponse.AsObject;
  static toObject(includeInstance: boolean, msg: GetUserRolesResponse): GetUserRolesResponse.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: GetUserRolesResponse, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): GetUserRolesResponse;
  static deserializeBinaryFromReader(message: GetUserRolesResponse, reader: jspb.BinaryReader): GetUserRolesResponse;
}

export namespace GetUserRolesResponse {
  export type AsObject = {
    rolesList: Array<string>,
  }
}

export class GetUserPermissionsRequest extends jspb.Message {
  getUserId(): string;
  setUserId(value: string): void;

  getBusinessUnitId(): string;
  setBusinessUnitId(value: string): void;

  getOrganizationId(): string;
  setOrganizationId(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): GetUserPermissionsRequest.AsObject;
  static toObject(includeInstance: boolean, msg: GetUserPermissionsRequest): GetUserPermissionsRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: GetUserPermissionsRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): GetUserPermissionsRequest;
  static deserializeBinaryFromReader(message: GetUserPermissionsRequest, reader: jspb.BinaryReader): GetUserPermissionsRequest;
}

export namespace GetUserPermissionsRequest {
  export type AsObject = {
    userId: string,
    businessUnitId: string,
    organizationId: string,
  }
}

export class GetUserPermissionsResponse extends jspb.Message {
  clearPermissionsList(): void;
  getPermissionsList(): Array<string>;
  setPermissionsList(value: Array<string>): void;
  addPermissions(value: string, index?: number): string;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): GetUserPermissionsResponse.AsObject;
  static toObject(includeInstance: boolean, msg: GetUserPermissionsResponse): GetUserPermissionsResponse.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: GetUserPermissionsResponse, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): GetUserPermissionsResponse;
  static deserializeBinaryFromReader(message: GetUserPermissionsResponse, reader: jspb.BinaryReader): GetUserPermissionsResponse;
}

export namespace GetUserPermissionsResponse {
  export type AsObject = {
    permissionsList: Array<string>,
  }
}

export class IsPlatformAdminRequest extends jspb.Message {
  getUserId(): string;
  setUserId(value: string): void;

  getOrganizationId(): string;
  setOrganizationId(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): IsPlatformAdminRequest.AsObject;
  static toObject(includeInstance: boolean, msg: IsPlatformAdminRequest): IsPlatformAdminRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: IsPlatformAdminRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): IsPlatformAdminRequest;
  static deserializeBinaryFromReader(message: IsPlatformAdminRequest, reader: jspb.BinaryReader): IsPlatformAdminRequest;
}

export namespace IsPlatformAdminRequest {
  export type AsObject = {
    userId: string,
    organizationId: string,
  }
}

export class IsPlatformAdminResponse extends jspb.Message {
  getIsAdmin(): boolean;
  setIsAdmin(value: boolean): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): IsPlatformAdminResponse.AsObject;
  static toObject(includeInstance: boolean, msg: IsPlatformAdminResponse): IsPlatformAdminResponse.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: IsPlatformAdminResponse, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): IsPlatformAdminResponse;
  static deserializeBinaryFromReader(message: IsPlatformAdminResponse, reader: jspb.BinaryReader): IsPlatformAdminResponse;
}

export namespace IsPlatformAdminResponse {
  export type AsObject = {
    isAdmin: boolean,
  }
}

export class CreateUserRequest extends jspb.Message {
  getEmail(): string;
  setEmail(value: string): void;

  getUsername(): string;
  setUsername(value: string): void;

  getPassword(): string;
  setPassword(value: string): void;

  getFullName(): string;
  setFullName(value: string): void;

  getOrganizationId(): string;
  setOrganizationId(value: string): void;

  clearRoleNamesList(): void;
  getRoleNamesList(): Array<string>;
  setRoleNamesList(value: Array<string>): void;
  addRoleNames(value: string, index?: number): string;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): CreateUserRequest.AsObject;
  static toObject(includeInstance: boolean, msg: CreateUserRequest): CreateUserRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: CreateUserRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): CreateUserRequest;
  static deserializeBinaryFromReader(message: CreateUserRequest, reader: jspb.BinaryReader): CreateUserRequest;
}

export namespace CreateUserRequest {
  export type AsObject = {
    email: string,
    username: string,
    password: string,
    fullName: string,
    organizationId: string,
    roleNamesList: Array<string>,
  }
}

export class UpdateUserRequest extends jspb.Message {
  getUserId(): string;
  setUserId(value: string): void;

  getEmail(): string;
  setEmail(value: string): void;

  getFullName(): string;
  setFullName(value: string): void;

  getPassword(): string;
  setPassword(value: string): void;

  getIsActive(): boolean;
  setIsActive(value: boolean): void;

  clearRoleNamesList(): void;
  getRoleNamesList(): Array<string>;
  setRoleNamesList(value: Array<string>): void;
  addRoleNames(value: string, index?: number): string;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): UpdateUserRequest.AsObject;
  static toObject(includeInstance: boolean, msg: UpdateUserRequest): UpdateUserRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: UpdateUserRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): UpdateUserRequest;
  static deserializeBinaryFromReader(message: UpdateUserRequest, reader: jspb.BinaryReader): UpdateUserRequest;
}

export namespace UpdateUserRequest {
  export type AsObject = {
    userId: string,
    email: string,
    fullName: string,
    password: string,
    isActive: boolean,
    roleNamesList: Array<string>,
  }
}

export class DeleteUserRequest extends jspb.Message {
  getUserId(): string;
  setUserId(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): DeleteUserRequest.AsObject;
  static toObject(includeInstance: boolean, msg: DeleteUserRequest): DeleteUserRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: DeleteUserRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): DeleteUserRequest;
  static deserializeBinaryFromReader(message: DeleteUserRequest, reader: jspb.BinaryReader): DeleteUserRequest;
}

export namespace DeleteUserRequest {
  export type AsObject = {
    userId: string,
  }
}

export class GetUserRequest extends jspb.Message {
  getUserId(): string;
  setUserId(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): GetUserRequest.AsObject;
  static toObject(includeInstance: boolean, msg: GetUserRequest): GetUserRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: GetUserRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): GetUserRequest;
  static deserializeBinaryFromReader(message: GetUserRequest, reader: jspb.BinaryReader): GetUserRequest;
}

export namespace GetUserRequest {
  export type AsObject = {
    userId: string,
  }
}

export class GetCurrentUserRequest extends jspb.Message {
  getToken(): string;
  setToken(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): GetCurrentUserRequest.AsObject;
  static toObject(includeInstance: boolean, msg: GetCurrentUserRequest): GetCurrentUserRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: GetCurrentUserRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): GetCurrentUserRequest;
  static deserializeBinaryFromReader(message: GetCurrentUserRequest, reader: jspb.BinaryReader): GetCurrentUserRequest;
}

export namespace GetCurrentUserRequest {
  export type AsObject = {
    token: string,
  }
}

export class UpdateCurrentUserRequest extends jspb.Message {
  getToken(): string;
  setToken(value: string): void;

  getEmail(): string;
  setEmail(value: string): void;

  getFullName(): string;
  setFullName(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): UpdateCurrentUserRequest.AsObject;
  static toObject(includeInstance: boolean, msg: UpdateCurrentUserRequest): UpdateCurrentUserRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: UpdateCurrentUserRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): UpdateCurrentUserRequest;
  static deserializeBinaryFromReader(message: UpdateCurrentUserRequest, reader: jspb.BinaryReader): UpdateCurrentUserRequest;
}

export namespace UpdateCurrentUserRequest {
  export type AsObject = {
    token: string,
    email: string,
    fullName: string,
  }
}

export class ChangePasswordRequest extends jspb.Message {
  getToken(): string;
  setToken(value: string): void;

  getCurrentPassword(): string;
  setCurrentPassword(value: string): void;

  getNewPassword(): string;
  setNewPassword(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): ChangePasswordRequest.AsObject;
  static toObject(includeInstance: boolean, msg: ChangePasswordRequest): ChangePasswordRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: ChangePasswordRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): ChangePasswordRequest;
  static deserializeBinaryFromReader(message: ChangePasswordRequest, reader: jspb.BinaryReader): ChangePasswordRequest;
}

export namespace ChangePasswordRequest {
  export type AsObject = {
    token: string,
    currentPassword: string,
    newPassword: string,
  }
}

export class ListUsersRequest extends jspb.Message {
  getSkip(): number;
  setSkip(value: number): void;

  getLimit(): number;
  setLimit(value: number): void;

  getSearch(): string;
  setSearch(value: string): void;

  getRoleFilter(): string;
  setRoleFilter(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): ListUsersRequest.AsObject;
  static toObject(includeInstance: boolean, msg: ListUsersRequest): ListUsersRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: ListUsersRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): ListUsersRequest;
  static deserializeBinaryFromReader(message: ListUsersRequest, reader: jspb.BinaryReader): ListUsersRequest;
}

export namespace ListUsersRequest {
  export type AsObject = {
    skip: number,
    limit: number,
    search: string,
    roleFilter: string,
  }
}

export class ListUsersResponse extends jspb.Message {
  clearUsersList(): void;
  getUsersList(): Array<UserResponse>;
  setUsersList(value: Array<UserResponse>): void;
  addUsers(value?: UserResponse, index?: number): UserResponse;

  getTotal(): number;
  setTotal(value: number): void;

  getSkip(): number;
  setSkip(value: number): void;

  getLimit(): number;
  setLimit(value: number): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): ListUsersResponse.AsObject;
  static toObject(includeInstance: boolean, msg: ListUsersResponse): ListUsersResponse.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: ListUsersResponse, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): ListUsersResponse;
  static deserializeBinaryFromReader(message: ListUsersResponse, reader: jspb.BinaryReader): ListUsersResponse;
}

export namespace ListUsersResponse {
  export type AsObject = {
    usersList: Array<UserResponse.AsObject>,
    total: number,
    skip: number,
    limit: number,
  }
}

export class UserResponse extends jspb.Message {
  getId(): string;
  setId(value: string): void;

  getEmail(): string;
  setEmail(value: string): void;

  getUsername(): string;
  setUsername(value: string): void;

  getFullName(): string;
  setFullName(value: string): void;

  clearRolesList(): void;
  getRolesList(): Array<string>;
  setRolesList(value: Array<string>): void;
  addRoles(value: string, index?: number): string;

  getAvatarUrl(): string;
  setAvatarUrl(value: string): void;

  getIsActive(): boolean;
  setIsActive(value: boolean): void;

  getIsAdmin(): boolean;
  setIsAdmin(value: boolean): void;

  getCreatedAt(): string;
  setCreatedAt(value: string): void;

  getOrganizationId(): string;
  setOrganizationId(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): UserResponse.AsObject;
  static toObject(includeInstance: boolean, msg: UserResponse): UserResponse.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: UserResponse, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): UserResponse;
  static deserializeBinaryFromReader(message: UserResponse, reader: jspb.BinaryReader): UserResponse;
}

export namespace UserResponse {
  export type AsObject = {
    id: string,
    email: string,
    username: string,
    fullName: string,
    rolesList: Array<string>,
    avatarUrl: string,
    isActive: boolean,
    isAdmin: boolean,
    createdAt: string,
    organizationId: string,
  }
}

export class CreateRoleRequest extends jspb.Message {
  getName(): string;
  setName(value: string): void;

  getDescription(): string;
  setDescription(value: string): void;

  getIsPlatformRole(): boolean;
  setIsPlatformRole(value: boolean): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): CreateRoleRequest.AsObject;
  static toObject(includeInstance: boolean, msg: CreateRoleRequest): CreateRoleRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: CreateRoleRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): CreateRoleRequest;
  static deserializeBinaryFromReader(message: CreateRoleRequest, reader: jspb.BinaryReader): CreateRoleRequest;
}

export namespace CreateRoleRequest {
  export type AsObject = {
    name: string,
    description: string,
    isPlatformRole: boolean,
  }
}

export class UpdateRoleRequest extends jspb.Message {
  getRoleId(): string;
  setRoleId(value: string): void;

  getName(): string;
  setName(value: string): void;

  getDescription(): string;
  setDescription(value: string): void;

  getIsPlatformRole(): boolean;
  setIsPlatformRole(value: boolean): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): UpdateRoleRequest.AsObject;
  static toObject(includeInstance: boolean, msg: UpdateRoleRequest): UpdateRoleRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: UpdateRoleRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): UpdateRoleRequest;
  static deserializeBinaryFromReader(message: UpdateRoleRequest, reader: jspb.BinaryReader): UpdateRoleRequest;
}

export namespace UpdateRoleRequest {
  export type AsObject = {
    roleId: string,
    name: string,
    description: string,
    isPlatformRole: boolean,
  }
}

export class DeleteRoleRequest extends jspb.Message {
  getRoleId(): string;
  setRoleId(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): DeleteRoleRequest.AsObject;
  static toObject(includeInstance: boolean, msg: DeleteRoleRequest): DeleteRoleRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: DeleteRoleRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): DeleteRoleRequest;
  static deserializeBinaryFromReader(message: DeleteRoleRequest, reader: jspb.BinaryReader): DeleteRoleRequest;
}

export namespace DeleteRoleRequest {
  export type AsObject = {
    roleId: string,
  }
}

export class GetRoleRequest extends jspb.Message {
  getRoleId(): string;
  setRoleId(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): GetRoleRequest.AsObject;
  static toObject(includeInstance: boolean, msg: GetRoleRequest): GetRoleRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: GetRoleRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): GetRoleRequest;
  static deserializeBinaryFromReader(message: GetRoleRequest, reader: jspb.BinaryReader): GetRoleRequest;
}

export namespace GetRoleRequest {
  export type AsObject = {
    roleId: string,
  }
}

export class ListRolesRequest extends jspb.Message {
  hasPlatformRolesOnly(): boolean;
  clearPlatformRolesOnly(): void;
  getPlatformRolesOnly(): boolean;
  setPlatformRolesOnly(value: boolean): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): ListRolesRequest.AsObject;
  static toObject(includeInstance: boolean, msg: ListRolesRequest): ListRolesRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: ListRolesRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): ListRolesRequest;
  static deserializeBinaryFromReader(message: ListRolesRequest, reader: jspb.BinaryReader): ListRolesRequest;
}

export namespace ListRolesRequest {
  export type AsObject = {
    platformRolesOnly: boolean,
  }
}

export class ListRolesResponse extends jspb.Message {
  clearRolesList(): void;
  getRolesList(): Array<RoleResponse>;
  setRolesList(value: Array<RoleResponse>): void;
  addRoles(value?: RoleResponse, index?: number): RoleResponse;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): ListRolesResponse.AsObject;
  static toObject(includeInstance: boolean, msg: ListRolesResponse): ListRolesResponse.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: ListRolesResponse, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): ListRolesResponse;
  static deserializeBinaryFromReader(message: ListRolesResponse, reader: jspb.BinaryReader): ListRolesResponse;
}

export namespace ListRolesResponse {
  export type AsObject = {
    rolesList: Array<RoleResponse.AsObject>,
  }
}

export class AssignRoleRequest extends jspb.Message {
  getUserId(): string;
  setUserId(value: string): void;

  getRoleName(): string;
  setRoleName(value: string): void;

  getOrganizationId(): string;
  setOrganizationId(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): AssignRoleRequest.AsObject;
  static toObject(includeInstance: boolean, msg: AssignRoleRequest): AssignRoleRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: AssignRoleRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): AssignRoleRequest;
  static deserializeBinaryFromReader(message: AssignRoleRequest, reader: jspb.BinaryReader): AssignRoleRequest;
}

export namespace AssignRoleRequest {
  export type AsObject = {
    userId: string,
    roleName: string,
    organizationId: string,
  }
}

export class RemoveRoleRequest extends jspb.Message {
  getUserId(): string;
  setUserId(value: string): void;

  getRoleName(): string;
  setRoleName(value: string): void;

  getOrganizationId(): string;
  setOrganizationId(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): RemoveRoleRequest.AsObject;
  static toObject(includeInstance: boolean, msg: RemoveRoleRequest): RemoveRoleRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: RemoveRoleRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): RemoveRoleRequest;
  static deserializeBinaryFromReader(message: RemoveRoleRequest, reader: jspb.BinaryReader): RemoveRoleRequest;
}

export namespace RemoveRoleRequest {
  export type AsObject = {
    userId: string,
    roleName: string,
    organizationId: string,
  }
}

export class RoleResponse extends jspb.Message {
  getId(): string;
  setId(value: string): void;

  getName(): string;
  setName(value: string): void;

  getDescription(): string;
  setDescription(value: string): void;

  getIsPlatformRole(): boolean;
  setIsPlatformRole(value: boolean): void;

  getCreatedAt(): string;
  setCreatedAt(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): RoleResponse.AsObject;
  static toObject(includeInstance: boolean, msg: RoleResponse): RoleResponse.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: RoleResponse, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): RoleResponse;
  static deserializeBinaryFromReader(message: RoleResponse, reader: jspb.BinaryReader): RoleResponse;
}

export namespace RoleResponse {
  export type AsObject = {
    id: string,
    name: string,
    description: string,
    isPlatformRole: boolean,
    createdAt: string,
  }
}

export class CreateGroupRequest extends jspb.Message {
  getName(): string;
  setName(value: string): void;

  getDescription(): string;
  setDescription(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): CreateGroupRequest.AsObject;
  static toObject(includeInstance: boolean, msg: CreateGroupRequest): CreateGroupRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: CreateGroupRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): CreateGroupRequest;
  static deserializeBinaryFromReader(message: CreateGroupRequest, reader: jspb.BinaryReader): CreateGroupRequest;
}

export namespace CreateGroupRequest {
  export type AsObject = {
    name: string,
    description: string,
  }
}

export class UpdateGroupRequest extends jspb.Message {
  getGroupId(): string;
  setGroupId(value: string): void;

  getName(): string;
  setName(value: string): void;

  getDescription(): string;
  setDescription(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): UpdateGroupRequest.AsObject;
  static toObject(includeInstance: boolean, msg: UpdateGroupRequest): UpdateGroupRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: UpdateGroupRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): UpdateGroupRequest;
  static deserializeBinaryFromReader(message: UpdateGroupRequest, reader: jspb.BinaryReader): UpdateGroupRequest;
}

export namespace UpdateGroupRequest {
  export type AsObject = {
    groupId: string,
    name: string,
    description: string,
  }
}

export class DeleteGroupRequest extends jspb.Message {
  getGroupId(): string;
  setGroupId(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): DeleteGroupRequest.AsObject;
  static toObject(includeInstance: boolean, msg: DeleteGroupRequest): DeleteGroupRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: DeleteGroupRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): DeleteGroupRequest;
  static deserializeBinaryFromReader(message: DeleteGroupRequest, reader: jspb.BinaryReader): DeleteGroupRequest;
}

export namespace DeleteGroupRequest {
  export type AsObject = {
    groupId: string,
  }
}

export class GetGroupRequest extends jspb.Message {
  getGroupId(): string;
  setGroupId(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): GetGroupRequest.AsObject;
  static toObject(includeInstance: boolean, msg: GetGroupRequest): GetGroupRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: GetGroupRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): GetGroupRequest;
  static deserializeBinaryFromReader(message: GetGroupRequest, reader: jspb.BinaryReader): GetGroupRequest;
}

export namespace GetGroupRequest {
  export type AsObject = {
    groupId: string,
  }
}

export class ListGroupsRequest extends jspb.Message {
  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): ListGroupsRequest.AsObject;
  static toObject(includeInstance: boolean, msg: ListGroupsRequest): ListGroupsRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: ListGroupsRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): ListGroupsRequest;
  static deserializeBinaryFromReader(message: ListGroupsRequest, reader: jspb.BinaryReader): ListGroupsRequest;
}

export namespace ListGroupsRequest {
  export type AsObject = {
  }
}

export class ListGroupsResponse extends jspb.Message {
  clearGroupsList(): void;
  getGroupsList(): Array<GroupResponse>;
  setGroupsList(value: Array<GroupResponse>): void;
  addGroups(value?: GroupResponse, index?: number): GroupResponse;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): ListGroupsResponse.AsObject;
  static toObject(includeInstance: boolean, msg: ListGroupsResponse): ListGroupsResponse.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: ListGroupsResponse, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): ListGroupsResponse;
  static deserializeBinaryFromReader(message: ListGroupsResponse, reader: jspb.BinaryReader): ListGroupsResponse;
}

export namespace ListGroupsResponse {
  export type AsObject = {
    groupsList: Array<GroupResponse.AsObject>,
  }
}

export class AddGroupMemberRequest extends jspb.Message {
  getGroupId(): string;
  setGroupId(value: string): void;

  getUserId(): string;
  setUserId(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): AddGroupMemberRequest.AsObject;
  static toObject(includeInstance: boolean, msg: AddGroupMemberRequest): AddGroupMemberRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: AddGroupMemberRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): AddGroupMemberRequest;
  static deserializeBinaryFromReader(message: AddGroupMemberRequest, reader: jspb.BinaryReader): AddGroupMemberRequest;
}

export namespace AddGroupMemberRequest {
  export type AsObject = {
    groupId: string,
    userId: string,
  }
}

export class RemoveGroupMemberRequest extends jspb.Message {
  getGroupId(): string;
  setGroupId(value: string): void;

  getUserId(): string;
  setUserId(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): RemoveGroupMemberRequest.AsObject;
  static toObject(includeInstance: boolean, msg: RemoveGroupMemberRequest): RemoveGroupMemberRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: RemoveGroupMemberRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): RemoveGroupMemberRequest;
  static deserializeBinaryFromReader(message: RemoveGroupMemberRequest, reader: jspb.BinaryReader): RemoveGroupMemberRequest;
}

export namespace RemoveGroupMemberRequest {
  export type AsObject = {
    groupId: string,
    userId: string,
  }
}

export class GroupResponse extends jspb.Message {
  getId(): string;
  setId(value: string): void;

  getName(): string;
  setName(value: string): void;

  getDescription(): string;
  setDescription(value: string): void;

  getCreatedAt(): string;
  setCreatedAt(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): GroupResponse.AsObject;
  static toObject(includeInstance: boolean, msg: GroupResponse): GroupResponse.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: GroupResponse, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): GroupResponse;
  static deserializeBinaryFromReader(message: GroupResponse, reader: jspb.BinaryReader): GroupResponse;
}

export namespace GroupResponse {
  export type AsObject = {
    id: string,
    name: string,
    description: string,
    createdAt: string,
  }
}

export class CreateBusinessUnitRequest extends jspb.Message {
  getName(): string;
  setName(value: string): void;

  getSlug(): string;
  setSlug(value: string): void;

  getDescription(): string;
  setDescription(value: string): void;

  getOrganizationId(): string;
  setOrganizationId(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): CreateBusinessUnitRequest.AsObject;
  static toObject(includeInstance: boolean, msg: CreateBusinessUnitRequest): CreateBusinessUnitRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: CreateBusinessUnitRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): CreateBusinessUnitRequest;
  static deserializeBinaryFromReader(message: CreateBusinessUnitRequest, reader: jspb.BinaryReader): CreateBusinessUnitRequest;
}

export namespace CreateBusinessUnitRequest {
  export type AsObject = {
    name: string,
    slug: string,
    description: string,
    organizationId: string,
  }
}

export class UpdateBusinessUnitRequest extends jspb.Message {
  getBusinessUnitId(): string;
  setBusinessUnitId(value: string): void;

  getName(): string;
  setName(value: string): void;

  getDescription(): string;
  setDescription(value: string): void;

  getIsActive(): boolean;
  setIsActive(value: boolean): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): UpdateBusinessUnitRequest.AsObject;
  static toObject(includeInstance: boolean, msg: UpdateBusinessUnitRequest): UpdateBusinessUnitRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: UpdateBusinessUnitRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): UpdateBusinessUnitRequest;
  static deserializeBinaryFromReader(message: UpdateBusinessUnitRequest, reader: jspb.BinaryReader): UpdateBusinessUnitRequest;
}

export namespace UpdateBusinessUnitRequest {
  export type AsObject = {
    businessUnitId: string,
    name: string,
    description: string,
    isActive: boolean,
  }
}

export class DeleteBusinessUnitRequest extends jspb.Message {
  getBusinessUnitId(): string;
  setBusinessUnitId(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): DeleteBusinessUnitRequest.AsObject;
  static toObject(includeInstance: boolean, msg: DeleteBusinessUnitRequest): DeleteBusinessUnitRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: DeleteBusinessUnitRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): DeleteBusinessUnitRequest;
  static deserializeBinaryFromReader(message: DeleteBusinessUnitRequest, reader: jspb.BinaryReader): DeleteBusinessUnitRequest;
}

export namespace DeleteBusinessUnitRequest {
  export type AsObject = {
    businessUnitId: string,
  }
}

export class GetBusinessUnitRequest extends jspb.Message {
  getBusinessUnitId(): string;
  setBusinessUnitId(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): GetBusinessUnitRequest.AsObject;
  static toObject(includeInstance: boolean, msg: GetBusinessUnitRequest): GetBusinessUnitRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: GetBusinessUnitRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): GetBusinessUnitRequest;
  static deserializeBinaryFromReader(message: GetBusinessUnitRequest, reader: jspb.BinaryReader): GetBusinessUnitRequest;
}

export namespace GetBusinessUnitRequest {
  export type AsObject = {
    businessUnitId: string,
  }
}

export class ListBusinessUnitsRequest extends jspb.Message {
  getUserId(): string;
  setUserId(value: string): void;

  getOrganizationId(): string;
  setOrganizationId(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): ListBusinessUnitsRequest.AsObject;
  static toObject(includeInstance: boolean, msg: ListBusinessUnitsRequest): ListBusinessUnitsRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: ListBusinessUnitsRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): ListBusinessUnitsRequest;
  static deserializeBinaryFromReader(message: ListBusinessUnitsRequest, reader: jspb.BinaryReader): ListBusinessUnitsRequest;
}

export namespace ListBusinessUnitsRequest {
  export type AsObject = {
    userId: string,
    organizationId: string,
  }
}

export class ListBusinessUnitsResponse extends jspb.Message {
  clearBusinessUnitsList(): void;
  getBusinessUnitsList(): Array<BusinessUnitResponse>;
  setBusinessUnitsList(value: Array<BusinessUnitResponse>): void;
  addBusinessUnits(value?: BusinessUnitResponse, index?: number): BusinessUnitResponse;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): ListBusinessUnitsResponse.AsObject;
  static toObject(includeInstance: boolean, msg: ListBusinessUnitsResponse): ListBusinessUnitsResponse.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: ListBusinessUnitsResponse, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): ListBusinessUnitsResponse;
  static deserializeBinaryFromReader(message: ListBusinessUnitsResponse, reader: jspb.BinaryReader): ListBusinessUnitsResponse;
}

export namespace ListBusinessUnitsResponse {
  export type AsObject = {
    businessUnitsList: Array<BusinessUnitResponse.AsObject>,
  }
}

export class AddBusinessUnitMemberRequest extends jspb.Message {
  getBusinessUnitId(): string;
  setBusinessUnitId(value: string): void;

  getUserEmail(): string;
  setUserEmail(value: string): void;

  clearRoleIdsList(): void;
  getRoleIdsList(): Array<string>;
  setRoleIdsList(value: Array<string>): void;
  addRoleIds(value: string, index?: number): string;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): AddBusinessUnitMemberRequest.AsObject;
  static toObject(includeInstance: boolean, msg: AddBusinessUnitMemberRequest): AddBusinessUnitMemberRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: AddBusinessUnitMemberRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): AddBusinessUnitMemberRequest;
  static deserializeBinaryFromReader(message: AddBusinessUnitMemberRequest, reader: jspb.BinaryReader): AddBusinessUnitMemberRequest;
}

export namespace AddBusinessUnitMemberRequest {
  export type AsObject = {
    businessUnitId: string,
    userEmail: string,
    roleIdsList: Array<string>,
  }
}

export class RemoveBusinessUnitMemberRequest extends jspb.Message {
  getBusinessUnitId(): string;
  setBusinessUnitId(value: string): void;

  getUserId(): string;
  setUserId(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): RemoveBusinessUnitMemberRequest.AsObject;
  static toObject(includeInstance: boolean, msg: RemoveBusinessUnitMemberRequest): RemoveBusinessUnitMemberRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: RemoveBusinessUnitMemberRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): RemoveBusinessUnitMemberRequest;
  static deserializeBinaryFromReader(message: RemoveBusinessUnitMemberRequest, reader: jspb.BinaryReader): RemoveBusinessUnitMemberRequest;
}

export namespace RemoveBusinessUnitMemberRequest {
  export type AsObject = {
    businessUnitId: string,
    userId: string,
  }
}

export class ListBusinessUnitMembersRequest extends jspb.Message {
  getBusinessUnitId(): string;
  setBusinessUnitId(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): ListBusinessUnitMembersRequest.AsObject;
  static toObject(includeInstance: boolean, msg: ListBusinessUnitMembersRequest): ListBusinessUnitMembersRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: ListBusinessUnitMembersRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): ListBusinessUnitMembersRequest;
  static deserializeBinaryFromReader(message: ListBusinessUnitMembersRequest, reader: jspb.BinaryReader): ListBusinessUnitMembersRequest;
}

export namespace ListBusinessUnitMembersRequest {
  export type AsObject = {
    businessUnitId: string,
  }
}

export class ListBusinessUnitMembersResponse extends jspb.Message {
  clearMembersList(): void;
  getMembersList(): Array<BusinessUnitMemberResponse>;
  setMembersList(value: Array<BusinessUnitMemberResponse>): void;
  addMembers(value?: BusinessUnitMemberResponse, index?: number): BusinessUnitMemberResponse;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): ListBusinessUnitMembersResponse.AsObject;
  static toObject(includeInstance: boolean, msg: ListBusinessUnitMembersResponse): ListBusinessUnitMembersResponse.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: ListBusinessUnitMembersResponse, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): ListBusinessUnitMembersResponse;
  static deserializeBinaryFromReader(message: ListBusinessUnitMembersResponse, reader: jspb.BinaryReader): ListBusinessUnitMembersResponse;
}

export namespace ListBusinessUnitMembersResponse {
  export type AsObject = {
    membersList: Array<BusinessUnitMemberResponse.AsObject>,
  }
}

export class BusinessUnitResponse extends jspb.Message {
  getId(): string;
  setId(value: string): void;

  getName(): string;
  setName(value: string): void;

  getSlug(): string;
  setSlug(value: string): void;

  getDescription(): string;
  setDescription(value: string): void;

  getOrganizationId(): string;
  setOrganizationId(value: string): void;

  getIsActive(): boolean;
  setIsActive(value: boolean): void;

  getRole(): string;
  setRole(value: string): void;

  getMemberCount(): number;
  setMemberCount(value: number): void;

  getCanManageMembers(): boolean;
  setCanManageMembers(value: boolean): void;

  getCreatedAt(): string;
  setCreatedAt(value: string): void;

  getUpdatedAt(): string;
  setUpdatedAt(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): BusinessUnitResponse.AsObject;
  static toObject(includeInstance: boolean, msg: BusinessUnitResponse): BusinessUnitResponse.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: BusinessUnitResponse, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): BusinessUnitResponse;
  static deserializeBinaryFromReader(message: BusinessUnitResponse, reader: jspb.BinaryReader): BusinessUnitResponse;
}

export namespace BusinessUnitResponse {
  export type AsObject = {
    id: string,
    name: string,
    slug: string,
    description: string,
    organizationId: string,
    isActive: boolean,
    role: string,
    memberCount: number,
    canManageMembers: boolean,
    createdAt: string,
    updatedAt: string,
  }
}

export class BusinessUnitMemberResponse extends jspb.Message {
  getId(): string;
  setId(value: string): void;

  getBusinessUnitId(): string;
  setBusinessUnitId(value: string): void;

  getUserId(): string;
  setUserId(value: string): void;

  getUserEmail(): string;
  setUserEmail(value: string): void;

  getUserName(): string;
  setUserName(value: string): void;

  getRole(): string;
  setRole(value: string): void;

  getRoleId(): string;
  setRoleId(value: string): void;

  getCreatedAt(): string;
  setCreatedAt(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): BusinessUnitMemberResponse.AsObject;
  static toObject(includeInstance: boolean, msg: BusinessUnitMemberResponse): BusinessUnitMemberResponse.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: BusinessUnitMemberResponse, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): BusinessUnitMemberResponse;
  static deserializeBinaryFromReader(message: BusinessUnitMemberResponse, reader: jspb.BinaryReader): BusinessUnitMemberResponse;
}

export namespace BusinessUnitMemberResponse {
  export type AsObject = {
    id: string,
    businessUnitId: string,
    userId: string,
    userEmail: string,
    userName: string,
    role: string,
    roleId: string,
    createdAt: string,
  }
}

export class CreateOrganizationRequest extends jspb.Message {
  getName(): string;
  setName(value: string): void;

  getSlug(): string;
  setSlug(value: string): void;

  getDescription(): string;
  setDescription(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): CreateOrganizationRequest.AsObject;
  static toObject(includeInstance: boolean, msg: CreateOrganizationRequest): CreateOrganizationRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: CreateOrganizationRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): CreateOrganizationRequest;
  static deserializeBinaryFromReader(message: CreateOrganizationRequest, reader: jspb.BinaryReader): CreateOrganizationRequest;
}

export namespace CreateOrganizationRequest {
  export type AsObject = {
    name: string,
    slug: string,
    description: string,
  }
}

export class UpdateOrganizationRequest extends jspb.Message {
  getOrganizationId(): string;
  setOrganizationId(value: string): void;

  getName(): string;
  setName(value: string): void;

  getDescription(): string;
  setDescription(value: string): void;

  getIsActive(): boolean;
  setIsActive(value: boolean): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): UpdateOrganizationRequest.AsObject;
  static toObject(includeInstance: boolean, msg: UpdateOrganizationRequest): UpdateOrganizationRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: UpdateOrganizationRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): UpdateOrganizationRequest;
  static deserializeBinaryFromReader(message: UpdateOrganizationRequest, reader: jspb.BinaryReader): UpdateOrganizationRequest;
}

export namespace UpdateOrganizationRequest {
  export type AsObject = {
    organizationId: string,
    name: string,
    description: string,
    isActive: boolean,
  }
}

export class DeleteOrganizationRequest extends jspb.Message {
  getOrganizationId(): string;
  setOrganizationId(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): DeleteOrganizationRequest.AsObject;
  static toObject(includeInstance: boolean, msg: DeleteOrganizationRequest): DeleteOrganizationRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: DeleteOrganizationRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): DeleteOrganizationRequest;
  static deserializeBinaryFromReader(message: DeleteOrganizationRequest, reader: jspb.BinaryReader): DeleteOrganizationRequest;
}

export namespace DeleteOrganizationRequest {
  export type AsObject = {
    organizationId: string,
  }
}

export class GetOrganizationRequest extends jspb.Message {
  getOrganizationId(): string;
  setOrganizationId(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): GetOrganizationRequest.AsObject;
  static toObject(includeInstance: boolean, msg: GetOrganizationRequest): GetOrganizationRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: GetOrganizationRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): GetOrganizationRequest;
  static deserializeBinaryFromReader(message: GetOrganizationRequest, reader: jspb.BinaryReader): GetOrganizationRequest;
}

export namespace GetOrganizationRequest {
  export type AsObject = {
    organizationId: string,
  }
}

export class ListOrganizationsRequest extends jspb.Message {
  getSkip(): number;
  setSkip(value: number): void;

  getLimit(): number;
  setLimit(value: number): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): ListOrganizationsRequest.AsObject;
  static toObject(includeInstance: boolean, msg: ListOrganizationsRequest): ListOrganizationsRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: ListOrganizationsRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): ListOrganizationsRequest;
  static deserializeBinaryFromReader(message: ListOrganizationsRequest, reader: jspb.BinaryReader): ListOrganizationsRequest;
}

export namespace ListOrganizationsRequest {
  export type AsObject = {
    skip: number,
    limit: number,
  }
}

export class GetCurrentOrganizationRequest extends jspb.Message {
  getUserId(): string;
  setUserId(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): GetCurrentOrganizationRequest.AsObject;
  static toObject(includeInstance: boolean, msg: GetCurrentOrganizationRequest): GetCurrentOrganizationRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: GetCurrentOrganizationRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): GetCurrentOrganizationRequest;
  static deserializeBinaryFromReader(message: GetCurrentOrganizationRequest, reader: jspb.BinaryReader): GetCurrentOrganizationRequest;
}

export namespace GetCurrentOrganizationRequest {
  export type AsObject = {
    userId: string,
  }
}

export class OrganizationResponse extends jspb.Message {
  getId(): string;
  setId(value: string): void;

  getName(): string;
  setName(value: string): void;

  getSlug(): string;
  setSlug(value: string): void;

  getDescription(): string;
  setDescription(value: string): void;

  getIsActive(): boolean;
  setIsActive(value: boolean): void;

  getCreatedAt(): string;
  setCreatedAt(value: string): void;

  getUpdatedAt(): string;
  setUpdatedAt(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): OrganizationResponse.AsObject;
  static toObject(includeInstance: boolean, msg: OrganizationResponse): OrganizationResponse.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: OrganizationResponse, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): OrganizationResponse;
  static deserializeBinaryFromReader(message: OrganizationResponse, reader: jspb.BinaryReader): OrganizationResponse;
}

export namespace OrganizationResponse {
  export type AsObject = {
    id: string,
    name: string,
    slug: string,
    description: string,
    isActive: boolean,
    createdAt: string,
    updatedAt: string,
  }
}

export class ListOrganizationsResponse extends jspb.Message {
  clearOrganizationsList(): void;
  getOrganizationsList(): Array<OrganizationResponse>;
  setOrganizationsList(value: Array<OrganizationResponse>): void;
  addOrganizations(value?: OrganizationResponse, index?: number): OrganizationResponse;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): ListOrganizationsResponse.AsObject;
  static toObject(includeInstance: boolean, msg: ListOrganizationsResponse): ListOrganizationsResponse.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: ListOrganizationsResponse, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): ListOrganizationsResponse;
  static deserializeBinaryFromReader(message: ListOrganizationsResponse, reader: jspb.BinaryReader): ListOrganizationsResponse;
}

export namespace ListOrganizationsResponse {
  export type AsObject = {
    organizationsList: Array<OrganizationResponse.AsObject>,
  }
}

export class CreateBusinessUnitGroupRequest extends jspb.Message {
  getBusinessUnitId(): string;
  setBusinessUnitId(value: string): void;

  getName(): string;
  setName(value: string): void;

  getDescription(): string;
  setDescription(value: string): void;

  getRoleId(): string;
  setRoleId(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): CreateBusinessUnitGroupRequest.AsObject;
  static toObject(includeInstance: boolean, msg: CreateBusinessUnitGroupRequest): CreateBusinessUnitGroupRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: CreateBusinessUnitGroupRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): CreateBusinessUnitGroupRequest;
  static deserializeBinaryFromReader(message: CreateBusinessUnitGroupRequest, reader: jspb.BinaryReader): CreateBusinessUnitGroupRequest;
}

export namespace CreateBusinessUnitGroupRequest {
  export type AsObject = {
    businessUnitId: string,
    name: string,
    description: string,
    roleId: string,
  }
}

export class UpdateBusinessUnitGroupRequest extends jspb.Message {
  getBusinessUnitId(): string;
  setBusinessUnitId(value: string): void;

  getGroupId(): string;
  setGroupId(value: string): void;

  getName(): string;
  setName(value: string): void;

  getDescription(): string;
  setDescription(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): UpdateBusinessUnitGroupRequest.AsObject;
  static toObject(includeInstance: boolean, msg: UpdateBusinessUnitGroupRequest): UpdateBusinessUnitGroupRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: UpdateBusinessUnitGroupRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): UpdateBusinessUnitGroupRequest;
  static deserializeBinaryFromReader(message: UpdateBusinessUnitGroupRequest, reader: jspb.BinaryReader): UpdateBusinessUnitGroupRequest;
}

export namespace UpdateBusinessUnitGroupRequest {
  export type AsObject = {
    businessUnitId: string,
    groupId: string,
    name: string,
    description: string,
  }
}

export class DeleteBusinessUnitGroupRequest extends jspb.Message {
  getBusinessUnitId(): string;
  setBusinessUnitId(value: string): void;

  getGroupId(): string;
  setGroupId(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): DeleteBusinessUnitGroupRequest.AsObject;
  static toObject(includeInstance: boolean, msg: DeleteBusinessUnitGroupRequest): DeleteBusinessUnitGroupRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: DeleteBusinessUnitGroupRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): DeleteBusinessUnitGroupRequest;
  static deserializeBinaryFromReader(message: DeleteBusinessUnitGroupRequest, reader: jspb.BinaryReader): DeleteBusinessUnitGroupRequest;
}

export namespace DeleteBusinessUnitGroupRequest {
  export type AsObject = {
    businessUnitId: string,
    groupId: string,
  }
}

export class GetBusinessUnitGroupRequest extends jspb.Message {
  getBusinessUnitId(): string;
  setBusinessUnitId(value: string): void;

  getGroupId(): string;
  setGroupId(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): GetBusinessUnitGroupRequest.AsObject;
  static toObject(includeInstance: boolean, msg: GetBusinessUnitGroupRequest): GetBusinessUnitGroupRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: GetBusinessUnitGroupRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): GetBusinessUnitGroupRequest;
  static deserializeBinaryFromReader(message: GetBusinessUnitGroupRequest, reader: jspb.BinaryReader): GetBusinessUnitGroupRequest;
}

export namespace GetBusinessUnitGroupRequest {
  export type AsObject = {
    businessUnitId: string,
    groupId: string,
  }
}

export class ListBusinessUnitGroupsRequest extends jspb.Message {
  getBusinessUnitId(): string;
  setBusinessUnitId(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): ListBusinessUnitGroupsRequest.AsObject;
  static toObject(includeInstance: boolean, msg: ListBusinessUnitGroupsRequest): ListBusinessUnitGroupsRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: ListBusinessUnitGroupsRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): ListBusinessUnitGroupsRequest;
  static deserializeBinaryFromReader(message: ListBusinessUnitGroupsRequest, reader: jspb.BinaryReader): ListBusinessUnitGroupsRequest;
}

export namespace ListBusinessUnitGroupsRequest {
  export type AsObject = {
    businessUnitId: string,
  }
}

export class AddBusinessUnitGroupMemberRequest extends jspb.Message {
  getBusinessUnitId(): string;
  setBusinessUnitId(value: string): void;

  getGroupId(): string;
  setGroupId(value: string): void;

  getUserId(): string;
  setUserId(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): AddBusinessUnitGroupMemberRequest.AsObject;
  static toObject(includeInstance: boolean, msg: AddBusinessUnitGroupMemberRequest): AddBusinessUnitGroupMemberRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: AddBusinessUnitGroupMemberRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): AddBusinessUnitGroupMemberRequest;
  static deserializeBinaryFromReader(message: AddBusinessUnitGroupMemberRequest, reader: jspb.BinaryReader): AddBusinessUnitGroupMemberRequest;
}

export namespace AddBusinessUnitGroupMemberRequest {
  export type AsObject = {
    businessUnitId: string,
    groupId: string,
    userId: string,
  }
}

export class RemoveBusinessUnitGroupMemberRequest extends jspb.Message {
  getBusinessUnitId(): string;
  setBusinessUnitId(value: string): void;

  getGroupId(): string;
  setGroupId(value: string): void;

  getUserId(): string;
  setUserId(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): RemoveBusinessUnitGroupMemberRequest.AsObject;
  static toObject(includeInstance: boolean, msg: RemoveBusinessUnitGroupMemberRequest): RemoveBusinessUnitGroupMemberRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: RemoveBusinessUnitGroupMemberRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): RemoveBusinessUnitGroupMemberRequest;
  static deserializeBinaryFromReader(message: RemoveBusinessUnitGroupMemberRequest, reader: jspb.BinaryReader): RemoveBusinessUnitGroupMemberRequest;
}

export namespace RemoveBusinessUnitGroupMemberRequest {
  export type AsObject = {
    businessUnitId: string,
    groupId: string,
    userId: string,
  }
}

export class ListBusinessUnitGroupMembersRequest extends jspb.Message {
  getBusinessUnitId(): string;
  setBusinessUnitId(value: string): void;

  getGroupId(): string;
  setGroupId(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): ListBusinessUnitGroupMembersRequest.AsObject;
  static toObject(includeInstance: boolean, msg: ListBusinessUnitGroupMembersRequest): ListBusinessUnitGroupMembersRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: ListBusinessUnitGroupMembersRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): ListBusinessUnitGroupMembersRequest;
  static deserializeBinaryFromReader(message: ListBusinessUnitGroupMembersRequest, reader: jspb.BinaryReader): ListBusinessUnitGroupMembersRequest;
}

export namespace ListBusinessUnitGroupMembersRequest {
  export type AsObject = {
    businessUnitId: string,
    groupId: string,
  }
}

export class BusinessUnitGroupResponse extends jspb.Message {
  getId(): string;
  setId(value: string): void;

  getBusinessUnitId(): string;
  setBusinessUnitId(value: string): void;

  getName(): string;
  setName(value: string): void;

  getDescription(): string;
  setDescription(value: string): void;

  getCreatedAt(): string;
  setCreatedAt(value: string): void;

  getUpdatedAt(): string;
  setUpdatedAt(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): BusinessUnitGroupResponse.AsObject;
  static toObject(includeInstance: boolean, msg: BusinessUnitGroupResponse): BusinessUnitGroupResponse.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: BusinessUnitGroupResponse, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): BusinessUnitGroupResponse;
  static deserializeBinaryFromReader(message: BusinessUnitGroupResponse, reader: jspb.BinaryReader): BusinessUnitGroupResponse;
}

export namespace BusinessUnitGroupResponse {
  export type AsObject = {
    id: string,
    businessUnitId: string,
    name: string,
    description: string,
    createdAt: string,
    updatedAt: string,
  }
}

export class ListBusinessUnitGroupsResponse extends jspb.Message {
  clearGroupsList(): void;
  getGroupsList(): Array<BusinessUnitGroupResponse>;
  setGroupsList(value: Array<BusinessUnitGroupResponse>): void;
  addGroups(value?: BusinessUnitGroupResponse, index?: number): BusinessUnitGroupResponse;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): ListBusinessUnitGroupsResponse.AsObject;
  static toObject(includeInstance: boolean, msg: ListBusinessUnitGroupsResponse): ListBusinessUnitGroupsResponse.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: ListBusinessUnitGroupsResponse, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): ListBusinessUnitGroupsResponse;
  static deserializeBinaryFromReader(message: ListBusinessUnitGroupsResponse, reader: jspb.BinaryReader): ListBusinessUnitGroupsResponse;
}

export namespace ListBusinessUnitGroupsResponse {
  export type AsObject = {
    groupsList: Array<BusinessUnitGroupResponse.AsObject>,
  }
}

export class BusinessUnitGroupMemberResponse extends jspb.Message {
  getId(): string;
  setId(value: string): void;

  getBusinessUnitId(): string;
  setBusinessUnitId(value: string): void;

  getGroupId(): string;
  setGroupId(value: string): void;

  getUserId(): string;
  setUserId(value: string): void;

  getUserEmail(): string;
  setUserEmail(value: string): void;

  getUserName(): string;
  setUserName(value: string): void;

  getCreatedAt(): string;
  setCreatedAt(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): BusinessUnitGroupMemberResponse.AsObject;
  static toObject(includeInstance: boolean, msg: BusinessUnitGroupMemberResponse): BusinessUnitGroupMemberResponse.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: BusinessUnitGroupMemberResponse, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): BusinessUnitGroupMemberResponse;
  static deserializeBinaryFromReader(message: BusinessUnitGroupMemberResponse, reader: jspb.BinaryReader): BusinessUnitGroupMemberResponse;
}

export namespace BusinessUnitGroupMemberResponse {
  export type AsObject = {
    id: string,
    businessUnitId: string,
    groupId: string,
    userId: string,
    userEmail: string,
    userName: string,
    createdAt: string,
  }
}

export class ListBusinessUnitGroupMembersResponse extends jspb.Message {
  clearMembersList(): void;
  getMembersList(): Array<BusinessUnitGroupMemberResponse>;
  setMembersList(value: Array<BusinessUnitGroupMemberResponse>): void;
  addMembers(value?: BusinessUnitGroupMemberResponse, index?: number): BusinessUnitGroupMemberResponse;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): ListBusinessUnitGroupMembersResponse.AsObject;
  static toObject(includeInstance: boolean, msg: ListBusinessUnitGroupMembersResponse): ListBusinessUnitGroupMembersResponse.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: ListBusinessUnitGroupMembersResponse, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): ListBusinessUnitGroupMembersResponse;
  static deserializeBinaryFromReader(message: ListBusinessUnitGroupMembersResponse, reader: jspb.BinaryReader): ListBusinessUnitGroupMembersResponse;
}

export namespace ListBusinessUnitGroupMembersResponse {
  export type AsObject = {
    membersList: Array<BusinessUnitGroupMemberResponse.AsObject>,
  }
}

export class CreateCredentialRequest extends jspb.Message {
  getName(): string;
  setName(value: string): void;

  getProvider(): string;
  setProvider(value: string): void;

  getCredentials(): string;
  setCredentials(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): CreateCredentialRequest.AsObject;
  static toObject(includeInstance: boolean, msg: CreateCredentialRequest): CreateCredentialRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: CreateCredentialRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): CreateCredentialRequest;
  static deserializeBinaryFromReader(message: CreateCredentialRequest, reader: jspb.BinaryReader): CreateCredentialRequest;
}

export namespace CreateCredentialRequest {
  export type AsObject = {
    name: string,
    provider: string,
    credentials: string,
  }
}

export class UpdateCredentialRequest extends jspb.Message {
  getCredentialId(): string;
  setCredentialId(value: string): void;

  getName(): string;
  setName(value: string): void;

  getCredentials(): string;
  setCredentials(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): UpdateCredentialRequest.AsObject;
  static toObject(includeInstance: boolean, msg: UpdateCredentialRequest): UpdateCredentialRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: UpdateCredentialRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): UpdateCredentialRequest;
  static deserializeBinaryFromReader(message: UpdateCredentialRequest, reader: jspb.BinaryReader): UpdateCredentialRequest;
}

export namespace UpdateCredentialRequest {
  export type AsObject = {
    credentialId: string,
    name: string,
    credentials: string,
  }
}

export class DeleteCredentialRequest extends jspb.Message {
  getCredentialId(): string;
  setCredentialId(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): DeleteCredentialRequest.AsObject;
  static toObject(includeInstance: boolean, msg: DeleteCredentialRequest): DeleteCredentialRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: DeleteCredentialRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): DeleteCredentialRequest;
  static deserializeBinaryFromReader(message: DeleteCredentialRequest, reader: jspb.BinaryReader): DeleteCredentialRequest;
}

export namespace DeleteCredentialRequest {
  export type AsObject = {
    credentialId: string,
  }
}

export class GetCredentialRequest extends jspb.Message {
  getCredentialId(): string;
  setCredentialId(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): GetCredentialRequest.AsObject;
  static toObject(includeInstance: boolean, msg: GetCredentialRequest): GetCredentialRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: GetCredentialRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): GetCredentialRequest;
  static deserializeBinaryFromReader(message: GetCredentialRequest, reader: jspb.BinaryReader): GetCredentialRequest;
}

export namespace GetCredentialRequest {
  export type AsObject = {
    credentialId: string,
  }
}

export class ListCredentialsRequest extends jspb.Message {
  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): ListCredentialsRequest.AsObject;
  static toObject(includeInstance: boolean, msg: ListCredentialsRequest): ListCredentialsRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: ListCredentialsRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): ListCredentialsRequest;
  static deserializeBinaryFromReader(message: ListCredentialsRequest, reader: jspb.BinaryReader): ListCredentialsRequest;
}

export namespace ListCredentialsRequest {
  export type AsObject = {
  }
}

export class CredentialResponse extends jspb.Message {
  getId(): string;
  setId(value: string): void;

  getName(): string;
  setName(value: string): void;

  getProvider(): string;
  setProvider(value: string): void;

  getCreatedAt(): string;
  setCreatedAt(value: string): void;

  getUpdatedAt(): string;
  setUpdatedAt(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): CredentialResponse.AsObject;
  static toObject(includeInstance: boolean, msg: CredentialResponse): CredentialResponse.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: CredentialResponse, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): CredentialResponse;
  static deserializeBinaryFromReader(message: CredentialResponse, reader: jspb.BinaryReader): CredentialResponse;
}

export namespace CredentialResponse {
  export type AsObject = {
    id: string,
    name: string,
    provider: string,
    createdAt: string,
    updatedAt: string,
  }
}

export class ListCredentialsResponse extends jspb.Message {
  clearCredentialsList(): void;
  getCredentialsList(): Array<CredentialResponse>;
  setCredentialsList(value: Array<CredentialResponse>): void;
  addCredentials(value?: CredentialResponse, index?: number): CredentialResponse;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): ListCredentialsResponse.AsObject;
  static toObject(includeInstance: boolean, msg: ListCredentialsResponse): ListCredentialsResponse.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: ListCredentialsResponse, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): ListCredentialsResponse;
  static deserializeBinaryFromReader(message: ListCredentialsResponse, reader: jspb.BinaryReader): ListCredentialsResponse;
}

export namespace ListCredentialsResponse {
  export type AsObject = {
    credentialsList: Array<CredentialResponse.AsObject>,
  }
}

