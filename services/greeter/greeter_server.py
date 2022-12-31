import grpc

from lib import greeter_pb2, greeter_pb2_grpc


class Servicer(greeter_pb2_grpc.GreeterServicer):
    def SayHelloTo(self, request, context):
        return greeter_pb2.HelloReply(message=f"Hello, {request.name}")


if __name__ == "__main__":
    from concurrent import futures

    port = 50051

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    greeter_pb2_grpc.add_GreeterServicer_to_server(Servicer(), server)

    server.add_insecure_port(f"[::]:{port}")
    server.start()
    print(f"Server started, listening on [::]:{port}")
    server.wait_for_termination()
