FROM python:3.12-slim
# Debian 13: gói docker.io không còn kèm docker CLI khi --no-install-recommends -> lấy CLI từ image chính thức
COPY --from=docker:27-cli /usr/local/bin/docker /usr/local/bin/docker
RUN apt-get update && apt-get install -y --no-install-recommends curl git && rm -rf /var/lib/apt/lists/* \
 && curl -fsSL https://get.helm.sh/helm-v4.3.2-linux-amd64.tar.gz | tar xz -C /tmp && mv /tmp/linux-amd64/helm /usr/local/bin/ \
 && curl -fsSLo /usr/local/bin/kubectl https://dl.k8s.io/release/v1.34.0/bin/linux/amd64/kubectl && chmod +x /usr/local/bin/kubectl
RUN pip install --no-cache-dir "mutmut<3" langfuse pyyaml requests mlflow
# workspace do container jnlp (uid 1000) checkout, tools chạy root: git coi là "dubious ownership" và từ chối repo
RUN git config --system --add safe.directory '*'
