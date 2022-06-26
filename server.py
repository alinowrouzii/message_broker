from threading import Thread
import re
import socket


topics = {}


def send_msg_to_subscribers(topicID, msg):

    topic = topics[topicID]
    topic = list(topic)

    # user connection
    for subscriber_conn in topic:
        subscriber_conn.send(f"{topicID}: {msg}".encode())


def unsubscribe_topic(topicID, conn):
    topic = topics[topicID]
    topic = list(topic)

    topic.remove(conn)
    topics[topicID] = topic


def create_topic(topicID):
    topics[topicID] = []
    return True


def add_subscriber_to_topic(topicID, conn):
    
    if topicID not in topics.keys():
        create_topic(topicID)

    topic = topics[topicID]
    topic = list(topic)

    topic.append(conn)
    topics[topicID] = topic
    return True

def handle_publisher_client(new_connection, new_addr, user_msg):
    
    _, topicID, message = user_msg.split(" ")
    
    try:
        send_msg_to_subscribers(topicID=topicID, msg=message)
        new_connection.send(
            f"your message published successfully\n".encode()
        )
    except KeyError:
        new_connection.send(
            f"Topic Does not exist\n".encode()
        )
    except Exception:
        new_connection.send(
            f"Something goes wrong\n".encode()
        )
    
    new_connection.close()


def handle_subscriber_client(new_connection, new_addr, user_msg):
    
    topicsID = user_msg.split(" ")[1:]
    for topicID in topicsID:
        add_subscriber_to_topic(topicID=topicID, conn=new_connection)
    
    new_connection.send(
        f"subscribing on {' '.join(topicsID)}\n".encode()
    )
    
    
    while True:
        user_msg = new_connection.recv(1024).decode()
        user_msg = str(user_msg)
        
        if user_msg.startswith("unsubscribe") and user_msg.split(" ") == 2:
            _, topicID = user_msg.split(" ")
            unsubscribe_topic(topicID=topicID, conn=new_connection)



def handle_client(newConn, addr):
    user_msg = newConn.recv(1024).decode()
    user_msg = str(user_msg)

    if user_msg.startswith("publish"):
        if len(user_msg.split(" ")) == 3:
            handle_publisher_client(newConn, addr, user_msg)
        else:
            newConn.send(
                f"Invalid input!!\nexiting...\n".encode()
            )
            newConn.close()
            return
    
    if user_msg.startswith("subscribe"):
        if len(user_msg.split(" ")) >= 2:
            handle_subscriber_client(newConn, addr, user_msg)
        else:
            newConn.send(
                f"Invalid input!!\nexiting...\n".encode()
            )
            newConn.close()



def runner():
    # next create a socket object
    s = socket.socket()
    print("Socket successfully created")

    port = 12345

    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    s.bind(("", port))
    print("socket binded to %s" % (port))

    # put the socket into listening mode
    s.listen(5)
    print("socket is listening")

    while True:

        # Establish connection with client.
        conn, addr = s.accept()

        address = str(addr[1])

        print("Got connection from", address)
        # send a thank you message to the client. encoding to send byte type.
        
        thread = Thread(
            target=handle_client,
            args=(
                conn,
                address,
            ),
        )
        thread.start()


runner()
