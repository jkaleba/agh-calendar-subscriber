import threading
import time
from datetime import datetime
from concurrent import futures
import grpc
import events_pb2, events_pb2_grpc
from parser import parse_ics

INTERVAL = 3  # seconds between pushes

class EventService(events_pb2_grpc.EventServiceServicer):
    def Manage(self, request_iterator, context):
        print(f"Manage() called!")

        first = next(request_iterator, None)
        if not first or not first.HasField('sub'):
            context.abort(grpc.StatusCode.INVALID_ARGUMENT,
                          "Expected initial SubscriptionRequest")
        sid     = first.sub.subscriber_id
        filters = [f.value for f in first.sub.filters]
        print(f"[Manage] '{sid}' subscribed to types = {filters}")

        def updater():
            for msg in request_iterator:
                if msg.HasField('sub'):
                    new_types = [f.value for f in msg.sub.filters]
                    filters[:] = new_types
                    print(f"[Manage] '{sid}' updated types = {filters}")
        threading.Thread(target=updater, daemon=True).start()

        # every INTERVAL, push the closest event for each type
        while context.is_active():
            now    = datetime.utcnow()
            events = list(parse_ics('plan.ics').values())

            for typ in filters:
                candidates = [e for e in events
                              if e.summary.startswith(f"{typ} -")]
                if not candidates:
                    continue
                next_ev = min(candidates, key=lambda e: e.start)

                ce = events_pb2.ClassEvent(
                    subscription_id=sid,
                    type=events_pb2.EventType.CLASS_ADDED,
                    timestamp=int(now.timestamp() * 1000),
                    uid=next_ev.uid,
                    summary=next_ev.summary,
                    start_time=int(next_ev.start.timestamp() * 1000),
                    end_time=int(next_ev.end.timestamp() * 1000),
                    location=next_ev.location,
                )
                print(f"[dispatch] Sending {typ} next at {next_ev.start} to '{sid}'")
                yield ce

            time.sleep(INTERVAL)

        print(f"[Manage] Stream for '{sid}' closed")
        return


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    events_pb2_grpc.add_EventServiceServicer_to_server(
        EventService(), server)
    server.add_insecure_port('[::]:50052')
    server.start()
    print("gRPC server listening on 50052")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
