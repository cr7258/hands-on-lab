IMAGE_NAME=cr7258/my-scheduler:latest

.PHONY: build
build: build-image push-image

.PHONY: deploy
deploy:
	kubectl apply -f deploy

.PHONY: clean
clean:
	kubectl delete -f deploy

.PHONY: build-image
build-image:
	docker build -t $(IMAGE_NAME) .

.PHONY: push-image
push-image:
	docker push $(IMAGE_NAME)

.PHONY: run
run:
	go run main.go --config=./config/scorebylabel-scheduler-config.yaml

.PHONY: get-config
get-config:
	go run main.go --write-config-to=./config/generate-config.yaml --config=./config/scorebylabel-scheduler-config.yaml

.PHONY: simulator
simulator:
	go run simulator/main.go --config=./simulator/scheduler.yaml