#!/usr/bin/env python3
"""
Simple gRPC test client for auth microservice
Run this after the service is up to test gRPC endpoints directly
"""
import grpc
import sys
import os

# Add proto to path
sys.path.insert(0, os.path.dirname(__file__))

try:
    from proto import auth_pb2, auth_pb2_grpc
except ImportError:
    print("ERROR: Proto files not generated. Run generate_proto.sh first or build Docker image.")
    sys.exit(1)


def test_login(channel):
    """Test login endpoint"""
    stub = auth_pb2_grpc.AuthenticationServiceStub(channel)
    
    request = auth_pb2.LoginRequest(
        identifier="admin@foundry-idp.com",
        password="admin123"
    )
    
    try:
        response = stub.Login(request)
        print("✓ Login successful!")
        print(f"  Access Token: {response.access_token[:50]}...")
        print(f"  User: {response.user.email} ({response.user.username})")
        print(f"  Roles: {', '.join(response.user.roles)}")
        return response
    except grpc.RpcError as e:
        print(f"✗ Login failed: {e.code()} - {e.details()}")
        return None


def test_validate_token(channel, token):
    """Test token validation"""
    stub = auth_pb2_grpc.AuthenticationServiceStub(channel)
    
    request = auth_pb2.ValidateTokenRequest(token=token)
    
    try:
        response = stub.ValidateToken(request)
        print("✓ Token validation successful!")
        print(f"  User ID: {response.user_id}")
        print(f"  Email: {response.email}")
        print(f"  Username: {response.username}")
        return response
    except grpc.RpcError as e:
        print(f"✗ Token validation failed: {e.code()} - {e.details()}")
        return None


def test_check_permission(channel, user_id, permission):
    """Test permission check"""
    stub = auth_pb2_grpc.AuthorizationServiceStub(channel)
    
    request = auth_pb2.PermissionCheckRequest(
        user_id=user_id,
        permission_slug=permission,
        business_unit_id="",
        organization_id=""
    )
    
    try:
        response = stub.CheckPermission(request)
        if response.allowed:
            print(f"✓ Permission '{permission}' granted")
        else:
            print(f"✗ Permission '{permission}' denied: {response.message}")
        return response
    except grpc.RpcError as e:
        print(f"✗ Permission check failed: {e.code()} - {e.details()}")
        return None


def main():
    """Run all tests"""
    print("=" * 50)
    print("Auth Microservice gRPC Test Client")
    print("=" * 50)
    
    # Connect to gRPC server
    server_address = os.getenv("AUTH_SERVICE_URL", "localhost:50051")
    print(f"\nConnecting to {server_address}...")
    
    try:
        channel = grpc.insecure_channel(server_address)
        
        # Test connection
        try:
            grpc.channel_ready_future(channel).result(timeout=5)
            print("✓ Connected to gRPC server")
        except grpc.FutureTimeoutError:
            print("✗ Connection timeout. Is the auth-service running?")
            return
        
        # Test 1: Login
        print("\n" + "-" * 50)
        print("Test 1: Login")
        print("-" * 50)
        login_response = test_login(channel)
        
        if login_response:
            # Test 2: Validate Token
            print("\n" + "-" * 50)
            print("Test 2: Validate Token")
            print("-" * 50)
            validate_response = test_validate_token(channel, login_response.access_token)
            
            if validate_response:
                # Test 3: Check Permission
                print("\n" + "-" * 50)
                print("Test 3: Check Permission")
                print("-" * 50)
                test_check_permission(
                    channel,
                    validate_response.user_id,
                    "platform:users:list"
                )
        
        channel.close()
        print("\n" + "=" * 50)
        print("Tests completed!")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
