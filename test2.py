import os
import subprocess

# 指定你的 .proto 文件的目录
proto_dir = '/Users/yzq/fiture/workspace/petlocust/libs/protobuf_file'

# 遍历目录，找到所有 .proto 文件
for proto_file in os.listdir(proto_dir):
    if proto_file.endswith('.proto'):

        # 构造完整的文件路径
        full_proto_file = os.path.join(proto_dir, proto_file)

        # 构造 protoc 命令
        command = '/Users/yzq/fiture/workspace/petlocust/libs/protoc-23.3-osx-x86_64/bin/protoc -I {} --python_out={} {}'.format(proto_dir, proto_dir, full_proto_file)

        # 通过 subprocess 执行命令
        try:
            output = subprocess.check_output(command, shell=True)
            print(output)
        except subprocess.CalledProcessError as e:
            print(e.output)