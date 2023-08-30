import sys
import pathlib

sys.path.append(str(pathlib.Path(__file__).parent.absolute()))

from . import greeter_pb2, greeter_pb2_grpc  # noqa: E402

__all__ = [greeter_pb2, greeter_pb2_grpc]
