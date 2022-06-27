from threading import Thread
import re
import socket
import signal
import time
import multiprocessing as mp

topics = {}

def timeout(func, args = (), kwds = {}, timeout = 1, default = None):
    pool = mp.Pool(processes = 1)
    result = pool.apply_async(func, args = args, kwds = kwds)
    try:
        val = result.get(timeout = timeout)
    except mp.TimeoutError:
        pool.terminate()
        raise Exception
    else:
        pool.close()
        pool.join()
        return val


def send_ping(conn):
    # server sends ping and wait for subscriber to wait for PONG response
    conn.send(f"PING".encode())
    print("PING sent to conn")
    
    while True:
        user_msg = conn.recv(1024).decode()
        user_msg = str(user_msg)
        
        if user_msg == "PONG":
            print("> PONG")
            break


def unsubscribe_topics(conn):
    pass
    for topicID in topics.keys():
        unsubscribe_topic(topicID=topicID, conn=conn)



    
    
def handle_ping(conn):
    while True:
        # Send pingmessage to subscriber every 10 seconds
        time.sleep(4)
        try:
            # wait for subscriber to response to PING message
            # If subscriber did not any response in 10 seconds, timeout will occur
            timeout(send_ping, args = (conn,), timeout = 5, default = '')
        except Exception as e:
            print(e)
            # close the socket connection
            conn.close()
            unsubscribe_topics(conn)
            print("timeout occured...")
            break
    
def send_msg_to_subscribers(topicID, msg):

    topic = topics[topicID]
    topic = list(topic)

    # user connection
    for subscriber_conn in topic:
        subscriber_conn.send(f"{topicID}: {msg}".encode())


def unsubscribe_topic(topicID, conn):
    topic = topics[topicID]
    topic = list(topic)
    try:
        topic.remove(conn)
        topics[topicID] = topic
    except ValueError:
        pass
    


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
    except Exception as e:
        print("eeee", e)
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
            client_ping_handler = Thread(
                target=handle_ping,
                args=(
                    newConn,
                )
            )
            client_ping_handler.start()
            
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
        
        client_handler = Thread(
            target=handle_client,
            args=(
                conn,
                address,
            ),
        )
        client_handler.start()


runner()
