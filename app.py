from flask import Flask, jsonify, request
from datetime import datetime
import os
import requests
import phonenumbers
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from flask_cors import CORS
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
CORS(app)

@app.route('/api/compara_datas', methods=['POST'])
def compara_datas():
    dados = request.get_json()
    data1 = datetime.strptime(dados['data1'], '%d/%m/%Y').date()
    data2 = datetime.strptime(dados['data2'], '%d/%m/%Y').date()
    modo = dados['modo']

    if modo == 'diferenca':
        dias_entre_datas = abs((data1 - data2).days)

        response = {
            'result': dias_entre_datas
        }

    elif modo == 'comparacao':
        if data1 > data2:
            maior_ou_menor = '1'
        elif data1 < data2:
            maior_ou_menor = '-1'
        else:
            maior_ou_menor = '0'

        response = {
            'result': maior_ou_menor
        }

    else:
        response = {
            'Erro': 'Modo de operação inválido! Modos aceitos: diferenca ou comparacao'
        }

    return jsonify(response)

@app.route('/api/geolocation', methods=['POST'])
def obter_localizacao():
    dados = request.get_json()
    latitude = dados['latitude']
    longitude = dados['longitude']

    # Valida o formato dos dados enviados
    if valida_formato(latitude, longitude) is True:
        pass
    else:
        response = {
            'Erro': 'Você inseriu dados inválidos, insira apenas coordenadas numéricas.'
        }
        return jsonify(response), 400

    # Utiliza a função validar_dados para verificar a validade das coordenadas inseridas
    if not validar_dados(latitude, longitude):
        response = {
            'Erro': 'Você inseriu coordenadas inválidas.'
        }
        return jsonify(response), 400

    # Utiliza a API da OpenStreetMap para consultar a localização
    url = f'https://nominatim.openstreetmap.org/reverse?format=json&lat={latitude}&lon={longitude}'
    response_url = requests.get(url)
    data = response_url.json()

    # Extrai a cidade, estado e país do response
    endereco = data.get('address', {})
    cidade = endereco.get('city')
    estado = endereco.get('state')
    pais = endereco.get('country')

    response = {
        'cidade': cidade,
        'estado': estado,
        'pais': pais
    }

    return jsonify(response), 200

def valida_formato(latitude, longitude):
    try:
        float(latitude),
        float(longitude)

        return True

    except ValueError:

        return False

def validar_dados(latitude, longitude):
    if latitude is None or longitude is None:
        return False

    if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
        return False

    return True

