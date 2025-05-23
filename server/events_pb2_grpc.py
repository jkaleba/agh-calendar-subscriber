# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

import events_pb2 as events__pb2

GRPC_GENERATED_VERSION = '1.72.0'
GRPC_VERSION = grpc.__version__
_version_not_supported = False

try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True

if _version_not_supported:
    raise RuntimeError(
        f'The grpc package installed is at version {GRPC_VERSION},'
        + f' but the generated code in events_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class EventServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Manage = channel.stream_stream(
                '/aghevents.EventService/Manage',
                request_serializer=events__pb2.ClientMessage.SerializeToString,
                response_deserializer=events__pb2.ClassEvent.FromString,
                _registered_method=True)


class EventServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def Manage(self, request_iterator, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_EventServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Manage': grpc.stream_stream_rpc_method_handler(
                    servicer.Manage,
                    request_deserializer=events__pb2.ClientMessage.FromString,
                    response_serializer=events__pb2.ClassEvent.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'aghevents.EventService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('aghevents.EventService', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class EventService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def Manage(request_iterator,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.stream_stream(
            request_iterator,
            target,
            '/aghevents.EventService/Manage',
            events__pb2.ClientMessage.SerializeToString,
            events__pb2.ClassEvent.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
