foam:
	docker run -it opencfd/openfoam2106-dev
test:
	echo "Testing flask"
	docker compose build
	docker compose up
	docker compose down
flask:
	echo "Running flask"
	grep -q "ENTRYPOINT [\"pytest\"]" Dockerfile && \
		sed -i 's/ENTRYPOINT \[ "pytest" \]/ENTRYPOINT [ "python3" ]/g' Dockerfile || :
	#grep -q "CMD [\"tests\"]" Dockerfile && \
	#	sed -i 's/CMD \[ "tests" \]/CMD [ "app.py" ]/g' Dockerfile || :
#	docker-compose build
#	docker-compose up



