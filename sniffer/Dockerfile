FROM mitmproxy/mitmproxy:latest

WORKDIR /scripts

COPY main.py .
CMD ["mitmproxy", "--listen-host", "0.0.0.0", "--listen-port", "8080", "-s", "main.py"]
