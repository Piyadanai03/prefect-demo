# ใช้ Debian 11 (Python 3.10) เพื่อให้รองรับ OpenSSL 1.1.1
# สาเหตุ: SQL Server ปลายทางเป็นเวอร์ชันเก่า (Legacy SSL)
# ถ้า SQL Server อัปเกรดแล้ว สามารถเปลี่ยนกลับไปใช้ python:3.11-slim (Debian 12) ได้
FROM python:3.10-slim-bullseye

WORKDIR /app

# ลง Driver SQL Server และ Tools
RUN apt-get update && apt-get install -y \
    curl \
    gnupg2 \
    unixodbc \
    unixodbc-dev \
    freetds-dev \
    freetds-bin \
    tdsodbc \
    && curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /etc/apt/trusted.gpg.d/microsoft.gpg \
    && curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# แก้ SSL: ลด MinProtocol เป็น TLSv1.0 และลด SECLEVEL เป็น 0
# (คำสั่งนี้จะไปหาคำว่า TLSv1.2 แล้วแก้เป็น TLSv1.0 ในไฟล์ config)
RUN sed -i 's/MinProtocol = TLSv1.2/MinProtocol = TLSv1.0/g' /etc/ssl/openssl.cnf \
    && sed -i 's/CipherString = DEFAULT@SECLEVEL=2/CipherString = DEFAULT@SECLEVEL=0/g' /etc/ssl/openssl.cnf

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY database_connection/ ./database_connection/
COPY flows/ ./flows/

CMD ["prefect", "worker", "start", "--pool", "cedar7-pool"]