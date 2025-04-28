import socket 
 
ip = '127.0.0.1' 
porta = 5006 
endpoint = (ip,porta) 
buf_size = 1024 
try: 
    # creo socket TCP 
    skt = socket.socket (socket.AF_INET, socket.SOCK_STREAM) 
    skt.bind(endpoint) 
    skt.listen() 
    print("Server in ascolto...") 
    con, addr = skt.accept() 
    print("Connessione da: ", addr) 
    data_bytes = con.recv(buf_size) 
    data_str = data_bytes.decode("utf-8") #converto byte in stringa 
    print ("Ricevuto dal client: ", data_str) 
    con.send(data_bytes) 
    con.close() 
except socket.error as e: 
    print("Si è verificato un errore: ", e) 