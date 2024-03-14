FROM alpine:3.19

WORKDIR /app

COPY deployment/requirements.txt .

RUN apk update && \
    apk add python3 py3-pip

RUN pip install --no-cache-dir --upgrade pip --break-system-packages

RUN pip install -r requirements.txt --break-system-packages

COPY kube_sidecar_vpn kube_sidecar_vpn

ENV PYTHONPATH "${PYTHONPATH}:/app"

CMD [ "python", "./kube_sidecar_vpn/main.py" ]