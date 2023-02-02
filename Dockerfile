FROM opencfd/openfoam2106-dev
RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    apt-get clean && rm -rf /var/lib/apt/lists/*


WORKDIR /app
COPY . /app/

RUN pip3 install -r requirements.txt
CMD ["cd","/app"]
#CMD ["pytest", "tests"]
