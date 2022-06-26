from threading import Thread
import socket            
import sys


def handle_printing(socket):
    while True:
        received_msg = socket.recv(1024).decode()
        
        if not received_msg:
            break
        
        received_msg = str(received_msg)
        for line in received_msg.splitlines():
            print(f"> {line}")




def runner():
    
    print(sys.argv)
    _, host, port, *user_input = sys.argv
    # Create a socket object
    s = socket.socket()        
    
    try:
        s.connect((host, int(port)))
        # s.connect(('127.0.0.1', 12345))
    except ConnectionRefusedError:
        print("Connection refused")
        return
    except Exception as e:
        print(e)
        print("Some error occured...")
        return
        
    print("client connected to server successfully!")

    
    text = " ".join(user_input)
    s.send(text.encode())
    
    thread = Thread(target = handle_printing, args = (s, ))
    thread.start()
    
    # s.close()
    
runner()


