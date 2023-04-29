FROM opencfd/openfoam2106-dev

RUN apt-get update && \
    apt-get install -y make &&\
    apt-get install -y build-essential && \
    apt-get install -y flex bison &&\
    apt-get install -y python3 python3-pip && \
    apt-get install -y libc-dev && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Create a non-root user
RUN useradd --create-home --shell /bin/bash openfoam_user

# Switch to the non-root user
USER openfoam_user

WORKDIR /app
COPY --chown=openfoam_user:openfoam_user . .
SHELL ["/bin/bash", "-l", "-c"]
RUN pip3 install --user -r requirements.txt

ENTRYPOINT [ "python3" ]
CMD ["nabla.py"]

