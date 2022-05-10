.PHONY: grpc

PROTO_PATH:=./api/v1/hide_and_seek.proto

dependencies:
	@. venv/bin/activate && \
		pip install -r requirements.txt

grpc: | dependencies
	@. venv/bin/activate && \
		mkdir -p ./api/v1 && \
		cp -R ../AIC-server/src/main/proto/v1/hide_and_seek.proto $(PROTO_PATH) && \
		python -m grpc_tools.protoc -I ./api/v1 --python_out=. --grpc_python_out=. hide_and_seek.proto

run: | grpc
	@. venv/bin/activate && \
		python client.py