@app.route('/api/informa_dia_util', methods=['POST'])
def verificar_data():
    dados = request.get_json()
    data_atual = dados['data_atual']
    estado = dados['estado']

    if '-' in data_atual:
        data_atual = datetime.strptime(data_atual, '%Y-%m-%d').strftime('%d/%m/%Y')

    try:
        data_atual = datetime.strptime(data_atual, '%d/%m/%Y')
    except ValueError:
        response = {
            'Erro': 'Você inseriu um data inválida! Por favor, respeite o formato DD/MM/AAAA.'
        }
        return jsonify(response), 400

    quantidade_caracteres_estado = len(estado)

    if quantidade_caracteres_estado > 3:
        response = {
            'Erro': 'Você inseriu a UF de um estado inválida.'
        }
        return jsonify(response), 400

    ano_atual = datetime.now().year

    feriados_nacionais = [
        datetime.strptime(f'01/01/{ano_atual}', '%d/%m/%Y'), # Confraternização Universal
        datetime.strptime(f'20/02/{ano_atual}', '%d/%m/%Y'), # Carnaval
        datetime.strptime(f'21/02/{ano_atual}', '%d/%m/%Y'), # Carnaval
        datetime.strptime(f'07/04/{ano_atual}', '%d/%m/%Y'), # Paixão de Cristo
        datetime.strptime(f'21/04/{ano_atual}', '%d/%m/%Y'), # Tiradentes
        datetime.strptime(f'01/05/{ano_atual}', '%d/%m/%Y'), # Dia do Trabalho
        datetime.strptime(f'08/06/{ano_atual}', '%d/%m/%Y'), # Corpus Christi
        datetime.strptime(f'07/09/{ano_atual}', '%d/%m/%Y'), # Independência do Brasil
        datetime.strptime(f'12/10/{ano_atual}', '%d/%m/%Y'), # Nossa Senhora Aparecida - Padroeira do Brasil
        datetime.strptime(f'02/11/{ano_atual}', '%d/%m/%Y'), # Finados
        datetime.strptime(f'15/11/{ano_atual}', '%d/%m/%Y'), # Proclamação da República
        datetime.strptime(f'25/12/{ano_atual}', '%d/%m/%Y'), # Natal
        datetime.strptime(f'31/12/{ano_atual}', '%d/%m/%Y')  # Véspera do Ano Novo
    ]

    feriados_acre = [
        datetime.strptime(f'20/01/{ano_atual}', '%d/%m/%Y'),  # Dia do Católico
        datetime.strptime(f'25/01/{ano_atual}', '%d/%m/%Y'),  # Dia do Evangélico
        datetime.strptime(f'15/06/{ano_atual}', '%d/%m/%Y'),  # Aniversário do Estado do Acre
        datetime.strptime(f'05/09/{ano_atual}', '%d/%m/%Y'),  # Dia da Amazônia
        datetime.strptime(f'17/11/{ano_atual}', '%d/%m/%Y'),  # Tratado de Petrópolis
    ]

    feriados_alagoas = [
        datetime.strptime(f'24/06/{ano_atual}', '%d/%m/%Y'),  # Dia de São João
        datetime.strptime(f'29/06/{ano_atual}', '%d/%m/%Y'),  # Dia de São Pedro
        datetime.strptime(f'16/09/{ano_atual}', '%d/%m/%Y'),  # Emancipação Política de Alagoas
        datetime.strptime(f'20/11/{ano_atual}', '%d/%m/%Y'),  # Dia da Consciência Negra
    ]

    feriados_amapa = [
        datetime.strptime(f'19/03/{ano_atual}', '%d/%m/%Y'),  # Dia de São José
        datetime.strptime(f'25/07/{ano_atual}', '%d/%m/%Y'),  # Dia de São Tiago
        datetime.strptime(f'05/10/{ano_atual}', '%d/%m/%Y'),  # Criação do Estado do Amapá
        datetime.strptime(f'20/11/{ano_atual}', '%d/%m/%Y'),  # Dia da Consciência Negra
    ]

    feriados_amazonas = [
        datetime.strptime(f'05/09/{ano_atual}', '%d/%m/%Y'),  # Elevação do Amazonas à categoria de província
        datetime.strptime(f'20/11/{ano_atual}', '%d/%m/%Y'),  # Dia da Consciência Negra
        datetime.strptime(f'08/12/{ano_atual}', '%d/%m/%Y'),  # Dia de Nossa Senhora da Conceição
    ]

    feriados_bahia = [
        datetime.strptime(f'02/07/{ano_atual}', '%d/%m/%Y'),  # Independência do Estado da Bahia
    ]

    feriados_ceara = [
        datetime.strptime(f'19/03/{ano_atual}', '%d/%m/%Y'),  # Dia de São José
        datetime.strptime(f'25/03/{ano_atual}', '%d/%m/%Y'),  # Data Magna do Ceará
    ]

    feriados_distrito_federal = [
        datetime.strptime(f'21/04/{ano_atual}', '%d/%m/%Y'),  # Fundação de Brasília
        datetime.strptime(f'30/11/{ano_atual}', '%d/%m/%Y'),  # Dia do Evangélico
    ]

    feriados_espirito_santo = [
        datetime.strptime(f'28/10/{ano_atual}', '%d/%m/%Y'),  # Dia do Servidor Público
    ]

    feriados_maranhao = [
        datetime.strptime(f'28/07/{ano_atual}', '%d/%m/%Y'),  # Dia da Adesão do Maranhão à Independência do Brasil
    ]

    feriados_mato_grosso = [
        datetime.strptime(f'20/11/{ano_atual}', '%d/%m/%Y'),  # Dia da Consciência Negra
    ]

    feriados_mato_grosso_do_sul = [
        datetime.strptime(f'11/10/{ano_atual}', '%d/%m/%Y'),  # Criação do Estado do Mato Grosso do Sul
    ]

    feriados_minas_gerais = [
        datetime.strptime(f'21/04/{ano_atual}', '%d/%m/%Y'),  # Data Magna de Minas Gerais
    ]

    feriados_para = [
        datetime.strptime(f'15/08/{ano_atual}', '%d/%m/%Y'),  # Adesão do Grão-Pará à independência do Brasil
    ]

    feriados_paraiba = [
        datetime.strptime(f'05/08/{ano_atual}', '%d/%m/%Y'),  # Fundação do Estado da Paraíba
    ]

    feriados_pernambuco = [
        datetime.strptime(f'06/03/{ano_atual}', '%d/%m/%Y'),  # Data Magna do Estado de Pernambuco
        datetime.strptime(f'24/06/{ano_atual}', '%d/%m/%Y'),  # Dia de São João
    ]

    feriados_piaui = [
        datetime.strptime(f'13/03/{ano_atual}', '%d/%m/%Y'),  # Dia da Batalha do Jenipapo
        datetime.strptime(f'19/10/{ano_atual}', '%d/%m/%Y'),  # Dia do Piauí
    ]

    feriados_rio_de_janeiro = [
        datetime.strptime(f'23/04/{ano_atual}', '%d/%m/%Y'),  # Dia de São Jorge
        datetime.strptime(f'20/11/{ano_atual}', '%d/%m/%Y'),  # Dia da Consciência Negra
    ]

    feriados_rio_grande_do_norte = [
        datetime.strptime(f'29/06/{ano_atual}', '%d/%m/%Y'),  # Dia de São Pedro
        datetime.strptime(f'03/10/{ano_atual}', '%d/%m/%Y'),  # Mártires de Cunhaú e Uruaçu
    ]

    feriados_rio_grande_do_sul = [
        datetime.strptime(f'20/09/{ano_atual}', '%d/%m/%Y'),  # Revolução Farroupilha (Dia do Gaúcho)
    ]

    feriados_rondonia = [
        datetime.strptime(f'05/10/{ano_atual}', '%d/%m/%Y'),  # Criação de Roraima
    ]

    feriados_santa_catarina = [
        datetime.strptime(f'15/08/{ano_atual}', '%d/%m/%Y'),  # Dia do Estado de Santa Catarina
    ]

    feriados_sao_paulo = [
        datetime.strptime(f'09/07/{ano_atual}', '%d/%m/%Y'),  # Revolução Constitucionalista de 1932
    ]

    feriados_sergipe = [
        datetime.strptime(f'08/07/{ano_atual}', '%d/%m/%Y'),  # Emancipação política de Sergipe
    ]

    feriados_tocantins = [
        datetime.strptime(f'08/09/{ano_atual}', '%d/%m/%Y'),  # Nossa Senhora da Natividade
        datetime.strptime(f'05/10/{ano_atual}', '%d/%m/%Y'),  # Criação de Tocantins
    ]

    if estado == 'AC':
        if data_atual in feriados_acre:
            response = {
                'result': 'Feriado'
            }
            return jsonify(response), 200

    if estado == 'AL':
        if data_atual in feriados_alagoas:
            response = {
                'result': 'Feriado'
            }
            return jsonify(response), 200

    if estado == 'AP':
        if data_atual in feriados_amapa:
            response = {
                'result': 'Feriado'
            }
            return jsonify(response), 200

    if estado == 'AM':
        if data_atual in feriados_amazonas:
            response = {
                'result': 'Feriado'
            }
            return jsonify(response), 200

    if estado == 'BA':
        if data_atual in feriados_bahia:
            response = {
                'result': 'Feriado'
            }
            return jsonify(response), 200

    if estado == 'CE':
        if data_atual in feriados_ceara:
            response = {
                'result': 'Feriado'
            }
            return jsonify(response), 200

    if estado == 'DF':
        if data_atual in feriados_distrito_federal:
            response = {
                'result': 'Feriado'
            }
            return jsonify(response), 200

    if estado == 'ES':
        if data_atual in feriados_espirito_santo:
            response = {
                'result': 'Feriado'
            }
            return jsonify(response), 200

    if estado == 'MA':
        if data_atual in feriados_maranhao:
            response = {
                'result': 'Feriado'
            }
            return jsonify(response), 200

    if estado == 'MT':
        if data_atual in feriados_mato_grosso:
            response = {
                'result': 'Feriado'
            }
            return jsonify(response), 200

    if estado == 'MS':
        if data_atual in feriados_mato_grosso_do_sul:
            response = {
                'result': 'Feriado'
            }
            return jsonify(response), 200

    if estado == 'MG':
        if data_atual in feriados_minas_gerais:
            response = {
                'result': 'Feriado'
            }
            return jsonify(response), 200

    if estado == 'PA':
        if data_atual in feriados_para:
            response = {
                'result': 'Feriado'
            }
            return jsonify(response), 200

    if estado == 'PB':
        if data_atual in feriados_paraiba:
            response = {
                'result': 'Feriado'
            }
            return jsonify(response), 200

    if estado == 'PE':
        if data_atual in feriados_pernambuco:
            response = {
                'result': 'Feriado'
            }
            return jsonify(response), 200

    if estado == 'PI':
        if data_atual in feriados_piaui:
            response = {
                'result': 'Feriado'
            }
            return jsonify(response), 200

    if estado == 'RJ':
        if data_atual in feriados_rio_de_janeiro:
            response = {
                'result': 'Feriado'
            }
            return jsonify(response), 200

    if estado == 'RN':
        if data_atual in feriados_rio_grande_do_norte:
            response = {
                'result': 'Feriado'
            }
            return jsonify(response), 200

    if estado == 'RS':
        if data_atual in feriados_rio_grande_do_sul:
            response = {
                'result': 'Feriado'
            }
            return jsonify(response), 200

    if estado == 'RO':
        if data_atual in feriados_rondonia:
            response = {
                'result': 'Feriado'
            }
            return jsonify(response), 200

    if estado == 'SC':
        if data_atual in feriados_santa_catarina:
            response = {
                'result': 'Feriado'
            }
            return jsonify(response), 200

    if estado == 'SP':
        if data_atual in feriados_sao_paulo:
            response = {
                'result': 'Feriado'
            }
            return jsonify(response), 200

    if estado == 'SE':
        if data_atual in feriados_sergipe:
            response = {
                'result': 'Feriado'
            }
            return jsonify(response), 200

    if estado == 'TO':
        if data_atual in feriados_tocantins:
            response = {
                'result': 'Feriado'
            }
            return jsonify(response), 200

    if estado == 'all':
        pass

    if data_atual.weekday() < 5 and data_atual not in feriados_nacionais:
        response = {
            'result': 'Dia útil'
        }
        return jsonify(response), 200

    elif data_atual in feriados_nacionais:
        response = {
            'result': 'Feriado'
        }
        return jsonify(response), 200

    else:
        response = {
            'result': 'Fim de semana'
        }
        return jsonify(response), 200

