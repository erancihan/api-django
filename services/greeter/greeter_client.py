import grpc

from lib import greeter_pb2, greeter_pb2_grpc


if __name__ == "__main__":
    with grpc.insecure_channel("localhost:50051") as channel:
        stub = greeter_pb2_grpc.GreeterStub(channel)

        resp = stub.SayHelloTo(greeter_pb2.HelloRequest(name="nobody"))

        print(f">> {resp.message}")
