# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0


FROM python:3.12-slim-bookworm as base

FROM base as builder
RUN apt-get -qq update \
    && apt-get install -y --no-install-recommends g++ \
    && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt .
RUN pip install --prefix="/reqs" -r requirements.txt
RUN export LOCUST_BROWSER_TRAFFIC_ENABLED=true
FROM base
WORKDIR /usr/src/app/
COPY --from=builder /reqs /usr/local
COPY ./locustfile.py .
ENV LOCUST_PLAYWRIGHT=1
RUN playwright install --with-deps chromium
ENV PORT "8089"
EXPOSE 8089
ENTRYPOINT ["locust", "-f", "locustfile.py", "--host", "http://frontend:8080"]