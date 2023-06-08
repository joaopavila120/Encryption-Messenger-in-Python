import struct
import socket
import sys
import threading
import socket
from Cryptodome.Cipher import AES
from Cryptodome.PublicKey import RSA
from Cryptodome.Cipher import PKCS1_OAEP

HOST = '192.168.5.13'
PORT = 8000

# Descriptografar mensagem recebida
def descriptografarMensagemRecebida(mensagemRecebida):
    with open('private_key.pem', 'rb') as private_key_file:
        private_key_pem = private_key_file.read()
        private_key = RSA.import_key(private_key_pem)
    
    mensagem_criptografada = mensagemRecebida
    cipher_privada = PKCS1_OAEP.new(private_key) #Cria o objeto de criptografia com a chave privada
    return cipher_privada.decrypt(mensagem_criptografada)

# --- funcoes ---
def handle_client(conn, addr, chavePublica):
    try:
        with open('public_key_joao.pem', 'rb') as public_key_file:
            public_key_pem = public_key_file.read()
            chavePublicaServidor  = RSA.import_key(public_key_pem)
            cipher_public = PKCS1_OAEP.new(chavePublicaServidor)

        #Tratando mensagem recebida
        while True:
            mensagemRecebida = conn.recv(1024)
            
            if len(mensagemRecebida) == 0:
                break
            
            #print(mensagemRecebida) # Mensagem sem descriptografar
            
            msg = descriptografarMensagemRecebida(mensagemRecebida).decode('utf-8')

            print('Cliente:', msg)

            if msg == '0':
                break
            
            reply = input('Servidor: ')
            #criptografar mensagem para cliente
            reply_data = cipher_public.encrypt(bytes(reply, 'utf-8'))
            conn.send(reply_data)
            
            if reply == '0':
                break
            print('Aguardando resposta do cliente')
    
    except Exception as ex:
        print('[DEBUG] addr:', addr, 'Exception:', ex)
    finally:
        conn.close()

def obterChaveCliente():
    with open('public_key_joao.pem', 'rb') as public_key_file:
        public_key_pem = public_key_file.read()
        chavePublicaServidor = RSA.import_key(public_key_pem)
        return PKCS1_OAEP.new(chavePublicaServidor) 
    
def obterChavePrivadaServidor():
    with open('private_key.pem', 'rb') as public_key_file:
        public_key_pem = public_key_file.read()
        return RSA.import_key(public_key_pem)

try:
    # --- criar socket ---
    print('Bem Vindo ao zap de Seg e Auditoria de Sistemas')
    s = socket.socket()

    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # --- atribuir socket ao IP local ---
    print('Conexão estabelecida', (HOST, PORT))
    s.bind((HOST, PORT))

    s.listen(1)

    while True:
        # --- aceitar client ---
        conn, addr = s.accept()

        t = threading.Thread(target=handle_client, args=(conn, addr, obterChavePrivadaServidor()))
        t.start()

except Exception as ex:
    print('Erro:', ex)
except KeyboardInterrupt as ex:
    print('Interrupção do teclado')
except:
    print(sys.exc_info())
finally:
    s.close()