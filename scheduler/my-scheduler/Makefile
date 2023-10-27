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