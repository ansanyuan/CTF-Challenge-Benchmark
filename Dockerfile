FROM docker.cat/docker/python:3.12
WORKDIR /app
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-setuptools \
    python3-wheel
 # 复制依赖文件
COPY pyproject.toml ./

# 安装项目依赖
RUN pip3 install --no-cache-dir -i http://pypi.dog.cat/root/pypi/+simple/ --trusted-host pypi.dog.cat .

# 复制源代码
COPY . .

# 重新安装项目
RUN pip3 install --no-cache-dir -i http://pypi.dog.cat/root/pypi/+simple/ --trusted-host pypi.dog.cat . --force-reinstall --no-deps

CMD ["ccb"]