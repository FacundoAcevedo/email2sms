#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 Facundo M. Acevedo <acv2facundo[AT]gmail[DOT]com>
#
# Distributed under terms of the GPLv3+ license.


import imaplib
import email

import logging
import logging.handlers

import re
from on_gsm_communicate import Sms

import ConfigParser
import os.path
import sys

class Email2sms(object):
    def __init__(self):

        self.get_config()
        self.setupLoggin()

        self.sms = Sms(self.rutaUsb)


    def get_config(self):
        """Busca y carga su configuracion"""

        #Busco la config en /etc/email2sms.cfg, si no en donde estoy parado
        if os.path.isfile("/etc/email2sms.cfg"):
            config_archivo = "/etc/email2sms.cfg"

        elif os.path.isfile("email2sms.cfg"):
            config_archivo = "email2sms.cfg"

        else:
            print "Error al obtener el archivo de configuracion..."
            sys.exit()

        config = ConfigParser.ConfigParser()
        config.read([config_archivo])
        #Obtengo los datos
        self.usuario = config.get("Email2sms", "casilla_correo")
        self.clave = config.get("Email2sms", "clave_correo")
        self.ip = config.get("Email2sms", "dominio_correo")
        self.carpeta = config.get("Email2sms", "inbox")
        self.carpetaSmsEnviado = config.get("Email2sms", "carpeta_sms_enviado_OK")
        self.carpetaSmsNoEnviado = config.get("Email2sms", "carpeta_sms_enviado_FAIL")
        self.rutaUsb = config.get("Email2sms", "ruta_usb")
        self.rutaLog = config.get("Email2sms", "archivo_log")


    def setupLoggin(self):
        log_max_tam = 10*1024*1024

        # Set up a specific logger with our desired output level
        my_logger = logging.getLogger('logger')

        my_logger.setLevel(logging.INFO)

        # Add the log message handler to the logger
        #NOTA: backupCount es la cantidad de logs maxima que se tendra antes de
        #empezar a borrar el ultimo log y pisarlo con el posterior(en fecha no en numero
        handler = logging.handlers.RotatingFileHandler(
              "/tmp/email2sms.log", maxBytes=log_max_tam, backupCount=3)
              #self.rutaLog, maxBytes=log_max_tam, backupCount=3)

        my_logger.addHandler(handler)


        self.logger = my_logger


    def moverCorreo(self, uid, ok=True):
        """Mueve el correo segun el estado del envio del sms"""
        if ok:
            carpeta = self.carpetaSmsEnviado
        else:
            carpeta = self.carpetaSmsNoEnviado
        #Copio el mail a la nueva carpeta
        self.mail.uid("copy", uid, carpeta)
        #Marco el viejo correo como Borrado
        self.mail.uid("store",uid,'+FLAGS','(\\Deleted)')
        #Ejecuto el borrado
        self.mail.expunge()


    def validarNumeroCelular(self, numero):
        numero =  str(numero)
        tam = len(numero)

        #Sin 15 ni 011, con 15, con 011, con 01115 con 1115
        tamCorrecto = tam  in [8, 10 , 11 , 12, 13]

        if numero.isdigit() and tamCorrecto:
            return True
        return False


    def enviarSms(self, numeroCelular, mensaje):
        self.logger.info("Enviando SMS a "+ str(numeroCelular))
        self.sms.sendSMS(mensaje, numeroCelular)
        return self.sms.enviados()


    def procesarCorreos(self):
        """"Busca los mails formateados para mandar sms, luego de enviar el sms
        los archiva en otra carpeta"""
        resultados = []
        if not self.conectado:
            return

        for uid, correo in self.emails_raw:
            email_parser = email.message_from_string(correo)
            numerosCelular = email_parser['Subject'].strip()
            destinatarios = self.formatearNumeros(numerosCelular)

            cuerpo = ""

            #formo el cuerpo del correo
            for part in email_parser.walk():
                c_type = part.get_content_type()
                c_disp = part.get('Content-Disposition')

                if c_type == 'text/plain' and c_disp == None:
                    cuerpo = cuerpo + ' ' + part.get_payload()
                else:
                    continue
            cuerpo = self.formatear(cuerpo)


            estado = self.enviarSms(destinatarios, cuerpo)
            print "Estado: ",estado

            #promedio los resultados
            if estado.count(False) > 0:
                self.moverCorreo(uid, False)
            else:
                self.moverCorreo(uid, True)


    def formatearNumeros(self, numeros):
        """Recibe una cadena de numeros seprados por coma y los formatea,
        devuelve una lista con los numeros"""

        #Quito los espacios/+ que haya
        numeros = numeros.replace(" ","")
        numeros = numeros.replace("+","")

        #Separo los numeros, obtengo la lista
        numeros = numeros.split(",")

        return numeros


    def formatear(self, texto):
        """Quita los tags de html, quita acentos y limita a 160 caracteres"""
        t_sin_saltos = texto.replace('\n'," ")
        t_sin_tabs = t_sin_saltos.replace('\r', "")

        #Limpio la cadena de la manera mas HARDCORE que se me ocurre, solo ascii
        patron = "[ -~]"

        texto = ''.join(re.findall(patron, t_sin_tabs))

        return texto[:160]



    def obtenerCorreos(self):
        "Obtiene los correos nuevos ( no vistos )"

        if not self.conectado:
            return

        self.emails_raw = [] #lista de correos en crudo

        #Los obtengo por UID
        result, data = self.mail.uid('search', None, "UNSEEN")
        ids = data[0].split() #data es una lista de ids
        #Descargo los correos
        for unId in ids:
            result, data = self.mail.uid('fetch', unId, "(RFC822)") # fetch the email body (RFC822) for the given ID
            if result == "OK":
                self.emails_raw.append([unId, data[0][1]])
        if len(self.emails_raw) > 0:
            self.logger.info("Correos nuevos: "+str(len(self.emails_raw)))



    def conectar(self):
        self.mail = imaplib.IMAP4_SSL(self.ip)
        self.mail.login(self.usuario, self.clave)
        self.mail.select(self.carpeta)

    def conectado(self):
        if self.mail and self.mail.state in ["AUTH", "SELECTED"]:
            return True
        return False
