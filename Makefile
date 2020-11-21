build:
	docker build -t jzhao2k19/paypaya:latest .
run: build
	docker run -p 8080:8080 jzhao2k19/paypaya:latest
push: build
	docker tag jzhao2k19/paypaya:latest gcr.io/paypaya/webhook
	docker push gcr.io/paypaya/webhook