import socket
import select

HEADER_LENGTH = 3   #Header will be used to specify the length of the message received
IP  = socket.gethostname()
PORT = 2000

email_list = ["trinity"]
password_list = ["college"]
coef_authorization = 0
#This function returns a message received in the format: header, message_body- will be called further down.
def receive_message (client_socket):
    try:
        message_header = client_socket.recv(HEADER_LENGTH)
        message_length = int(message_header.decode("utf-8"))
        return {"header": message_header, 
                "data": client_socket.recv(message_length).decode("utf-8")}
    except:
        return False
def set_up():
    # Welcome & Setup
    print("\nWelcome to Group 7 Quarantine Monitor!\n")
    set_up = input("Do you want to set up a new patient (Y/N): ")
    while set_up != 'Y' and set_up != 'N':
        print("Invalid command!")
        set_up = input("Do you want to set up a new patient (Y/N): ")  
    while set_up == 'Y':
        new_email = input('Enter a new Email-adress: ')
        new_password = input('Enter the password: ')
        if new_email in email_list:
            print('Email already registered. ')
            del new_email, new_password
        else: 
            email_list.append(new_email)
            password_list.append(new_password)
            print("New user", new_email, "setup successful! ")
            del new_email, new_password
        set_up = input("Do you want to set up a new patient (Y/N): ")
        while set_up != 'Y' and set_up != 'N':
            print("Invalid command!")
            set_up = input("Do you want to set up a new patient (Y/N): ")      
set_up()            
def authorize ():
    # Check log in / give access to user
    print("Checking Authorization... ")
    trur_message = 'TRUE'.encode("utf-8")
    false_message = 'FALSE'.encode("utf-8")
    while True:
        try:    
            UP_header = client_socket.recv(HEADER_LENGTH).decode("utf-8")
        except: 
            continue
        break
    email_pass_packet = client_socket.recv(int(UP_header)).decode("utf-8")
    email_pass = email_pass_packet.split(',') #[0] will be the username, [1] will be the password
    print(email_pass[0], email_pass[1])
    # Authorization
    while True:
        if email_pass[0] in email_list:
            index = email_list.index(email_pass[0])
            if email_pass[1] == password_list[index]:
                print('Passed Authorization. Currently connected with ->', email_pass[0])
                client_socket.send(f"{len(trur_message):<{HEADER_LENGTH}}".encode("utf-8")+ 'TRUE'.encode("utf-8"))
                break
            else: 
                client_socket.send(f"{len(false_message):<{HEADER_LENGTH}}".encode("utf-8")+ 'FALSE'.encode("utf-8"))
                while True:
                    try:    
                        UP_header = client_socket.recv(HEADER_LENGTH)
                    except: 
                        continue
                    break
                email_pass_packet = client_socket.recv(int(UP_header.decode("utf-8"))).decode("utf-8")
                email_pass = email_pass_packet.split(',') #[0] will be the username, [1] will be the password
                print(email_pass[0], email_pass[1])
        else:

            client_socket.send(f"{len(false_message):<{HEADER_LENGTH}}".encode("utf-8") + 'FALSE'.encode("utf-8"))
            while True:
                try:    
                    UP_header = client_socket.recv(HEADER_LENGTH)
                except: 
                    continue
                break
            email_pass_packet = client_socket.recv(int(UP_header.decode("utf-8"))).decode("utf-8")
            email_pass = email_pass_packet.split(',') #[0] will be the username, [1] will be the password
            print(email_pass[0], email_pass[1])

#Set up the server socket details:
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setblocking(False)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #Not really sure if this line is necessary.
server_socket.bind((IP, PORT))
server_socket.listen()   #Might be able to limit the number of clients by specifying a number here

# Sockets from which we expect to read
sockets_list = [server_socket]
# Sockets to which we expect to write
outputs = [ ]

#This is a clients dictionary (key/value pair)
clients = {}
timeout=20  #this is the time for which the server waits for new connection

print("Waiting for incoming connections...")

while True:
    read_sockets, write_sockets, exception_sockets = select.select(sockets_list, outputs, sockets_list,timeout)
    for notified_socket in read_sockets:
        if notified_socket == server_socket:
            client_socket, client_address = server_socket.accept()
            user = receive_message(client_socket)
            print(f"In coming connection with username: {user['data']}")
            if coef_authorization == 0: 
                authorize()         # This is a loop, can be infinity
                coef_authorization = coef_authorization + 1
            user_id = user['data']#The patient id
            sockets_list.append(client_socket)
            clients[client_socket] = user 
            print(f"Accepted new connection from {client_address[0]}:{client_address[1]} username:{user['data']}")
            welcome_message = ("You are connected - stand by for advice.").encode("utf-8")
            welcome_header = f"{len(welcome_message):<{HEADER_LENGTH}}".encode("utf-8")
            client_socket.send(welcome_header + welcome_message)

        else:
            try:
                message = receive_message(notified_socket)
                user = clients[notified_socket]
                print(f"Received from {user['data']}: {message['data']}")

            except:
                print(f"Closed connection from {clients[notified_socket]['data']}")
                sockets_list.remove(notified_socket)
                del clients[notified_socket]
                #continue

    
    #Now print out a list of connected patients:
    print("The clients currently connected are:")
    for eachClient in clients:
        print(clients[eachClient]['data']),

    #See what the doctor wants to do next:
    options = input(f"Enter a patient name to send advice or enter 's' to stand-by for more connections: > ")
    while (options != 's'):
        if options == 'p':
            print("The clients currently connected are:")
            for eachClient in clients:
                print(clients[eachClient]['data']),
        else:
            patientFound = False
            for eachClient in clients:
                if clients[eachClient]['data'] == options:
                    patientFound = True
                    adviceMessage = input(f"Enter advice for {clients[eachClient]['data']}: > ")
                    adviceMessage = adviceMessage.encode("utf-8")
                    adviceMessage_header = f"{len(adviceMessage):<{HEADER_LENGTH}}".encode("utf-8")

                    try:
                        eachClient.send(adviceMessage_header + adviceMessage)
                    except:
                        print("Error sending advice to the patient.")

            if not patientFound:
                print("Unable to find patient. Please try again.")

        options = input(f"Enter patient name, 's' to stand-by for more connections or 'p' to print the list again: > ")