@app.route('/api/replace_text', methods=['POST'])
def replace_text():
    dados = request.get_json()
    texto = dados['texto']
    item_para_substituir = dados['item_para_substituir']
    item_substituto = dados['item_substituto']
    parcial = dados['CasoParcialQuantidade']
    modo = dados['modo']

    if modo == 'completo':
        novo_texto = texto.replace(item_para_substituir, item_substituto)

        response = {
            'result': novo_texto
        }
        return jsonify(response), 200

    elif modo == 'parcial':
        novo_texto = texto.replace(item_para_substituir, item_substituto, parcial)

        response = {
            'result': novo_texto
        }
        return jsonify(response), 200

    else:
        response = {
            'Erro': 'Modo de operação inválido! Modos aceitos: completo ou parcial (caso parcial, insira a quantidade em CasoParcialQuantidade.'
        }
        return jsonify(response), 400

def validar_cpf(cpf):
    # Remove pontuação
    cpf = cpf.replace(".", "").replace("-", "")

    # Verifica se todos os caracteres são numéricos
    if not cpf.isdigit():
        return False

    # Verifica se possui 11 dígitos
    if len(cpf) != 11:
        return False

    return True

def validar_cnpj(cnpj):
    # Remove pontuação
    cnpj = cnpj.replace(".", "").replace("-", "").replace("/", "")

    # Verifica se todos os caracteres são numéricos
    if not cnpj.isdigit():
        return False

    # Verifica se possui 14 dígitos
    if len(cnpj) != 14:
        return False

    return True

