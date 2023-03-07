FROM opencfd/openfoam2106-dev
RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    apt-get install -y libc-dev && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .
SHELL ["/bin/bash", "-l", "-c"]
RUN pip3 install -r requirements.txt

CMD ["pytest","-s"]

