#Stage 1
FROM python:3.10-slim 
WORKDIR /app
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

#Stage 2
#FROM python:3.11-slim
WORKDIR /app
#COPY --from=builder /root/.local /root/.local
COPY ./ ./app/
ENV PATH=/root/.local/bin:$PATH
CMD ["python3", "-u","app/app.py"]