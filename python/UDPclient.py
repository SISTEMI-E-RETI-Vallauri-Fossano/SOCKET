# import art
import socket 
 
ip = '10.0.100.76' #ip del prof 
ip = '10.0.102.158' #ip di mase

porta = 5006 
endpoint = (ip,porta) 
buf_size = 1024 
message = ""
# for i in range(1, 10):
#     message+="Ciao"
msg = bytes("Hello World"+message,"utf-8") #converte stringa in byte 
try: 
    # creo socket UDP 
    skt = socket.socket (socket.AF_INET, socket.SOCK_DGRAM) 
    skt.connect(endpoint) 
    skt.sendto(msg,endpoint) 
    #attendo risposta dal server 
    data_bytes, addr = skt.recvfrom(buf_size) 
    data_str = data_bytes.decode("utf-8") #converto byte in stringa 
    print ("Risposta: ", data_str) 
    skt.close 
except socket.error as e: 
    print("Si è verificato un errore: ", e)