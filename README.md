LEEME
=============

## Descripción ##
Email2sms es una aplicación que revisa una casilla de correo buscando correos con un
determinado formato, los descarga y los intenta enviar vía sms, usando un modem 3G.
Según el estado del envío los mueve a una carpeta especifica.

## Configuración ##
El archivo de configuración debe estar en /etc/email2sms.cfg o en el directorio 
donde se encuentre la aplicación, siendo el de /etc/ el principal.
Todos los campos son obligatorios.

Los parámetros carpeta_sms_enviado_OK, carpeta_sms_enviado_FAIL, son las carpetas
en la casilla de correo donde se copiaran los mails, según su estado.

## Uso ##
Agregar a cron la linea:

`* * * * * /usr/local/sbin/email2sms.py`

Los correos deben llegar a la casilla que se configuro, con el siguiente formato:
Asunto: números de celular separados por coma.
Los números pueden escribirse con 54, 011, 11, 15 o sus combinaciones.

Cuerpo: mensaje, se le quitaran los símbolos no ASCII, se quitan los saltos de linea
se truncara en 160 caracteres.

## Nota ##
1. En caso de error en el envío de sms con destinatarios múltiples (sea imposible 
el sms a uno o a todos), el correo se guardara en la carpeta de inválidos sin 
modificaciones.

1. Los adjuntos se obviaran.
