import socket 
ip = '127.0.0.1' 
porta = 5006 
endpoint = (ip,porta) 
buf_size = 1024 
while True:
    try: 
        # creo socket UDP 
        skt = socket.socket (socket.AF_INET, socket.SOCK_DGRAM) 
        skt.bind(endpoint) 
        print("Server in ascolto...") 
        data_bytes, addr = skt.recvfrom(buf_size) 
        print("Connessione da: ", addr) 
        data_str = data_bytes.decode("utf-8") #converto byte in stringa 
        
        if data_str == "frutta":
            data_bytes = bytes("banana","utf-8")
        elif data_str == "verdura":
            data_bytes = bytes("carota","utf-8")
        elif data_str == "carne":
            data_bytes = bytes("pollo","utf-8")
        elif data_str == "fine":
            data_bytes = bytes("fine","utf-8")
        else: 
            data_bytes = bytes("non so","utf-8")

        print ("Ricevuto dal client: ", data_str) 
        skt.sendto(data_bytes,addr) 
        skt.close() 
    except socket.error as e: 
        print("Si è verificato un errore: ", e)