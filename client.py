import socket
import sys
import threading
from Cryptodome.PublicKey import RSA
from Cryptodome.Cipher import PKCS1_OAEP
from Cryptodome.Cipher import AES
from Cryptodome.PublicKey import RSA
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QTextEdit, QPushButton

HOST = '192.168.5.13'
PORT = 8000

#monta o front
class Chat(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Welcome to the python whatsapp')
        self.setGeometry(100, 100, 400, 400)

        self.message_history = QTextEdit(self)
        self.message_history.setGeometry(20, 20, 360, 260)
        self.message_history.setReadOnly(True)

        self.text_edit = QTextEdit(self)
        self.text_edit.setGeometry(20, 290, 260, 80)

        self.send_button = QPushButton('Send', self)
        self.send_button.setGeometry(300, 290, 80, 30)
        self.send_button.clicked.connect(self.enviar_mensagem)

        self.disconnect_button = QPushButton('Disconnect', self)
        self.disconnect_button.setGeometry(300, 330, 80, 30)
        self.disconnect_button.clicked.connect(self.disconnect)

        self.s = None

        self.conectar_servidor()

        t = threading.Thread(target=self.receber_mensagem)
        t.start()

    def conectar_servidor(self):
        try:
            with open('public_key_julio.pem', 'rb') as public_key_file:
                public_key_pem = public_key_file.read()
                chavePublicaServidor = RSA.import_key(public_key_pem)
                self.cipher_public = PKCS1_OAEP.new(chavePublicaServidor)

            print('Bem-vindo ao zap de seg e auditoria de sistemas')

            self.s = socket.socket()
            print('Conexão estabelecida!', (HOST, PORT))
            self.s.connect((HOST, PORT))

        except Exception as ex:
            print('Erro:', ex)
            sys.exit()

    def receber_mensagem(self):
        try:
            while True:
                msg = self.s.recv(1024)
                print(msg)
                msg = self.descriptografarMensagemRecebida(msg)

                if len(msg) == 0:
                    break

                self.message_history.append('Server: ' + msg.decode('utf-8'))
        except Exception as ex:
            print('Erro ao receber mensagens:', ex)
        finally:
            self.s.close()

    #funcao que descriptografa
    def descriptografarMensagemRecebida(self, mensagemRecebida):
        with open('private_key.pem', 'rb') as private_key_file:
            private_key_pem = private_key_file.read()
            private_key = RSA.import_key(private_key_pem)

        mensagem_criptografada = mensagemRecebida
        cipher_privada = PKCS1_OAEP.new(private_key)

        return cipher_privada.decrypt(mensagem_criptografada)

    #envia e criptografa
    def enviar_mensagem(self):
        msg = self.text_edit.toPlainText()
        #criptografa
        encrypted_msg = self.cipher_public.encrypt(bytes(msg, 'utf-8'))

        print(encrypted_msg) #mensagem criptogr

        self.s.send(encrypted_msg)
        self.message_history.append('You: ' + msg)
        self.text_edit.clear()

    def disconnect(self):
        self.s.close()
        self.close()

#inicializa a janela
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Chat()
    window.show()
    sys.exit(app.exec_())
