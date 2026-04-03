# Scanner V3 - 生产 Docker 镜像
FROM python:3.11-slim

# 工作目录
WORKDIR /app

# 环境变量
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# 安装依赖
RUN pip install --no-cache-dir \
    requests==2.31.0

# 复制代码
COPY round16/ast_engine_v2.py /app/
COPY round18/batch_scanner.py /app/
COPY round18/cache_manager.py /app/
COPY round18/parallel_executor.py /app/
COPY round19/web_dashboard.py /app/
COPY round19/cli_tool.py /app/
COPY round19/alert_manager.py /app/
COPY samples/ /app/samples/
COPY rules/ /app/rules/

# 创建数据目录
RUN mkdir -p /app/cache /app/logs /app/results

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 -c "import requests; requests.get('http://localhost:8080')" || exit 1

# 暴露端口
EXPOSE 8080

# 启动命令
CMD ["python3", "round19/web_dashboard.py", "8080"]
