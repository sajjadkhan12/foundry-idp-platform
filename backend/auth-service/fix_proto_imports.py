#!/usr/bin/env python3
"""Fix imports in generated proto grpc files"""
import re
import glob
import os

for grpc_file in glob.glob('proto/*_pb2_grpc.py'):
    with open(grpc_file, 'r') as f:
        content = f.read()
    
    # Fix: import auth_pb2 as auth__pb2 -> from proto import auth_pb2 as auth__pb2
    content = re.sub(
        r'^import (auth_pb2|audit_pb2) as (\w+)',
        r'from proto import \1 as \2',
        content,
        flags=re.MULTILINE
    )
    
    # Fix: from auth_pb2 import -> from proto.auth_pb2 import
    content = content.replace('from auth_pb2 import', 'from proto.auth_pb2 import')
    content = content.replace('from audit_pb2 import', 'from proto.audit_pb2 import')
    
    with open(grpc_file, 'w') as f:
        f.write(content)
    
    print(f"Fixed imports in {grpc_file}")
