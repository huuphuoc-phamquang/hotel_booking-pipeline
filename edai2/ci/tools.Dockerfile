FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends curl git docker.io && rm -rf /var/lib/apt/lists/* \
 && curl -fsSL https://get.helm.sh/helm-v4.3.2-linux-amd64.tar.gz | tar xz -C /tmp && mv /tmp/linux-amd64/helm /usr/local/bin/ \
 && curl -fsSLo /usr/local/bin/kubectl https://dl.k8s.io/release/v1.34.0/bin/linux/amd64/kubectl && chmod +x /usr/local/bin/kubectl
RUN pip install --no-cache-dir "mutmut<3" langfuse pyyaml requests mlflow
