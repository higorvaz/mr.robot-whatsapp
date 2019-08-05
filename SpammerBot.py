from selenium import webdriver
from time import sleep

from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, UnexpectedAlertPresentException
from selenium.webdriver.common.keys import Keys
from datetime import datetime


def get_txt_box():
    ''' pega o text box para envio de mensagem'''
    txt_msg = driver.find_element_by_xpath('/html/body/div[1]/div/div/div[4]/div/footer/div[1]/div[2]/div/div[2]')
    return txt_msg


def get_wrong_number():
    ''' pega o text box para envio de mensagem'''
    try:
        element = driver.find_element_by_xpath('//div[div/div[@role="button"]]/div[1]')
        return 'inválido' in element.text
    except StaleElementReferenceException:
        try:
            element = driver.find_element_by_xpath('//div[div/div[@role="button"]]/div[1]')
            return 'inválido' in element.text
        except NoSuchElementException:
            return False
    except NoSuchElementException:
        return False


# load Chrome drive
driver = webdriver.Chrome()
driver.get('http://web.whatsapp.com')

# v1.0.2: correcao do encode de leitura e multiplas linhas de mensagem
# v1.0.3: correcao de excecoes no laço de repeticao de envio de mensagem para nao para-la quando der err em um numero.
# v1.1.0: cria um arquivo de log com os erros
# v1.1.1: removidos os tempos de espera e corrigido erro para numero nao existe no whats
# v1.1.2: corrigido erro de alerta de saida da pagina
# v1.1.3: ignorado linhas vazias
# v1.1.4: tratamento do alerta do navegador quando a mensagem nao foi enviada antes do proximo numero ser chamado
# v1.1.5: dicionado hardcoded o DDI do brasil no link e mais logs
print('v1.1.5')

f = open(file='msg.txt', encoding='utf8', mode='r')
msg = f.readlines()
f.close()

print('Please Scan the QR Code and press enter')
input()

e = open(file='log_err.txt', encoding='utf8', mode='a')

# read the list of  phone numbers
f = open('list.txt', 'r')
content = f.readlines()
for i, string in enumerate(content):
    sleep(1)
    try:
        string = string.strip()
        if len(string) == 0:
            continue
        print('https://api.whatsapp.com/send?phone=55' + string)

        while True:
            try:
                driver.get('https://api.whatsapp.com/send?phone=' + string)
                break
            except UnexpectedAlertPresentException:
                alert = driver.switch_to.alert
                print(alert.text)
                alert.dismiss()
                sleep(1)

        button = driver.find_element_by_xpath('//*[@id="action-button"]')
        button.click()
        is_wrong = False
        was_sent = False
        stop_when = 0;
        # continue tentando enquanto nao for numero invalido ou conseguir pegar a caixa de texto
        while not is_wrong and not was_sent:
            stop_when += 1
            if stop_when > 10:
                raise Exception('Too many tries')
            try:
                txt_msg = get_txt_box()

                for message in msg:
                    txt_msg.send_keys(message.replace('\n', ''))
                    txt_msg.send_keys(Keys.SHIFT + Keys.ENTER)
                txt_msg.send_keys(Keys.ENTER)
                was_sent = True
            except NoSuchElementException as err:
                sleep(1)
                is_wrong = get_wrong_number()
        if is_wrong:
            is_wrong = False
            raise Exception('Number is not a whats client')
    except Exception as err:
        exc_type, exc_obj, exc_tb = err.exc_info()
        print(i + 1, string, exc_type, exc_tb.tb_lineno)
        # print(i + 1, string, type(err), err)
        e.write(f'[{datetime.now()}]\t[{i + 1}\t{string}]\t[{type(err)}]\t{err}')

e.close()
print('FIM')