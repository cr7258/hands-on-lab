BUILD_NUM=$(shell cat ./properties.json | jq -r ".build_num")
ES_VERSION=$(shell cat ./properties.json | jq -r ".es_version")
APP_NAME=$(shell cat ./properties.json | jq -r ".app_name")

# elastiflix-dotnet-login and elastiflix-dotnet-login-elastic-auto are built with docker buildx

CONTAINERS = python-favorite javascript-client node-server movie-data-loader go-favorite redis java-favorite
CONTAINERS_ELASTIC = python-favorite-elastic-manual javascript-client-elastic-manual node-server-elastic-manual go-favorite-elastic-manual java-favorite-elastic-manual java-favorite-elastic-auto
CONTAINERS_OTEL = python-favorite-otel-auto python-favorite-otel-manual node-server-otel-auto node-server-otel-manual go-favorite-otel-manual java-favorite-otel-manual java-favorite-otel-auto

docker_build: check-docker-env
	echo "Building docker images"
	for container in ${CONTAINERS}; do\
	    echo Building container: docker.elastic.co/demos/workshop/observability/$(APP_NAME)-$$container:$(ES_VERSION)-$(BUILD_NUM); \
		docker build --platform linux/amd64 --build-arg ES_VERSION=$(VERSION) ./$$container -t docker.elastic.co/demos/workshop/observability/$(APP_NAME)-$$container:$(ES_VERSION)-$(BUILD_NUM);\
	done\

	docker buildx build --push --platform linux/arm64/v8,linux/amd64 -t docker.elastic.co/demos/workshop/observability/elastiflix-dotnet-login:$(ES_VERSION)-$(BUILD_NUM) ./dotnet-login

docker_build_elastic: check-docker-env
	echo "Building docker images"
	for container in ${CONTAINERS_ELASTIC}; do\
	    echo Building container: docker.elastic.co/demos/workshop/observability/$(APP_NAME)-$$container:$(ES_VERSION)-$(BUILD_NUM); \
		docker build --platform linux/amd64 --build-arg ES_VERSION=$(VERSION) ./$$container -t docker.elastic.co/demos/workshop/observability/$(APP_NAME)-$$container:$(ES_VERSION)-$(BUILD_NUM);\
	done\

	docker buildx build --push --platform linux/arm64/v8,linux/amd64 -t docker.elastic.co/demos/workshop/observability/elastiflix-dotnet-login-elastic-auto:$(ES_VERSION)-$(BUILD_NUM) ./dotnet-login-elastic-auto

	
docker_build_otel: check-docker-env
	echo "Building docker images"
	for container in ${CONTAINERS_OTEL}; do\
	    echo Building container: docker.elastic.co/demos/workshop/observability/$(APP_NAME)-$$container:$(ES_VERSION)-$(BUILD_NUM); \
		docker build --platform linux/amd64 --build-arg ES_VERSION=$(VERSION) ./$$container -t docker.elastic.co/demos/workshop/observability/$(APP_NAME)-$$container:$(ES_VERSION)-$(BUILD_NUM);\
	done\

	docker buildx build --push --platform linux/arm64/v8,linux/amd64 -t docker.elastic.co/demos/workshop/observability/elastiflix-dotnet-login-otel-auto:$(ES_VERSION)-$(BUILD_NUM) ./dotnet-login-otel-auto

docker_push: check-docker-env
	@echo "Pushing docker images"
	@for container in ${CONTAINERS}; do\
	    echo Pushing container: docker.elastic.co/demos/workshop/observability/$(APP_NAME)-$$container:$(ES_VERSION)-$(BUILD_NUM); \
		docker push docker.elastic.co/demos/workshop/observability/$(APP_NAME)-$$container:$(ES_VERSION)-$(BUILD_NUM);\
	done\

docker_push_elastic: check-docker-env
	@echo "Pushing docker images"
	@for container in ${CONTAINERS_ELASTIC}; do\
	    echo Pushing container: docker.elastic.co/demos/workshop/observability/$(APP_NAME)-$$container:$(ES_VERSION)-$(BUILD_NUM); \
		docker push docker.elastic.co/demos/workshop/observability/$(APP_NAME)-$$container:$(ES_VERSION)-$(BUILD_NUM);\
	done\

docker_push_otel: check-docker-env
	@echo "Pushing docker images"
	@for container in ${CONTAINERS_OTEL}; do\
	    echo Pushing container: docker.elastic.co/demos/workshop/observability/$(APP_NAME)-$$container:$(ES_VERSION)-$(BUILD_NUM); \
		docker push docker.elastic.co/demos/workshop/observability/$(APP_NAME)-$$container:$(ES_VERSION)-$(BUILD_NUM);\
	done\

check-docker-env:
ifeq (, $(shell which docker))
	$(error "No docker installed")
endif
