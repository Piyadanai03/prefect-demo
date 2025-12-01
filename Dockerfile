FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    unixodbc \
    unixodbc-dev \
    freetds-dev \
    freetds-bin \
    tdsodbc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# เพิ่ม FreeTDS config
RUN echo "[FreeTDS]" >> /etc/odbcinst.ini && \
    echo "Description = TDS driver (Sybase/MS SQL)" >> /etc/odbcinst.ini && \
    echo "Driver = /usr/lib/x86_64-linux-gnu/odbc/libtdsodbc.so" >> /etc/odbcinst.ini && \
    echo "Setup = /usr/lib/x86_64-linux-gnu/odbc/libtdsS.so" >> /etc/odbcinst.ini && \
    echo "CPTimeout =" >> /etc/odbcinst.ini && \
    echo "CPReuse =" >> /etc/odbcinst.ini && \
    echo "" >> /etc/odbcinst.ini && \
    echo "[SQL Server]" >> /etc/odbcinst.ini && \
    echo "Description = FreeTDS SQL Server" >> /etc/odbcinst.ini && \
    echo "Driver = /usr/lib/x86_64-linux-gnu/odbc/libtdsodbc.so" >> /etc/odbcinst.ini && \
    echo "Setup = /usr/lib/x86_64-linux-gnu/odbc/libtdsS.so" >> /etc/odbcinst.ini && \
    echo "UsageCount = 1" >> /etc/odbcinst.ini

# freetds.conf - รองรับภาษาไทย
RUN echo "[global]" > /etc/freetds/freetds.conf && \
    echo "tds version = 7.4" >> /etc/freetds/freetds.conf && \
    echo "client charset = UTF-8" >> /etc/freetds/freetds.conf && \
    echo "use utf-16 = yes" >> /etc/freetds/freetds.conf && \
    echo "text size = 64512" >> /etc/freetds/freetds.conf && \
    echo "encryption = off" >> /etc/freetds/freetds.conf

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY flows/ ./flows/

CMD ["prefect", "worker", "start", "--pool", "cedar7-pool"]