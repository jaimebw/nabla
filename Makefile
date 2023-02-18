foam:
	docker run -it opencfd/openfoam2106-dev
local:
	flask run
test:
	echo "Testing flask"
	docker compose build
	docker compose up
	docker compose down
flask:
	docker compose build
	docker compose up