@app.route('/api/valida_cpf_cnpj', methods=['POST'])
def validar_cpf_cnpj():
    dados = request.json
    documento = dados.get('documento', '')

    # Remove pontuação do documento
    documento = documento.replace('.', '').replace('-', '').replace('/', '')

    if len(documento) == 11:
        resultado = validar_cpf(documento)
    elif len(documento) == 14:
        resultado = validar_cnpj(documento)
    else:
        resultado = False

    # Formato do retorno
    response = {
        "result": resultado
    }

    # Decisor de exibição do response code
    if resultado == True:
        return jsonify(response), 200
    else:
        return jsonify(response), 400

@app.route('/api/valida_telefone_latam', methods=['POST'])
def valida_telefone():
    dados = request.get_json()
    telefone = dados['telefone']

    if not telefone:
        response = {
            'Erro': 'Por favor, preencha o campo telefone com um número válido.'
        }
        return jsonify(response), 400

    if '+' not in telefone:
        telefone = f'+{telefone}'

    try:
        parsed_number = phonenumbers.parse(telefone, None)
        is_valid = phonenumbers.is_valid_number(parsed_number)
        region_code = phonenumbers.region_code_for_number(parsed_number)

        if is_valid and region_code in ('AR', 'BO', 'BR', 'CL', 'CO', 'CR', 'CU', 'DO', 'EC', 'GT', 'HN', 'MX', 'NI', 'PA', 'PY', 'PE', 'PR', 'UY', 'VE'):
            response = {
                'valid': True,
                'regiao': region_code
            }
            return jsonify(response), 200
        else:
            response = {
                'valid': False,
                'regiao': 'Desconhecida'
            }
            return jsonify(response), 200

    except phonenumbers.phonenumberutil.NumberParseException:
        response = {
            'Erro': 'Você inseriu um número inválido!'
        }
        return jsonify(response), 400

