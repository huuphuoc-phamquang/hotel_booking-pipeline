# Build từ thư mục edai1: docker build -f k8s/flink.Dockerfile -t REGISTRY/data/flink-booking:TAG .
# base Ubuntu 22.04 (python 3.10, PyFlink 1.20 hỗ trợ 3.8-3.11)
FROM flink:1.20.1-scala_2.12-java17
RUN apt-get update && apt-get install -y --no-install-recommends python3 python3-pip && rm -rf /var/lib/apt/lists/* \
 && ln -s /usr/bin/python3 /usr/bin/python && pip3 install --no-cache-dir apache-flink==1.20.1 jsonschema==4.26.0
ADD https://repo1.maven.org/maven2/org/apache/flink/flink-sql-connector-kafka/3.3.0-1.20/flink-sql-connector-kafka-3.3.0-1.20.jar /opt/flink/lib/
# 3.1.2-1.18: bản cuối còn JdbcOutputFormat.createRowJdbcStatementBuilder mà JdbcSink của PyFlink 1.20 gọi bằng
# reflection (từ 3.2.0 hàm này chuyển sang RowJdbcOutputFormat); chạy được trên Flink 1.20 (tests/test_stream_e2e.py)
ADD https://repo1.maven.org/maven2/org/apache/flink/flink-connector-jdbc/3.1.2-1.18/flink-connector-jdbc-3.1.2-1.18.jar /opt/flink/lib/
ADD https://repo1.maven.org/maven2/org/postgresql/postgresql/42.7.7/postgresql-42.7.7.jar /opt/flink/lib/
RUN mkdir -p /opt/flink/plugins/s3-fs-hadoop && cp /opt/flink/opt/flink-s3-fs-hadoop-1.20.1.jar /opt/flink/plugins/s3-fs-hadoop/
COPY flink_jobs/ /opt/flink/usrlib/
COPY schema/contracts/ /opt/flink/schema/contracts/
