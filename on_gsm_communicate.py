import time
import sys
import serial
import glob

# https://github.com/opennirvana/on-gsm-communicate

class Sms(object):
    def __init__(self, puerto="/dev/ttyUSB0"):
        self.phone = serial.Serial()
        self.phone.port=puerto
        self.phone.baudrate=9600
        self.phone.timeout=9
        self.phone.xonxoff = False
        self.phone.rtscts = False
        self.phone.bytesize = serial.EIGHTBITS
        self.phone.parity = serial.PARITY_NONE
        self.phone.stopbits = serial.STOPBITS_ONE
        self.enviadoOK=[]


    def get_num(self, x):
       return str(''.join(ele for ele in x if str(ele).isdigit()))

    def recept(self, message, recipient):
       time.sleep(0.5)
       #Lo pongo en modo AT para comunicarme
       self.phone.write('AT\r\n')
       time.sleep(0.5)
       #Lo pongo en modo sms
       self.phone.write('AT+CMGF=1\r\n')
       time.sleep(0.5)
       #Seteo el destinatario
       self.phone.write('AT+CMGW="'+recipient+'"\r\n')
       out = ''
       time.sleep(1)
       while self.phone.inWaiting() > 0:
          out += self.phone.read(1)
       if out != '':
          print ">>" + out
       self.phone.write(message)
       self.phone.write('\x1a')
       out = ''
       time.sleep(1)
       while self.phone.inWaiting() > 0:
          out += self.phone.read(1)
       if out != '':
          print ">>" + out
       number = self.get_num(out)
       self.phone.write('AT+CMSS='+number+'\r\n')
       out = ''
       time.sleep(2)
       while self.phone.inWaiting() > 0:
          out += self.phone.read(1)
       if out != '':
          print ">>" + out
       #Es un poco tramposo, aveces el modem no devuelve nada y manda el sms
       #por eso solo verifico si da ERROR y no OK.
       if out.find("ERROR") > -1:
          self.enviadoOK.append(False)
       else:
          self.enviadoOK.append(True)

    def enviados(self):
        return self.enviadoOK

    def sendSMS(self,message,mobileno):
        """Recibe el mensaje y el numero de celular dentro de una lista"""
        try:
            self.phone.open()
            self.phone.flushInput()
            self.phone.flushOutput()
            for row in mobileno:
                time.sleep(0.5)
                mobile = row
                self.recept(message, mobile)
            time.sleep(1)
            #Borra los mensajes guardados desde la pos 1 hasta la 4
            self.phone.write('AT+CMGD=1,4\r\n')
            self.phone.close()
        finally:
            self.phone.close()