@app.route('/api/exchange_rate_tool', methods=['GET'])
def run_exchange_rate_tool():
    options = Options()
    options.add_argument("--headless")
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    specific_version = '114.0.5735.90' #100.0.4896.20
    service = Service(ChromeDriverManager(driver_version=specific_version).install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get("https://dolarhoje.com/")
        wait = WebDriverWait(driver, 20)
        try:
            result = wait.until(EC.presence_of_element_located((By.ID, "nacional")))
        except TimeoutException:
            result = None

        if result:
            current_usd_exchange_rate = result.get_attribute('value')
            response = {'usd_brl_exchange_rate': current_usd_exchange_rate, 'success': True}
            return jsonify(response), 200
        else:
            return jsonify({'error': "Houve um erro ao obter a cotação do dólar.", 'success': False}), 400
    except Exception as e:
        return jsonify({'error': "Houve um erro sistêmico, por favor, tente novamente.", 'success': False}), 500
    finally:
        driver.quit()

@app.route('/api/send_email', methods=['POST'])
def send_email():
    dados = request.get_json()
    nome = dados['nome']
    email = dados['email']
    telefone = dados['telefone']

    subject = 'Formulário do Portfolio'
    body = f'Informações de Contato\n\nNome completo: {nome}\nE-mail: {email}\nTelefone: {telefone}'

    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    smtp_username = 'lucasreinert96@gmail.com'
    smtp_password = 'odzf tcau fcso jsol'

    # Configuração do servidor SMTP
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(smtp_username, smtp_password)

    # Criação do e-mail
    msg = MIMEMultipart()
    msg['From'] = smtp_username
    msg['To'] = 'lucasreinert96@gmail.com'
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    server.sendmail(smtp_username, 'lucasreinert96@gmail.com', msg.as_string())

    server.quit()

    response = {
        'success': True
    }
    return jsonify(response), 201

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)