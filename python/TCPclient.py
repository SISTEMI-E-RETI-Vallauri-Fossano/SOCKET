import socket 
ip = '127.0.0.1' 
porta = 5006 
endpoint = (ip,porta) 
buf_size = 1024 
msg = bytes("Hello World","utf-8") #converte stringa in byte 
try: 
    # creo socket TCP 
    skt = socket.socket (socket.AF_INET, socket.SOCK_STREAM) 
    skt.connect(endpoint) 
    skt.send(msg) 
    #attendo risposta dal server 
    data_bytes = skt.recv(buf_size) 
    data_str = data_bytes.decode("utf-8") #converto byte in stringa 
    print ("Risposta: ", data_str) 
    skt.close 
except socket.error as e: 
    print("Si è verificato un errore: ", e)