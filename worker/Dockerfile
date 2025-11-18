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
ENV PATH=/root/.local/bin:$PATH
CMD ["python3", "-u", "worker/main.py"]