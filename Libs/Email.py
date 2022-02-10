from O365 import Message
from smtplib import *
from Libs.Logs import *
from Libs.AppConfig import *
from datetime import *

log = Logs.RetornaLog("--ManipulaEmail--")
#Instancia o objeto para retornar os dados do json de configuração
json = appConfig()

log.info('Abrindo configurações de e-mail')
class Email():
    def __init__(self):
        log.info('Colentando informações da conta')
        self.SMTP = json.retorna_smtp_email()
        self.porta = json.retorna_porta_email()
        self.usuario = json.retorna_usuario_email()
        self.senha = json.retorna_senha_email()

    def envia_email(self, assunto, email, destinatarios:list):
        log.info('Gerando e-mail')
        lista_emails =''
        for d in destinatarios:
            if not d == destinatarios[-1]:
                lista_emails += d + ';'
            else:
                lista_emails += d
        try:
            
            headers = {
                'Content-Type': 'text/html; charset=utf-8',
                'Content-Disposition': 'inline',
                'Content-Transfer-Encoding': '8bit',
                'From': self.usuario,
                'To': lista_emails,
                'Date': datetime.now().strftime('%a, %d %b %Y  %H:%M:%S %Z'),
                'X-Mailer': 'python',
                'Subject': assunto
            }
            msg = ''
            for key, value in headers.items():
                msg += "%s: %s\n" % (key, value)

            # add contents
            msg += "\n%s\n" % (email)

            mailserver = SMTP(self.SMTP, self.porta)
            mailserver.ehlo()
            mailserver.starttls()
            mailserver.login(self.usuario, self.senha)
            log.info(f'Enviando e-mail para: {lista_emails}')
            mailserver.sendmail(self.usuario, lista_emails, msg.encode("utf-8"))
            log.info('E-mail enviado com sucesso')
            mailserver.quit()
        except SMTPResponseException as e:
            log.error(f'Algum problema na transmissão do e-mail: {e.errno}')



