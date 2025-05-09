package org.example;

import io.grpc.ManagedChannel;
import io.grpc.ManagedChannelBuilder;
import io.grpc.stub.StreamObserver;
import org.example.aghevents.EventServiceGrpc;
import org.example.aghevents.ClassEvent;
import org.example.aghevents.ClientMessage;
import org.example.aghevents.Filter;
import org.example.aghevents.SubscriptionRequest;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.IOException;
import java.util.Set;
import java.util.HashSet;
import java.util.concurrent.atomic.AtomicReference;

public class GrpcClient {
    public static void main(String[] args) throws Exception {
        if (args.length < 1) {
            System.err.println("Usage: GrpcClient <subscriberId>");
            System.exit(1);
        }
        String subscriberId = args[0];

        ManagedChannel channel = ManagedChannelBuilder.forAddress("localhost", 50052)
                .usePlaintext()
                .build();
        EventServiceGrpc.EventServiceStub stub = EventServiceGrpc.newStub(channel);

        AtomicReference<StreamObserver<ClientMessage>> reqObsRef = new AtomicReference<>();
        Set<String> subscribedTypes = new HashSet<>();

        StreamObserver<ClassEvent> responseObserver = new StreamObserver<ClassEvent>() {
            @Override public void onNext(ClassEvent ev) {
                System.out.printf("Got %s: %s @ %s → %s%n",
                        ev.getType(), ev.getSummary(),
                        new java.util.Date(ev.getStartTime()),
                        ev.getLocation());
            }
            @Override public void onError(Throwable t)    { t.printStackTrace(); }
            @Override public void onCompleted()           { System.out.println("Stream completed"); }
        };
        StreamObserver<ClientMessage> reqObs = stub.manage(responseObserver);
        reqObsRef.set(reqObs);

        SubscriptionRequest initial = SubscriptionRequest.newBuilder()
                .setSubscriberId(subscriberId)
                .build();
        reqObs.onNext(ClientMessage.newBuilder().setSub(initial).build());

        Thread console = new Thread(() -> {
            BufferedReader reader = new BufferedReader(new InputStreamReader(System.in));
            System.out.println("Available event types:");
            System.out.println("  W    (wykład)");
            System.out.println("  CWL  (ćwiczenia lab)");
            System.out.println("  CWP  (ćwiczenia projektowe)");
            System.out.println("Type one prefix to subscribe, or 'D'+prefix to unsubscribe (e.g. DW):");

            String line;
            try {
                while ((line = reader.readLine()) != null) {
                    String cmd = line.trim().toUpperCase();

                    if (cmd.startsWith("D") && cmd.length() > 1) {
                        String typeToRemove = cmd.substring(1);
                        if (!(typeToRemove.equals("W") || typeToRemove.equals("CWL") || typeToRemove.equals("CWP"))) {
                            System.out.println("Unknown type for unsubscribe: " + typeToRemove);
                            continue;
                        }
                        if (subscribedTypes.remove(typeToRemove)) {
                            SubscriptionRequest.Builder sb = SubscriptionRequest.newBuilder()
                                    .setSubscriberId(subscriberId);
                            for (String t : subscribedTypes) {
                                sb.addFilters(Filter.newBuilder()
                                        .setKey("type")
                                        .setValue(t)
                                        .build());
                            }
                            reqObsRef.get().onNext(
                                    ClientMessage.newBuilder().setSub(sb.build()).build()
                            );
                            System.out.println("→ Unsubscribed from: " + typeToRemove);
                            System.out.println("    Now subscribed to: " + subscribedTypes);
                        } else {
                            System.out.println("Not currently subscribed to: " + typeToRemove);
                        }
                        continue;
                    }

                    String prefix = cmd;
                    if (!(prefix.equals("W") || prefix.equals("CWL") || prefix.equals("CWP"))) {
                        System.out.println("Unknown command/type: " + prefix);
                        continue;
                    }
                    if (!subscribedTypes.add(prefix)) {
                        System.out.println("Already subscribed to: " + prefix);
                        continue;
                    }

                    SubscriptionRequest.Builder sb = SubscriptionRequest.newBuilder()
                            .setSubscriberId(subscriberId);
                    for (String t : subscribedTypes) {
                        sb.addFilters(Filter.newBuilder()
                                .setKey("type")
                                .setValue(t)
                                .build());
                    }
                    reqObsRef.get().onNext(
                            ClientMessage.newBuilder().setSub(sb.build()).build()
                    );
                    System.out.println("→ Now subscribed to: " + subscribedTypes);
                }
            } catch (IOException e) {
                e.printStackTrace();
            }
        }, "console-subscriber");
        console.setDaemon(true);
        console.start();

        Thread.currentThread().join();
    }
}
