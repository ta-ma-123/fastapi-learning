FROM mcr.microsoft.com/devcontainers/python:3.12

WORKDIR /workspace

# Pythonライブラリをインストールする
COPY requirements.txt /tmp/requirements.txt

RUN pip install --no-cache-dir -r /tmp/requirements.txt
