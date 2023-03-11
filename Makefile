
# Define variables
IMAGE_NAME := pythonandfoam
CONTAINER_NAME := mycontainer
TESTS_DIR := /app/tests/
DOCKERFILE := Dockerfile

# Define targets
.PHONY: build run runf test clean local

build:
	docker build -t $(IMAGE_NAME) -f $(DOCKERFILE) .
local:
	source venv/bin/activate
	flask run
runf:
	docker run --name $(CONTAINER_NAME) -it $(IMAGE_NAME) blockMesh
run:
	docker run --name $(CONTAINER_NAME) -it $(IMAGE_NAME) 

test:
	docker build -t $(IMAGE_NAME) -f $(DOCKERFILE) .
	docker run --privileged --rm --name $(CONTAINER_NAME) -it $(IMAGE_NAME) pytest -v  $(TESTS_DIR)

clean:
	docker stop $(CONTAINER_NAME) || true
	docker rm $(CONTAINER_NAME) || true

.PHONY: help
help:
	@echo "Usage: make [target]"
	@echo "Targets:"
	@echo "  build        Build the Docker image"
	@echo "  run          Start a shell inside a new container"
	@echo "  test         Run tests inside a new container"
	@echo "  clean        Stop and remove the container"

