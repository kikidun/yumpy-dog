#Stage 1
FROM python:3.10-slim 
WORKDIR /worker
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

#Stage 2
#FROM python:3.11-slim
WORKDIR /worker
#COPY --from=builder /root/.local /root/.local
COPY ./ ./worker/

# Download RDS CA bundle
RUN python3 -c "import urllib.request; urllib.request.urlretrieve('https://truststore.pki.rds.amazonaws.com/global/global-bundle.pem', '/app/rds-ca-2019-root.pem')"
ENV PATH=/root/.local/bin:$PATH
CMD ["python3", "-u", "worker/main.py"]