

"""
FUNÇÕES AUX

"""

import requests
import pandas as pd
import json
def prepare_url_parameters_(params):
    """
    Transforma um dicionário de parâmetros em uma string formatada para ser usada em requisições da API do Pipedrive.

    Parâmetros:
    - params (dict): Dicionário contendo os parâmetros que serão convertidos para a URL.

    Retorna:
    - str: String formatada para ser usada em uma query de URL.
    """
    if params is not None:
        param_str = "&".join([f"{key}={value}" for key, value in params.items() if value is not None])
        return param_str
    return ""

def get_all_(url):
    """
    Executa uma solicitação GET para a URL do Pipedrive, baixa todas as páginas e retorna um DataFrame com o resultado.

    Parâmetros:
    - url (str): URL do Pipedrive para obter informações das bases.

    Retorna:
    pd.DataFrame: Um DataFrame contendo o resultado das páginas.
    """
    pages = []
    page = requests.get(url).json()

    if page.get('additional_data', {}).get('pagination', {}).get('more_items_in_collection'):
        if 'limit=500' in url:
            pages.append(pd.DataFrame(page['data']))

            while page['additional_data']['pagination']['more_items_in_collection']:
                next_start = page['additional_data']['pagination']['next_start']
                next_url = url.replace('start=0', f'start={next_start}')
                page = requests.get(next_url).json()

                if 'data' in page:
                    pages.append(pd.DataFrame(page['data']))

            return pd.concat(pages, ignore_index=True)
        else:
            return pd.DataFrame(page['data'])
    else:
        return pd.DataFrame(page['data'])


def check_api_token(api_token):
    """
    Verificação de API Token
    Função interna para verificar o API Token.

    Parâmetros:
    api_token (str): Para validar suas solicitações, você precisará do seu api_token - isso significa que nosso sistema precisará saber quem você é e ser capaz de conectar todas as ações que você faz com a conta da Pipedrive escolhida. 
    Tenha em mente que um usuário tem um api_token diferente para cada empresa. Acesse o seguinte link para mais informações:
    https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference

    Retorna:
    str: O API token se for válido, caso contrário, lança um erro.


    exemplo:
    try:
        print(check_api_token("sjdfsanm23423"))
    except ValueError as e:
        print(e)
    """

    if api_token is None:
        raise ValueError(
            "Por favor, o campo api_token é obrigatório. Para mais informações, acesse <https://pipedrive.readme.io/docs/how-to-find-the-api-token>"
        )
    else:
        return api_token


def clear_list(data):
    """
    Remove campos com valor None de um dicionário.

    Parâmetros:
    data (dict): Dicionário que deseja remover os campos com valor None.

    Retorna:
    dict: Um dicionário sem os campos com valor None.
    # Exemplo de uso:
        example_data = {
            'field1': 123,
            'field2': None,
            'field3': "name"
        }
    """
    keys_to_remove = [key for key, value in data.items() if value is None]

    for key in keys_to_remove:
        del data[key]

    if len(data) == 0:
        return None
    else:
        return data



# FUNÇÕES API
def activities_add(subject, type, done=None, due_date=None, due_time=None, duration=None, user_id=None, deal_id=None, 
                   person_id=None, participants=None, org_id=None, note=None, api_token=None, 
                   company_domain='api', return_type='complete'):
    """
    Adiciona uma atividade no Pipedrive.

    Parâmetros:
    - subject (str): Título da atividade.
    - done (int): Se a atividade foi concluída ou não. 0 = Não concluída, 1 = Concluída.
    - type (str): Tipo da atividade, correlacionado com a string chave de ActivityTypes.
    - due_date (str): Data de vencimento da atividade. Formato: YYYY-MM-DD.
    - due_time (str): Hora de vencimento da atividade no formato UTC. Formato: HH:MM.
    - duration (str): Duração da atividade. Formato: HH:MM.
    - user_id (int): ID do usuário ao qual a atividade será atribuída. Se omitido, será atribuída ao usuário autorizado.
    - deal_id (int): ID do negócio ao qual a atividade será associada.
    - person_id (int): ID da pessoa ao qual a atividade será associada.
    - participants (list): Lista de múltiplas pessoas associadas a essa atividade. Deve estar no formato JSON.
    - org_id (int): ID da organização à qual a atividade será associada.
    - note (str): Nota da atividade no formato HTML.
    - api_token (str): Token da API para validar as solicitações.
    - company_domain (str): Domínio da empresa no Pipedrive.
    - return_type (str): Tipo de retorno esperado. 'complete' retorna o objeto de resposta completo; 'boolean' retorna True ou False.

    Retorna:
    dict ou bool: Retorna o objeto de resposta completo por padrão, ou booleano se 'boolean' for especificado.

    # Exemplo de uso:
    try:
        result = activities_add(
            subject='Exemplo de Atividade',
            type='call',
            api_token='seu_token_aqui',
            company_domain='sua_empresa'
        )
        print(result)
    except ValueError as e:
        print(e)
    """
    api_token = check_api_token(api_token)
    
    url = f'https://{company_domain}.pipedrive.com/v1/activities'
    
    body = {
        'subject': subject,
        'done': done,
        'type': type,
        'due_date': due_date,
        'due_time': due_time,
        'duration': duration,
        'user_id': user_id,
        'deal_id': deal_id,
        'person_id': person_id,
        'participants': participants,
        'org_id': org_id,
        'note': note
    }
    
    body = clear_list(body)
    
    headers = {'Content-Type': 'application/json'}
    params = {'api_token': api_token}
    
    response = requests.post(url, json=body, headers=headers, params=params)
    
    if return_type == 'boolean':
        return response.status_code in [200, 201]
    else:
        return response.json()


def activities_delete(id, api_token=None, company_domain='api', return_type='complete'):
    """
    Exclui uma atividade no Pipedrive.

    Parâmetros:
    - id (str): ID da atividade a ser excluída.
    - api_token (str): Token da API necessário para validar as solicitações.
    - company_domain (str): Domínio da empresa no Pipedrive.
    - return_type (str): Tipo de retorno esperado. 'complete' retorna o objeto de resposta completo; 'boolean' retorna True ou False.

    Retorna:
    dict ou bool: Retorna o objeto de resposta completo por padrão, ou booleano se 'boolean' for especificado.

    exemplo de uso:
    try:
        result = activities_delete(
            id='12345',
            api_token='seu_token_aqui',
            company_domain='sua_empresa',
            return_type='boolean'  # Pode ser 'complete' ou 'boolean'
        )
        print(result)  # Se 'boolean', retorna True ou False
    except ValueError as e:
        print(e)
    """
    api_token = check_api_token(api_token)

    url = f'https://{company_domain}.pipedrive.com/v1/activities/{id}'
    params = {'api_token': api_token}

    response = requests.delete(url, params=params)

    if return_type == 'boolean':
        return response.status_code in [200, 201]
    else:
        return response.json()
    



def activities_delete_multiple(ids, api_token=None, company_domain='api', return_type='complete'):
    """
    Exclui múltiplas atividades em massa no Pipedrive.

    Parâmetros:
    - ids (str): IDs separados por vírgula que serão excluídos.
    - api_token (str): Token da API necessário para validar as solicitações. Um usuário tem um token diferente para cada empresa.
      Para mais informações: <https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference>
    - company_domain (str): Domínio da empresa no Pipedrive. Para mais informações: <https://pipedrive.readme.io/docs/how-to-get-the-company-domain>
    - return_type (str): Tipo de retorno esperado. 'complete' retorna o objeto de resposta completo; 'boolean' retorna True ou False.

    Retorna:
    dict ou bool: Retorna o objeto de resposta completo por padrão, ou booleano se 'boolean' for especificado.

    Exemplo de uso:
    activities_delete_multiple(ids='12345,67890', api_token='seu_token_aqui', company_domain='sua_empresa')
    """
    api_token = check_api_token(api_token)

    url = f'https://{company_domain}.pipedrive.com/v1/activities'
    params = {'api_token': api_token}
    body = {'ids': ids}

    response = requests.delete(url, params=params, json=body)

    if return_type == 'boolean':
        return response.status_code in [200, 201]
    else:
        return response.json()

def activities_get(id, api_token=None, company_domain='api'):
    """
    Função para obter detalhes de uma atividade do Pipedrive.

    Parâmetros:
    - id (str): ID da atividade.
    - api_token (str): Token de API para validar as requisições. Para mais informações: 
      https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference
    - company_domain (str): Domínio da empresa. Para mais informações: 
      https://pipedrive.readme.io/docs/how-to-get-the-company-domain

    Retorna:
    - pd.DataFrame: Um DataFrame contendo os detalhes da atividade.
    """
    api_token = check_api_token(api_token)
    
    url = f'https://{company_domain}.pipedrive.com/v1/activities/{id}?api_token={api_token}'
    
    return get_all_(url)



def activities_get_all(user_id=None, filter_id=None, type=None, start=None, limit=None, 
                       start_date=None, end_date=None, done=None, api_token=None, 
                       company_domain='api'):
    """
    Obtém todas as atividades atribuídas a um usuário específico no Pipedrive.

    Parâmetros:
    - user_id (int, opcional): ID do usuário cujas atividades serão buscadas. Se omitido, será usado o usuário associado ao token da API. Se 0, busca as atividades de todos os usuários da empresa, com base nos conjuntos de permissões.
    - filter_id (int, opcional): ID do filtro a ser usado (limita os resultados quando usado junto com o parâmetro user_id).
    - type (str, opcional): Tipo de atividade, pode ser um tipo ou múltiplos tipos separados por vírgula.
    - start (int, opcional): Início da paginação.
    - limit (int, opcional): Itens exibidos por página.
    - start_date (str, opcional): Data a partir da qual as atividades serão buscadas (formato YYYY-MM-DD).
    - end_date (str, opcional): Data até a qual as atividades serão buscadas (formato YYYY-MM-DD).
    - done (int, opcional): Se a atividade está concluída ou não. 0 = Não concluída, 1 = Concluída. Se omitido, retorna tanto concluídas quanto não concluídas.
    - api_token (str): Token da API necessário para validar as solicitações. Um usuário tem um token diferente para cada empresa.
      Para mais informações: <https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference>
    - company_domain (str): Domínio da empresa no Pipedrive. Para mais informações: <https://pipedrive.readme.io/docs/how-to-get-the-company-domain>

    Retorna:
    dict: Um objeto com a lista de atividades.

    Exemplo de uso:
    activities_get_all(api_token='seu_token_aqui', company_domain='sua_empresa')
    """
    api_token = check_api_token(api_token)

    url = f'https://{company_domain}.pipedrive.com/v1/activities'
    
    params = {
        'user_id': user_id,
        'filter_id': filter_id,
        'type': type,
        'start': start if start is not None else 0,
        'limit': limit if limit is not None else 500,
        'start_date': start_date,
        'end_date': end_date,
        'done': done,
        'api_token': api_token
    }

    params = {k: v for k, v in params.items() if v is not None}
    
    url += "&".join([f"{key}={value}" for key, value in params.items()])
    
    return get_all_(url)

def activities_update(id, subject=None, done=None, type=None, due_date=None, due_time=None, 
                      duration=None, user_id=None, deal_id=None, person_id=None, participants=None, 
                      org_id=None, note=None, api_token=None, company_domain='api', return_type='complete'):
    """
    Edita uma atividade no Pipedrive.

    Parâmetros:
    - id (str): ID da atividade.
    - subject (str, opcional): Assunto da atividade. Se omitido, permanece inalterado.
    - done (int, opcional): Se a atividade está concluída ou não. 0 = Não concluída, 1 = Concluída.
    - type (str, opcional): Tipo da atividade, correlacionado com o parâmetro key_string de ActivityTypes.
    - due_date (str, opcional): Data de vencimento da atividade. Formato: YYYY-MM-DD.
    - due_time (str, opcional): Hora de vencimento da atividade em UTC. Formato: HH:MM.
    - duration (str, opcional): Duração da atividade. Formato: HH:MM.
    - user_id (int, opcional): ID do usuário a quem a atividade será atribuída.
    - deal_id (int, opcional): ID do negócio ao qual esta atividade será associada.
    - person_id (int, opcional): ID da pessoa à qual esta atividade será associada.
    - participants (list, opcional): Lista de participantes múltiplos para a atividade. Deve estar no formato JSON.
    - org_id (int, opcional): ID da organização à qual esta atividade será associada.
    - note (str, opcional): Nota da atividade no formato HTML. Se omitida, permanece inalterada.
    - api_token (str): Token da API necessário para validar as solicitações. Um usuário tem um token diferente para cada empresa.
      Para mais informações: <https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference>
    - company_domain (str): Domínio da empresa no Pipedrive. Para mais informações: <https://pipedrive.readme.io/docs/how-to-get-the-company-domain>
    - return_type (str, opcional): O retorno padrão é um objeto completo com todas as informações do processo, ou você pode definir como booleano (True = sucesso, False = erro).

    Retorna:
    dict ou bool: Retorna o objeto completo da resposta ou um booleano se especificado.

    Exemplo de uso:
    activities_update(id='12345', subject='Nova atividade', api_token='seu_token_aqui', company_domain='sua_empresa')
    """
    api_token = check_api_token(api_token)

    url = f'https://{company_domain}.pipedrive.com/v1/activities/{id}'
    
    body = {
        'subject': subject,
        'done': done,
        'type': type,
        'due_date': due_date,
        'due_time': due_time,
        'duration': duration,
        'user_id': user_id,
        'deal_id': deal_id,
        'person_id': person_id,
        'participants': participants,
        'org_id': org_id,
        'note': note
    }
    
    body = {k: v for k, v in body.items() if v is not None}

    headers = {'Content-Type': 'application/json'}
    params = {'api_token': api_token}

    response = requests.put(url, json=body, headers=headers, params=params)

    if return_type == 'boolean':
        return response.status_code in [200, 201]
    else:
        return response.json()

def activityfields_get_all(api_token=None, company_domain='api'):
    """
    Obtém todos os campos de uma atividade no Pipedrive.

    Parâmetros:
    - api_token (str): Token da API necessário para validar as solicitações. Um usuário tem um token diferente para cada empresa.
      Para mais informações: <https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference>
    - company_domain (str): Domínio da empresa no Pipedrive. Para mais informações: <https://pipedrive.readme.io/docs/how-to-get-the-company-domain>

    Retorna:
    dict: Um objeto com a lista de todos os campos da atividade.

    Exemplo de uso:
    activityfields_get_all(api_token='seu_token_aqui', company_domain='sua_empresa')
    """
    api_token = check_api_token(api_token)
    
    url = f'https://{company_domain}.pipedrive.com/v1/activityFields?api_token={api_token}'
    
    return get_all_(url)

def activitytypes_add(name, icon_key, color=None, api_token=None, company_domain='api', return_type='complete'):
    """
    Adiciona um novo tipo de atividade no Pipedrive.

    Parâmetros:
    - name (str): Nome do tipo de atividade.
    - icon_key (str): Ícone gráfico usado para representar esse tipo de atividade. Possíveis valores: 
      'task', 'email', 'meeting', 'deadline', 'call', 'lunch', 'calendar', 'downarrow', 'document', 
      'smartphone', 'camera', 'scissors', 'cogs', 'bubble', 'uparrow', 'checkbox', 'signpost', 
      'shuffle', 'addressbook', 'linegraph', 'picture', 'car', 'world', 'search', 'clip', 'sound', 
      'brush', 'key', 'padlock', 'pricetag', 'suitcase', 'finish', 'plane', 'loop', 'wifi', 'truck', 
      'cart', 'bulb', 'bell', 'presentation'.
    - color (str, opcional): Cor designada para o tipo de atividade no formato HEX de 6 caracteres (por exemplo, FFFFFF para branco, 000000 para preto).
    - api_token (str): Token da API necessário para validar as solicitações. Um usuário tem um token diferente para cada empresa.
      Para mais informações: <https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference>
    - company_domain (str): Domínio da empresa no Pipedrive. Para mais informações: <https://pipedrive.readme.io/docs/how-to-get-the-company-domain>
    - return_type (str, opcional): O retorno padrão é um objeto com todas as informações do processo, ou você pode definir como booleano (True = sucesso, False = erro).

    Retorna:
    dict ou bool: Retorna o objeto completo da resposta ou um booleano se especificado.

    Exemplo de uso:
    activitytypes_add(name='Tipo Exemplo', icon_key='call', api_token='seu_token_aqui', company_domain='sua_empresa')
    """
    api_token = check_api_token(api_token)

    url = f'https://{company_domain}.pipedrive.com/v1/activityTypes'
    
    body = {
        'name': name,
        'icon_key': icon_key,
        'color': color
    }
    
    body = {k: v for k, v in body.items() if v is not None}

    headers = {'Content-Type': 'application/json'}
    params = {'api_token': api_token}

    response = requests.post(url, json=body, headers=headers, params=params)

    if return_type == 'boolean':
        return response.status_code in [200, 201]
    else:
        return response.json()


def activitytypes_delete(id, api_token=None, company_domain='api', return_type='complete'):
    """
    Exclui um tipo de atividade no Pipedrive.

    Parâmetros:
    - id (str): ID do tipo de atividade.
    - api_token (str): Token da API necessário para validar as solicitações. Um usuário tem um token diferente para cada empresa.
      Para mais informações: <https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference>
    - company_domain (str): Domínio da empresa no Pipedrive. Para mais informações: <https://pipedrive.readme.io/docs/how-to-get-the-company-domain>
    - return_type (str, opcional): O retorno padrão é um objeto com todas as informações do processo, ou você pode definir como booleano (True = sucesso, False = erro).

    Retorna:
    dict ou bool: Retorna o objeto completo da resposta ou um booleano se especificado.

    Exemplo de uso:
    activitytypes_delete(id='12345', api_token='seu_token_aqui', company_domain='sua_empresa')
    """
    api_token = check_api_token(api_token)

    url = f'https://{company_domain}.pipedrive.com/v1/activityTypes/{id}'
    
    params = {'api_token': api_token}

    response = requests.delete(url, params=params)

    if return_type == 'boolean':
        return response.status_code in [200, 201]
    else:
        return response.json()

def activitytypes_delete_multiple(ids, api_token=None, company_domain='api', return_type='complete'):
    """
    Exclui múltiplos tipos de atividade em massa no Pipedrive.

    Parâmetros:
    - ids (str): IDs dos tipos de atividade, separados por vírgula, que serão excluídos.
    - api_token (str): Token da API necessário para validar as solicitações. Um usuário tem um token diferente para cada empresa.
      Para mais informações: <https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference>
    - company_domain (str): Domínio da empresa no Pipedrive. Para mais informações: <https://pipedrive.readme.io/docs/how-to-get-the-company-domain>
    - return_type (str, opcional): O retorno padrão é um objeto com todas as informações do processo, ou você pode definir como booleano (True = sucesso, False = erro).

    Retorna:
    dict ou bool: Retorna o objeto completo da resposta ou um booleano se especificado.

    Exemplo de uso:
    activitytypes_delete_multiple(ids='12345,67890', api_token='seu_token_aqui', company_domain='sua_empresa')
    """
    api_token = check_api_token(api_token)

    url = f'https://{company_domain}.pipedrive.com/v1/activityTypes'
    
    body = {'ids': ids}
    params = {'api_token': api_token}

    response = requests.delete(url, params=params, json=body)

    if return_type == 'boolean':
        return response.status_code in [200, 201]
    else:
        return response.json()
    
def activitytypes_get_all(api_token=None, company_domain='api'):
    """
    Função para obter todos os tipos de atividade no Pipedrive.

    Parâmetros:
    - api_token (str, opcional): Token de API para autenticação. Se não fornecido, será tratado.
    - company_domain (str, opcional): Domínio da empresa.

    Retorna:
    - pd.DataFrame: Um DataFrame contendo todos os tipos de atividade.
    """
    api_token = check_api_token(api_token)
    
    url = f'https://{company_domain}.pipedrive.com/v1/activityTypes?api_token={api_token}'
    
    return get_all_(url)



def activitytypes_update(id, name=None, icon_key=None, color=None, order_nr=None, 
                         api_token=None, company_domain='api', return_type='complete'):
    """
    Edita um tipo de atividade no Pipedrive.

    Parâmetros:
    - id (str): ID do tipo de atividade.
    - name (str, opcional): Nome do tipo de atividade.
    - icon_key (str, opcional): Ícone gráfico a ser usado. Valores suportados: 'default', 'call', 'meeting', 'lunch', 'email', 'task', 'deadline'. Outros valores serão disponibilizados no futuro.
    - color (str, opcional): Cor designada para o tipo de atividade no formato HEX de 6 caracteres (ex: FFFFFF para branco, 000000 para preto).
    - order_nr (int, opcional): Número de ordem para este tipo de atividade. Números de ordem devem ser usados para ordenar os tipos nas seleções de tipos de atividade.
    - api_token (str): Token da API necessário para validar as solicitações. Um usuário tem um token diferente para cada empresa.
      Para mais informações: <https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference>
    - company_domain (str): Domínio da empresa no Pipedrive. Para mais informações: <https://pipedrive.readme.io/docs/how-to-get-the-company-domain>
    - return_type (str, opcional): O retorno padrão é um objeto com todas as informações do processo, ou você pode definir como booleano (True = sucesso, False = erro).

    Retorna:
    dict ou bool: Retorna o objeto completo da resposta ou um booleano se especificado.

    Exemplo de uso:
    activitytypes_update(id='12345', name='Novo Nome', api_token='seu_token_aqui', company_domain='sua_empresa')
    """
    api_token = check_api_token(api_token)

    url = f'https://{company_domain}.pipedrive.com/v1/activityTypes/{id}'
    
    body = {
        'name': name,
        'icon_key': icon_key,
        'color': color,
        'order_nr': order_nr
    }
    
    body = {k: v for k, v in body.items() if v is not None}

    headers = {'Content-Type': 'application/json'}
    params = {'api_token': api_token}

    response = requests.put(url, json=body, headers=headers, params=params)

    if return_type == 'boolean':
        return response.status_code in [200, 201]
    else:
        return response.json()

def authorizations_add(email, password, api_token=None, company_domain='api', return_type='complete'):
    """
    Obtém todas as autorizações de um usuário no Pipedrive.

    Parâmetros:
    - email (str): Email do usuário.
    - password (str): Senha do usuário.
    - api_token (str): Token da API necessário para validar as solicitações. Um usuário tem um token diferente para cada empresa.
      Para mais informações: <https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference>
    - company_domain (str): Domínio da empresa no Pipedrive. Para mais informações: <https://pipedrive.readme.io/docs/how-to-get-the-company-domain>
    - return_type (str, opcional): O retorno padrão é um objeto com todas as informações do processo, ou você pode definir como booleano (True = sucesso, False = erro).

    Retorna:
    dict ou bool: Retorna o objeto completo da resposta ou um booleano se especificado.

    Exemplo de uso:
    authorizations_add(email='usuario@example.com', password='senha', api_token='seu_token_aqui', company_domain='sua_empresa')
    """
    api_token = check_api_token(api_token)

    url = f'https://{company_domain}.pipedrive.com/v1/authorizations'
    
    body = {
        'email': email,
        'password': password
    }
    
    body = {k: v for k, v in body.items() if v is not None}

    headers = {'Content-Type': 'application/json'}
    params = {'api_token': api_token}

    response = requests.post(url, json=body, headers=headers, params=params)

    if return_type == 'boolean':
        return response.status_code in [200, 201]
    else:
        return response.json()
    


def currencies_get_all(term=None, api_token=None, company_domain='api'):
    """
    Função para obter todas as moedas suportadas no Pipedrive.

    Parâmetros:
    - term (str, opcional): Termo de busca opcional para filtrar moedas.
    - api_token (str, opcional): Token de API para autenticação. Se não fornecido, será tratado.
    - company_domain (str, opcional): Domínio da empresa. Padrão é 'api'.

    Retorna:
    - pd.DataFrame: Um DataFrame contendo todas as moedas suportadas.
    """
    api_token = check_api_token(api_token)
    
    url = f'https://{company_domain}.pipedrive.com/v1/currencies?api_token={api_token}'
    
    if term:
        url += f'&term={term}'
    
    return get_all_(url)



def dealfields_add(name, field_type, options=None, api_token=None, company_domain='api', return_type='complete'):
    """
    Adiciona um novo campo de negócio no Pipedrive.

    Parâmetros:
    - name (str): Nome do campo.
    - field_type (str): Tipo do campo. Possíveis valores:
      'varchar' = Texto (até 255 caracteres),
      'varchar_auto' = Texto com autocomplete (até 255 caracteres),
      'text' = Texto longo (até 65k caracteres),
      'double' = Valor numérico,
      'monetary' = Campo monetário (valor numérico e moeda),
      'date' = Data (formato YYYY-MM-DD),
      'set' = Campo de opções com múltiplas opções possíveis,
      'enum' = Campo de opções com uma única opção possível,
      'user' = Campo de usuário (contém um ID de usuário Pipedrive),
      'org' = Campo de organização (contém um ID de organização armazenado na mesma conta),
      'people' = Campo de pessoa (contém um ID de pessoa armazenado na mesma conta),
      'phone' = Campo de telefone (até 255 números ou caracteres),
      'time' = Campo de tempo (formato HH:MM:SS),
      'timerange' = Intervalo de tempo (hora de início e fim, ambos no formato HH:MM:SS),
      'daterange' = Intervalo de datas (data de início e fim, ambos no formato YYYY-MM-DD).
    - options (list, opcional): Quando o field_type for 'set' ou 'enum', deve ser fornecido um array sequencial de opções no formato JSON.
    - api_token (str): Token da API necessário para validar as solicitações. Um usuário tem um token diferente para cada empresa.
      Para mais informações: <https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference>
    - company_domain (str): Domínio da empresa no Pipedrive. Para mais informações: <https://pipedrive.readme.io/docs/how-to-get-the-company-domain>
    - return_type (str, opcional): O retorno padrão é um objeto com todas as informações do processo, ou você pode definir como booleano (True = sucesso, False = erro).

    Retorna:
    dict ou bool: Retorna o objeto completo da resposta ou um booleano se especificado.

    Exemplo de uso:
    dealfields_add(name='Novo Campo', field_type='varchar', api_token='seu_token_aqui', company_domain='sua_empresa')
    """
    api_token = check_api_token(api_token)

    url = f'https://{company_domain}.pipedrive.com/v1/dealFields'
    
    body = {
        'name': name,
        'field_type': field_type,
        'options': options
    }
    
    body = {k: v for k, v in body.items() if v is not None}

    headers = {'Content-Type': 'application/json'}
    params = {'api_token': api_token}

    response = requests.post(url, json=body, headers=headers, params=params)

    if return_type == 'boolean':
        return response.status_code in [200, 201]
    else:
        return response.json()
    
def dealfields_delete(id, api_token=None, company_domain='api', return_type='complete'):
    """
    Exclui um campo de negócio no Pipedrive.

    Parâmetros:
    - id (str): ID do campo a ser excluído.
    - api_token (str): Token da API necessário para validar as solicitações. Um usuário tem um token diferente para cada empresa.
      Para mais informações: <https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference>
    - company_domain (str): Domínio da empresa no Pipedrive. Para mais informações: <https://pipedrive.readme.io/docs/how-to-get-the-company-domain>
    - return_type (str, opcional): O retorno padrão é um objeto com todas as informações do processo, ou você pode definir como booleano (True = sucesso, False = erro).

    Retorna:
    dict ou bool: Retorna o objeto completo da resposta ou um booleano se especificado.

    Exemplo de uso:
    dealfields_delete(id='12345', api_token='seu_token_aqui', company_domain='sua_empresa')
    """
    api_token = check_api_token(api_token)

    url = f'https://{company_domain}.pipedrive.com/v1/dealFields/{id}'
    
    params = {'api_token': api_token}

    response = requests.delete(url, params=params)

    if return_type == 'boolean':
        return response.status_code in [200, 201]
    else:
        return response.json()



def dealfields_delete_multiple(ids, api_token=None, company_domain='api', return_type='complete'):
    """
    Exclui múltiplos campos de negócio em massa no Pipedrive.

    Parâmetros:
    - ids (str): IDs dos campos, separados por vírgula, que serão excluídos.
    - api_token (str): Token da API necessário para validar as solicitações. Um usuário tem um token diferente para cada empresa.
      Para mais informações: <https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference>
    - company_domain (str): Domínio da empresa no Pipedrive. Para mais informações: <https://pipedrive.readme.io/docs/how-to-get-the-company-domain>
    - return_type (str, opcional): O retorno padrão é um objeto com todas as informações do processo, ou você pode definir como booleano (True = sucesso, False = erro).

    Retorna:
    dict ou bool: Retorna o objeto completo da resposta ou um booleano se especificado.

    Exemplo de uso:
    dealfields_delete_multiple(ids='12345,67890', api_token='seu_token_aqui', company_domain='sua_empresa')
    """
    api_token = check_api_token(api_token)

    url = f'https://{company_domain}.pipedrive.com/v1/dealFields'
    
    body = {'ids': ids}
    params = {'api_token': api_token}

    response = requests.delete(url, params=params, json=body)

    if return_type == 'boolean':
        return response.status_code in [200, 201]
    else:
        return response.json()

def dealfields_get(id, api_token=None, company_domain='api'):
    """
    Função para obter um campo de negócio específico do Pipedrive.

    Parâmetros:
    - id (str): ID do campo a ser buscado.
    - api_token (str): Token de API para validar as requisições. Para mais informações: 
      https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference
    - company_domain (str): Domínio da empresa. Para mais informações: 
      https://pipedrive.readme.io/docs/how-to-get-the-company-domain

    Retorna:
    - pd.DataFrame: Um DataFrame contendo os detalhes do campo de negócio.
    """
    api_token = check_api_token(api_token)
    
    url = f'https://{company_domain}.pipedrive.com/v1/dealFields/{id}?api_token={api_token}'
    
    return get_all_(url)



def dealfields_get_all(start=None, limit=None, api_token=None, company_domain='api'):
    """
    Função para obter todos os campos de negócio do Pipedrive.

    Parâmetros:
    - start (int, opcional): Início da paginação. Padrão é 0.
    - limit (int, opcional): Número de itens por página. Padrão é 500.
    - api_token (str, opcional): Token de API para autenticação. Se não fornecido, será tratado.
    - company_domain (str, opcional): Domínio da empresa. Padrão é 'api'.

    Retorna:
    - pd.DataFrame: Um DataFrame contendo todos os campos de negócio.
    """
    api_token = check_api_token(api_token)
    
    url = f'https://{company_domain}.pipedrive.com/v1/dealFields?api_token={api_token}'
    
    params = {}
    if limit is None:
        limit = 500
    if start is None:
        start = 0
    
    if limit:
        params['limit'] = limit
    if start:
        params['start'] = start
    
    url = f"{url}&{prepare_url_parameters_(params)}"
    
    return get_all_(url)


def dealfields_update(id, name, options=None, api_token=None, company_domain='api', return_type='complete'):
    """
    Atualiza um campo de negócio no Pipedrive.

    Parâmetros:
    - id (str): ID do campo a ser atualizado.
    - name (str): Nome do campo.
    - options (list, opcional): Quando o tipo do campo for 'set' ou 'enum', as opções possíveis devem ser fornecidas como um array sequencial codificado em JSON. 
      Todos os itens ativos devem ser fornecidos, e os itens já existentes devem ter seus IDs fornecidos. Novos itens exigem apenas um rótulo.
      Exemplo: [{"id":123,"label":"Item Existente"},{"label":"Novo Item"}].
    - api_token (str): Token da API necessário para validar as solicitações. Um usuário tem um token diferente para cada empresa.
      Para mais informações: <https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference>
    - company_domain (str): Domínio da empresa no Pipedrive. Para mais informações: <https://pipedrive.readme.io/docs/how-to-get-the-company-domain>
    - return_type (str, opcional): O retorno padrão é um objeto com todas as informações do processo, ou você pode definir como booleano (True = sucesso, False = erro).

    Retorna:
    dict ou bool: Retorna o objeto completo da resposta ou um booleano se especificado.

    Exemplo de uso:
    dealfields_update(id='12345', name='Novo Campo', options=[{'id':123,'label':'Item Existente'}, {'label':'Novo Item'}], api_token='seu_token_aqui', company_domain='sua_empresa')
    """
    api_token = check_api_token(api_token)

    url = f'https://{company_domain}.pipedrive.com/v1/dealFields/{id}'
    
    body = {
        'name': name,
        'options': options
    }
    
    body = {k: v for k, v in body.items() if v is not None}

    headers = {'Content-Type': 'application/json'}
    params = {'api_token': api_token}

    response = requests.put(url, json=body, headers=headers, params=params)

    if return_type == 'boolean':
        return response.status_code in [200, 201]
    else:
        return response.json()


def deals_add(title, value=None, currency=None, user_id=None, person_id=None, org_id=None, 
              stage_id=None, status=None, probability=None, lost_reason=None, add_time=None, 
              visible_to=None, customList=None, api_token=None, company_domain='api', return_type='complete'):
    """
    Adiciona um novo negócio no Pipedrive.

    Parâmetros:
    - title (str): Título do negócio.
    - value (float, opcional): Valor do negócio. Se omitido, será definido como 0.
    - currency (str, opcional): Moeda do negócio. Aceita um código de moeda de 3 caracteres. Se omitido, será definida a moeda padrão do usuário autorizado.
    - user_id (int, opcional): ID do usuário que será marcado como proprietário do negócio. Se omitido, será usado o ID do usuário autorizado.
    - person_id (int, opcional): ID da pessoa associada ao negócio.
    - org_id (int, opcional): ID da organização associada ao negócio.
    - stage_id (int, opcional): ID da fase em que o negócio será colocado em um pipeline.
    - status (str, opcional): Status do negócio: 'open' = Aberto, 'won' = Ganhou, 'lost' = Perdido, 'deleted' = Excluído. Se omitido, será definido como 'open'.
    - probability (float, opcional): Percentual de probabilidade de sucesso do negócio.
    - lost_reason (str, opcional): Motivo pelo qual o negócio foi perdido (usado quando status='lost').
    - add_time (str, opcional): Data e hora de criação do negócio em UTC. Exige token de usuário admin. Formato: YYYY-MM-DD HH:MM:SS.
    - visible_to (int, opcional): Visibilidade do negócio. 1 = Proprietário e seguidores (privado); 3 = Empresa inteira (compartilhado).
    - customList (dict, opcional): Lista de campos personalizados. Exemplo: {'custom_field': 'abc'}.
    - api_token (str): Token da API necessário para validar as solicitações.
      Para mais informações: <https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference>
    - company_domain (str): Domínio da empresa no Pipedrive. Para mais informações: <https://pipedrive.readme.io/docs/how-to-get-the-company-domain>
    - return_type (str, opcional): O retorno padrão é um objeto com todas as informações do processo, ou você pode definir como booleano (True = sucesso, False = erro).

    Retorna:
    dict ou bool: Retorna o objeto completo da resposta ou um booleano se especificado.

    Exemplo de uso:
    deals_add(title='Novo Negócio', api_token='seu_token_aqui', company_domain='sua_empresa')
    """
    api_token = check_api_token(api_token)

    url = f'https://{company_domain}.pipedrive.com/v1/deals'
    
    body = {
        'title': title,
        'value': value,
        'currency': currency,
        'user_id': user_id,
        'person_id': person_id,
        'org_id': org_id,
        'stage_id': stage_id,
        'status': status,
        'probability': probability,
        'lost_reason': lost_reason,
        'add_time': add_time,
        'visible_to': visible_to
    }

    if isinstance(customList, dict):
        body.update(customList)

    body = {k: v for k, v in body.items() if v is not None}

    headers = {'Content-Type': 'application/json'}
    params = {'api_token': api_token}

    response = requests.post(url, json=body, headers=headers, params=params)

    if return_type == 'boolean':
        return response.status_code in [200, 201]
    else:
        return response.json()


def deals_add_follower(id, user_id, api_token=None, company_domain='api', return_type='complete'):
    """
    Adiciona um seguidor a um negócio no Pipedrive.

    Parâmetros:
    - id (str): ID do negócio.
    - user_id (str): ID do usuário.
    - api_token (str): Token da API necessário para validar as solicitações. Um usuário tem um token diferente para cada empresa.
      Para mais informações: <https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference>
    - company_domain (str): Domínio da empresa no Pipedrive. Para mais informações: <https://pipedrive.readme.io/docs/how-to-get-the-company-domain>
    - return_type (str, opcional): O retorno padrão é um objeto com todas as informações do processo, ou você pode definir como booleano (True = sucesso, False = erro).

    Retorna:
    dict ou bool: Retorna o objeto completo da resposta ou um booleano se especificado.

    Exemplo de uso:
    deals_add_follower(id='12345', user_id='67890', api_token='seu_token_aqui', company_domain='sua_empresa')
    """
    api_token = check_api_token(api_token)

    url = f'https://{company_domain}.pipedrive.com/v1/deals/{id}/followers'
    
    body = {
        'user_id': user_id
    }

    body = {k: v for k, v in body.items() if v is not None}

    headers = {'Content-Type': 'application/json'}
    params = {'api_token': api_token}

    response = requests.post(url, json=body, headers=headers, params=params)

    if return_type == 'boolean':
        return response.status_code in [200, 201]
    else:
        return response.json()

def deals_add_participant(id, person_id, api_token=None, company_domain='api', return_type='complete'):
    """
    Adiciona um participante a um negócio no Pipedrive.

    Parâmetros:
    - id (str): ID do negócio.
    - person_id (str): ID da pessoa.
    - api_token (str): Token da API necessário para validar as solicitações. Um usuário tem um token diferente para cada empresa.
      Para mais informações: <https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference>
    - company_domain (str): Domínio da empresa no Pipedrive. Para mais informações: <https://pipedrive.readme.io/docs/how-to-get-the-company-domain>
    - return_type (str, opcional): O retorno padrão é um objeto com todas as informações do processo, ou você pode definir como booleano (True = sucesso, False = erro).

    Retorna:
    dict ou bool: Retorna o objeto completo da resposta ou um booleano se especificado.

    Exemplo de uso:
    deals_add_participant(id='12345', person_id='67890', api_token='seu_token_aqui', company_domain='sua_empresa')
    """
    api_token = check_api_token(api_token)

    url = f'https://{company_domain}.pipedrive.com/v1/deals/{id}/participants'
    
    body = {
        'person_id': person_id
    }

    headers = {'Content-Type': 'application/json'}
    params = {'api_token': api_token}

    response = requests.post(url, json=body, headers=headers, params=params)

    if return_type == 'boolean':
        return response.status_code in [200, 201]
    else:
        return response.json()

def deals_add_product(id, product_id, item_price, quantity, discount_percentage=None, duration=None, 
                      product_variation_id=None, comments=None, enabled_flag=None, 
                      api_token=None, company_domain='api', return_type='complete'):
    """
    Adiciona um produto ao negócio no Pipedrive, criando um item chamado deal-product.

    Parâmetros:
    - id (str): ID do negócio.
    - product_id (str): ID do produto que será associado ao negócio.
    - item_price (float): Preço pelo qual este produto será adicionado ao negócio.
    - quantity (int): Quantidade de itens deste produto que serão adicionados ao negócio.
    - discount_percentage (float, opcional): Percentual de desconto. Se omitido, será definido como 0.
    - duration (int, opcional): Duração do produto. Se omitido, será definido como 1.
    - product_variation_id (str, opcional): ID da variação do produto a ser usada. Se omitido, nenhuma variação será utilizada.
    - comments (str, opcional): Comentário textual associado a este vínculo produto-negócio. Visível e editável na interface do aplicativo.
    - enabled_flag (int, opcional): Se o produto está habilitado no negócio ou não. Se omitido, o produto será habilitado por padrão. 
      0 = Desabilitado, 1 = Habilitado.
    - api_token (str): Token da API necessário para validar as solicitações. Um usuário tem um token diferente para cada empresa.
      Para mais informações: <https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference>
    - company_domain (str): Domínio da empresa no Pipedrive. Para mais informações: <https://pipedrive.readme.io/docs/how-to-get-the-company-domain>
    - return_type (str, opcional): O retorno padrão é um objeto com todas as informações do processo, ou você pode definir como booleano (True = sucesso, False = erro).

    Retorna:
    dict ou bool: Retorna o objeto completo da resposta ou um booleano se especificado.

    Exemplo de uso:
    deals_add_product(id='12345', product_id='67890', item_price=100.0, quantity=2, api_token='seu_token_aqui', company_domain='sua_empresa')
    """
    api_token = check_api_token(api_token)

    url = f'https://{company_domain}.pipedrive.com/v1/deals/{id}/products'
    
    body = {
        'product_id': product_id,
        'item_price': item_price,
        'quantity': quantity,
        'discount_percentage': discount_percentage,
        'duration': duration,
        'product_variation_id': product_variation_id,
        'comments': comments,
        'enabled_flag': enabled_flag
    }

    body = {k: v for k, v in body.items() if v is not None}

    headers = {'Content-Type': 'application/json'}
    params = {'api_token': api_token}

    response = requests.post(url, json=body, headers=headers, params=params)

    if return_type == 'boolean':
        return response.status_code in [200, 201]
    else:
        return response.json()
    
def deals_delete(id, api_token=None, company_domain='api', return_type='complete'):
    """
    Exclui um negócio no Pipedrive.

    Parâmetros:
    - id (str): ID do negócio a ser excluído.
    - api_token (str): Token da API necessário para validar as solicitações. Um usuário tem um token diferente para cada empresa.
      Para mais informações: <https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference>
    - company_domain (str): Domínio da empresa no Pipedrive. Para mais informações: <https://pipedrive.readme.io/docs/how-to-get-the-company-domain>
    - return_type (str, opcional): O retorno padrão é um objeto com todas as informações do processo, ou você pode definir como booleano (True = sucesso, False = erro).

    Retorna:
    dict ou bool: Retorna o objeto completo da resposta ou um booleano se especificado.

    Exemplo de uso:
    deals_delete(id='12345', api_token='seu_token_aqui', company_domain='sua_empresa')
    """
    api_token = check_api_token(api_token)

    url = f'https://{company_domain}.pipedrive.com/v1/deals/{id}'
    params = {'api_token': api_token}

    response = requests.delete(url, params=params)

    if return_type == 'boolean':
        return response.status_code in [200, 201]
    else:
        return response.json()

def deals_delete_follower(id, follower_id, api_token=None, company_domain='api', return_type='complete'):
    """
    Exclui um seguidor de um negócio no Pipedrive.

    Parâmetros:
    - id (str): ID do negócio.
    - follower_id (str): ID do seguidor a ser excluído.
    - api_token (str): Token da API necessário para validar as solicitações. Um usuário tem um token diferente para cada empresa.
      Para mais informações: <https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference>
    - company_domain (str): Domínio da empresa no Pipedrive. Para mais informações: <https://pipedrive.readme.io/docs/how-to-get-the-company-domain>
    - return_type (str, opcional): O retorno padrão é um objeto com todas as informações do processo, ou você pode definir como booleano (True = sucesso, False = erro).

    Retorna:
    dict ou bool: Retorna o objeto completo da resposta ou um booleano se especificado.

    Exemplo de uso:
    deals_delete_follower(id='12345', follower_id='67890', api_token='seu_token_aqui', company_domain='sua_empresa')
    """
    api_token = check_api_token(api_token)

    url = f'https://{company_domain}.pipedrive.com/v1/deals/{id}/followers/{follower_id}'
    params = {'api_token': api_token}

    response = requests.delete(url, params=params)

    if return_type == 'boolean':
        return response.status_code in [200, 201]
    else:
        return response.json()

def deals_delete_participant(id, deal_participant_id, api_token=None, company_domain='api', return_type='complete'):
    """
    Exclui um participante de um negócio no Pipedrive.

    Parâmetros:
    - id (str): ID do negócio.
    - deal_participant_id (str): ID do participante do negócio a ser excluído.
    - api_token (str): Token da API necessário para validar as solicitações. Um usuário tem um token diferente para cada empresa.
      Para mais informações: <https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference>
    - company_domain (str): Domínio da empresa no Pipedrive. Para mais informações: <https://pipedrive.readme.io/docs/how-to-get-the-company-domain>
    - return_type (str, opcional): O retorno padrão é um objeto com todas as informações do processo, ou você pode definir como booleano (True = sucesso, False = erro).

    Retorna:
    dict ou bool: Retorna o objeto completo da resposta ou um booleano se especificado.

    Exemplo de uso:
    deals_delete_participant(id='12345', deal_participant_id='67890', api_token='seu_token_aqui', company_domain='sua_empresa')
    """
    api_token = check_api_token(api_token)

    url = f'https://{company_domain}.pipedrive.com/v1/deals/{id}/participants/{deal_participant_id}'
    params = {'api_token': api_token}

    response = requests.delete(url, params=params)

    if return_type == 'boolean':
        return response.status_code in [200, 201]
    else:
        return response.json()

def deals_delete_product(id, product_attachment_id, api_token=None, company_domain='api', return_type='complete'):
    """
    Exclui um produto anexado de um negócio no Pipedrive.

    Parâmetros:
    - id (str): ID do negócio.
    - product_attachment_id (str): ID do anexo do produto. Isso é retornado como product_attachment_id após anexar um produto a um negócio ou como id ao listar os produtos anexados a um negócio.
    - api_token (str): Token da API necessário para validar as solicitações. Um usuário tem um token diferente para cada empresa.
      Para mais informações: <https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference>
    - company_domain (str): Domínio da empresa no Pipedrive. Para mais informações: <https://pipedrive.readme.io/docs/how-to-get-the-company-domain>
    - return_type (str, opcional): O retorno padrão é um objeto com todas as informações do processo, ou você pode definir como booleano (True = sucesso, False = erro).

    Retorna:
    dict ou bool: Retorna o objeto completo da resposta ou um booleano se especificado.

    Exemplo de uso:
    deals_delete_product(id='12345', product_attachment_id='67890', api_token='seu_token_aqui', company_domain='sua_empresa')
    """
    api_token = check_api_token(api_token)

    url = f'https://{company_domain}.pipedrive.com/v1/deals/{id}/products/{product_attachment_id}'
    params = {'api_token': api_token}

    response = requests.delete(url, params=params)

    if return_type == 'boolean':
        return response.status_code in [200, 201]
    else:
        return response.json()

def deals_delete_multiple(ids, api_token=None, company_domain='api', return_type='complete'):
    """
    Exclui múltiplos negócios em massa no Pipedrive.

    Parâmetros:
    - ids (str): IDs dos negócios a serem excluídos, separados por vírgula.
    - api_token (str): Token da API necessário para validar as solicitações. Um usuário tem um token diferente para cada empresa.
      Para mais informações: <https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference>
    - company_domain (str): Domínio da empresa no Pipedrive. Para mais informações: <https://pipedrive.readme.io/docs/how-to-get-the-company-domain>
    - return_type (str, opcional): O retorno padrão é um objeto com todas as informações do processo, ou você pode definir como booleano (True = sucesso, False = erro).

    Retorna:
    dict ou bool: Retorna o objeto completo da resposta ou um booleano se especificado.

    Exemplo de uso:
    deals_delete_multiple(ids='12345,67890', api_token='seu_token_aqui', company_domain='sua_empresa')
    """
    api_token = check_api_token(api_token)

    url = f'https://{company_domain}.pipedrive.com/v1/deals'
    
    body = {'ids': ids}
    params = {'api_token': api_token}

    response = requests.delete(url, params=params, json=body)

    if return_type == 'boolean':
        return response.status_code in [200, 201]
    else:
        return response.json()

def deals_duplicate(id, api_token=None, company_domain='api', return_type='complete'):
    """
    Duplica um negócio no Pipedrive.

    Parâmetros:
    - id (str): ID do negócio que será duplicado.
    - api_token (str): Token da API necessário para validar as solicitações. Um usuário tem um token diferente para cada empresa.
      Para mais informações: <https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference>
    - company_domain (str): Domínio da empresa no Pipedrive. Para mais informações: <https://pipedrive.readme.io/docs/how-to-get-the-company-domain>
    - return_type (str, opcional): O retorno padrão é um objeto com todas as informações do processo, ou você pode definir como booleano (True = sucesso, False = erro).

    Retorna:
    dict ou bool: Retorna o objeto completo da resposta ou um booleano se especificado.

    Exemplo de uso:
    deals_duplicate(id='12345', api_token='seu_token_aqui', company_domain='sua_empresa')
    """
    api_token = check_api_token(api_token)

    url = f'https://{company_domain}.pipedrive.com/v1/deals/{id}/duplicate'
    params = {'api_token': api_token}

    response = requests.post(url, params=params)

    if return_type == 'boolean':
        return response.status_code in [200, 201]
    else:
        return response.json()


def deals_find(term, person_id=None, org_id=None, api_token=None, company_domain='api'):
    """
    Encontra negócios pelo nome no Pipedrive.

    Parâmetros:
    - term (str): Termo de pesquisa a ser buscado.
    - person_id (int, opcional): ID da pessoa com a qual o negócio está associado.
    - org_id (int, opcional): ID da organização com a qual o negócio está associado.
    - api_token (str): Token da API necessário para validar as solicitações. Um usuário tem um token diferente para cada empresa.
      Para mais informações: <https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference>
    - company_domain (str): Domínio da empresa no Pipedrive. Para mais informações: <https://pipedrive.readme.io/docs/how-to-get-the-company-domain>

    Retorna:
    dict: Um objeto com os resultados da busca.

    Exemplo de uso:
    deals_find(term='Negócio Exemplo', api_token='seu_token_aqui', company_domain='sua_empresa')
    """
    api_token = check_api_token(api_token)

    url = f'https://{company_domain}.pipedrive.com/v1/deals/find'

    params = {
        'term': term,
        'person_id': person_id,
        'org_id': org_id,
        'api_token': api_token
    }

    params = {k: v for k, v in params.items() if v is not None}

    response = requests.get(url, params=params)

    return response.json()


def deals_get(id, api_token=None, company_domain='api'):
    """
    Função para obter detalhes de um negócio no Pipedrive.

    Parâmetros:
    - id (str): ID do negócio.
    - api_token (str): Token de API para validar as requisições. Para mais informações: 
      https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference
    - company_domain (str): Domínio da empresa. Para mais informações: 
      https://pipedrive.readme.io/docs/how-to-get-the-company-domain

    Retorna:
    - pd.DataFrame: Um DataFrame contendo os detalhes do negócio.
    """
   
    api_token = check_api_token(api_token)
    
    url = f'https://{company_domain}.pipedrive.com/v1/deals/{id}?api_token={api_token}'
    
    
    return get_all_(url)



def deals_get_activities(id, start=None, limit=None, done=None, exclude=None, api_token=None, company_domain='api'):
    """
    Função para listar atividades associadas a um negócio no Pipedrive.

    Parâmetros:
    - id (str): ID do negócio.
    - start (int, opcional): Paginação inicial.
    - limit (int, opcional): Número de itens por página.
    - done (int, opcional): Buscar atividades concluídas (1) ou não concluídas (0). Se omitido, ambas são buscadas.
    - exclude (str, opcional): String separada por vírgulas com os IDs de atividades a serem excluídas dos resultados.
    - api_token (str): Token de API para validar as requisições. Para mais informações: 
      https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference
    - company_domain (str): Domínio da empresa. Para mais informações: 
      https://pipedrive.readme.io/docs/how-to-get-the-company-domain

    Retorna:
    - pd.DataFrame: Um DataFrame contendo as atividades associadas ao negócio.
    """
    api_token = check_api_token(api_token)
    
    params = {
        'id': id,
        'start': start if start is not None else 0,
        'limit': limit if limit is not None else 500,
        'done': done,
        'exclude': exclude
    }

    params = clear_list(params)

    url = f'https://{company_domain}.pipedrive.com/v1/deals/{id}/activities?'
    url += prepare_url_parameters_(params)
    url += f'&api_token={api_token}'
    
    return get_all_(url)



def deals_get_files(id, start=None, limit=None, include_deleted_files=None, sort=None, api_token=None, company_domain='api'):
    """
    Função para listar arquivos anexados a um negócio no Pipedrive.

    Parâmetros:
    - id (str): ID do negócio.
    - start (int, opcional): Paginação inicial.
    - limit (int, opcional): Número de itens por página.
    - include_deleted_files (int, opcional): Quando habilitado, a lista de arquivos incluirá arquivos excluídos. 
      Note que tentar baixar esses arquivos não funcionará. Domínios permitidos: (0; 1).
    - sort (str, opcional): Nome dos campos e modo de ordenação, separados por vírgula (ex.: 'field_name_1 ASC, field_name_2 DESC').
      Apenas campos de primeiro nível são suportados. Campos suportados: id, user_id, deal_id, person_id, org_id, product_id, 
      add_time, update_time, file_name, file_type, file_size, comment.
    - api_token (str): Token de API para validar as requisições. Para mais informações: 
      https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference
    - company_domain (str): Domínio da empresa. Para mais informações: 
      https://pipedrive.readme.io/docs/how-to-get-the-company-domain

    Retorna:
    - pd.DataFrame: Um DataFrame contendo os arquivos anexados ao negócio.
    """

    api_token = check_api_token(api_token)
    

    params = {
        'id': id,
        'start': start if start is not None else 0,
        'limit': limit if limit is not None else 500,
        'include_deleted_files': include_deleted_files,
        'sort': sort
    }


    params = clear_list(params)

    url = f'https://{company_domain}.pipedrive.com/v1/deals/{id}/files?'
    url += prepare_url_parameters_(params)
    url += f'&api_token={api_token}'
    
    return get_all_(url)



def deals_get_flow(id, start=None, limit=None, api_token=None, company_domain='api'):
    """
    Função para listar atualizações sobre um negócio no Pipedrive.

    Parâmetros:
    - id (str): ID do negócio.
    - start (int, opcional): Paginação inicial.
    - limit (int, opcional): Número de itens por página.
    - api_token (str): Token de API para validar as requisições. Para mais informações: 
      https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference
    - company_domain (str): Domínio da empresa. Para mais informações: 
      https://pipedrive.readme.io/docs/how-to-get-the-company-domain

    Retorna:
    - pd.DataFrame: Um DataFrame contendo as atualizações sobre o negócio.
    """
    
    api_token = check_api_token(api_token)
    
    params = {
        'id': id,
        'start': start if start is not None else 0,
        'limit': limit if limit is not None else 500
    }


    params = clear_list(params)

    url = f'https://{company_domain}.pipedrive.com/v1/deals/{id}/flow?'
    url += prepare_url_parameters_(params)
    url += f'&api_token={api_token}'
    
    return get_all_(url)



def deals_get_followers(id, api_token=None, company_domain='api'):
    """
    Função para listar os seguidores de um negócio no Pipedrive.

    Parâmetros:
    - id (str): ID do negócio.
    - api_token (str): Token de API para validar as requisições. Para mais informações: 
      https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference
    - company_domain (str): Domínio da empresa. Para mais informações: 
      https://pipedrive.readme.io/docs/how-to-get-the-company-domain

    Retorna:
    - pd.DataFrame: Um DataFrame contendo a lista de seguidores do negócio.
    """
    api_token = check_api_token(api_token)
    
    url = f'https://{company_domain}.pipedrive.com/v1/deals/{id}/followers?api_token={api_token}'
    
    return get_all_(url)

def deals_get_mailmessages(id, start=None, limit=None, api_token=None, company_domain='api'):
    """
    Função para listar as mensagens de e-mail associadas a um negócio no Pipedrive.

    Parâmetros:
    - id (str): ID do negócio.
    - start (int, opcional): Paginação inicial.
    - limit (int, opcional): Número de itens por página.
    - api_token (str): Token de API para validar as requisições. Para mais informações: 
      https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference
    - company_domain (str): Domínio da empresa. Para mais informações: 
      https://pipedrive.readme.io/docs/how-to-get-the-company-domain

    Retorna:
    - pd.DataFrame: Um DataFrame contendo as mensagens de e-mail associadas ao negócio.
    """
    api_token = check_api_token(api_token)
    
    params = {
        'id': id,
        'start': start if start is not None else 0,
        'limit': limit if limit is not None else 500
    }

    params = clear_list(params)

    url = f'https://{company_domain}.pipedrive.com/v1/deals/{id}/mailMessages?'
    url += prepare_url_parameters_(params)
    url += f'&api_token={api_token}'
    
    return get_all_(url)


def deals_get_participants(id, start=None, limit=None, api_token=None, company_domain='api'):
    """
    Função para listar os participantes de um negócio no Pipedrive.

    Parâmetros:
    - id (str): ID do negócio.
    - start (int, opcional): Paginação inicial.
    - limit (int, opcional): Número de itens por página.
    - api_token (str): Token de API para validar as requisições. Para mais informações: 
      https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference
    - company_domain (str): Domínio da empresa. Para mais informações: 
      https://pipedrive.readme.io/docs/how-to-get-the-company-domain

    Retorna:
    - pd.DataFrame: Um DataFrame contendo os participantes do negócio.
    """
    api_token = check_api_token(api_token)
    
    params = {
        'start': start if start is not None else 0,
        'limit': limit if limit is not None else 500
    }

    params = clear_list(params)

    url = f'https://{company_domain}.pipedrive.com/v1/deals/{id}/participants?'
    url += prepare_url_parameters_(params)
    url += f'&api_token={api_token}'
    
    return get_all_(url)




def deals_get_permittedusers(id, access_level=None, api_token=None, company_domain='api'):
    """
    Função para listar os usuários permitidos em um negócio no Pipedrive.

    Parâmetros:
    - id (str): ID do negócio.
    - access_level (int, opcional): Nível de acesso permitido. 1 = Leitura, 2 = Escrita, 3 = Leitura+Escrita.
    - api_token (str): Token de API para validar as requisições. Para mais informações: 
      https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference
    - company_domain (str): Domínio da empresa. Para mais informações: 
      https://pipedrive.readme.io/docs/how-to-get-the-company-domain

    Retorna:
    - pd.DataFrame: Um DataFrame contendo os usuários permitidos do negócio.
    """
    api_token = check_api_token(api_token)
    params = {
        'access_level': access_level
    }

    params = clear_list(params)

    url = f'https://{company_domain}.pipedrive.com/v1/deals/{id}/permittedUsers?'
    url += prepare_url_parameters_(params)
    url += f'&api_token={api_token}'
    
    return get_all_(url)

def deals_get_persons(id, start=None, limit=None, api_token=None, company_domain='api'):
    """
    Função para listar todas as pessoas associadas a um negócio no Pipedrive.

    Parâmetros:
    - id (str): ID do negócio.
    - start (int, opcional): Paginação inicial.
    - limit (int, opcional): Número de itens por página.
    - api_token (str): Token de API para validar as requisições. Para mais informações: 
      https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference
    - company_domain (str): Domínio da empresa. Para mais informações: 
      https://pipedrive.readme.io/docs/how-to-get-the-company-domain

    Retorna:
    - pd.DataFrame: Um DataFrame contendo as pessoas associadas ao negócio.
    """
    api_token = check_api_token(api_token)
    
    params = {
        'start': start if start is not None else 0,
        'limit': limit if limit is not None else 500
    }

    params = clear_list(params)

    url = f'https://{company_domain}.pipedrive.com/v1/deals/{id}/persons?'
    url += prepare_url_parameters_(params)
    url += f'&api_token={api_token}'
    
    return get_all_(url)




def deals_get_products(id, start=None, limit=None, include_product_data=None, api_token=None, company_domain='api'):
    """
    Função para listar os produtos anexados a um negócio no Pipedrive.

    Parâmetros:
    - id (str): ID do negócio.
    - start (int, opcional): Paginação inicial.
    - limit (int, opcional): Número de itens por página.
    - include_product_data (int, opcional): Buscar dados do produto junto com cada produto anexado (1) ou não (0, padrão).
    - api_token (str): Token de API para validar as requisições. Para mais informações: 
      https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference
    - company_domain (str): Domínio da empresa. Para mais informações: 
      https://pipedrive.readme.io/docs/how-to-get-the-company-domain

    Retorna:
    - pd.DataFrame: Um DataFrame contendo os produtos anexados ao negócio.
    """

    api_token = check_api_token(api_token)
    

    params = {
        'start': start if start is not None else 0,
        'limit': limit if limit is not None else 500,
        'include_product_data': include_product_data
    }


    params = clear_list(params)


    url = f'https://{company_domain}.pipedrive.com/v1/deals/{id}/products?'
    url += prepare_url_parameters_(params)
    url += f'&api_token={api_token}'
    
    return get_all_(url)



def deals_get_all(user_id=None, filter_id=None, stage_id=None, status=None, start=None, limit=None, sort=None, owned_by_you=None, api_token=None, company_domain='api'):
    """
    Função para obter todos os negócios do Pipedrive.

    Parâmetros:
    - user_id (int, opcional): ID do usuário. Se fornecido, apenas negócios correspondentes ao usuário serão retornados.
    - filter_id (int, opcional): ID do filtro a ser usado.
    - stage_id (int, opcional): ID do estágio. Se fornecido, apenas negócios neste estágio serão retornados.
    - status (str, opcional): Status dos negócios a serem retornados. Valores permitidos: 'open', 'won', 'lost', 'deleted', 'all_not_deleted'.
    - start (int, opcional): Início da paginação. Padrão é 0.
    - limit (int, opcional): Número de itens por página. Padrão é 500.
    - sort (str, opcional): Ordenação de campos, ex: 'field_name_1 ASC, field_name_2 DESC'.
    - owned_by_you (int, opcional): 0 ou 1. Se fornecido, apenas negócios de sua propriedade serão retornados.
    - api_token (str, opcional): Token de API para autenticação. Se não fornecido, será tratado.
    - company_domain (str, opcional): Domínio da empresa. Padrão é 'api'.

    Retorna:
    - pd.DataFrame: Um DataFrame contendo todos os negócios.
    """
    api_token = check_api_token(api_token)
    
    url = f'https://{company_domain}.pipedrive.com/v1/deals?api_token={api_token}'
    
    params = {
        'user_id': user_id,
        'filter_id': filter_id,
        'stage_id': stage_id,
        'status': status,
        'start': start if start is not None else 0,
        'limit': limit if limit is not None else 500,
        'sort': sort,
        'owned_by_you': owned_by_you
    }
    
    params = clear_list(params)
    
    url = f"{url}&{prepare_url_parameters_(params)}"
    
    return get_all_(url)



def deals_timeline(start_date, interval, amount, field_key, user_id=None, pipeline_id=None, filter_id=None, exclude_deals=None, totals_convert_currency=None, api_token=None, company_domain='api'):
    """
    Obtém a linha do tempo dos negócios no Pipedrive.

    Parâmetros:
    - start_date (str): Data em que o primeiro intervalo começa. Formato: YYYY-MM-DD.
    - interval (str): Tipo de intervalo. Opções: day, week, month, quarter.
    - amount (int): Número de intervalos, começando a partir de start_date.
    - field_key (str): Nome do campo de data pelo qual buscar os negócios.
    - user_id (int, opcional): Se fornecido, retorna apenas os negócios correspondentes ao usuário fornecido.
    - pipeline_id (int, opcional): Se fornecido, retorna apenas os negócios correspondentes ao pipeline fornecido.
    - filter_id (int, opcional): Se fornecido, retorna apenas os negócios correspondentes ao filtro fornecido.
    - exclude_deals (int, opcional): Se 1, exclui a lista de negócios, mas ainda retorna o resumo da linha do tempo. Opções: 0, 1.
    - totals_convert_currency (str, opcional): Código de 3 letras de uma moeda suportada. Se fornecido, os totais são convertidos para essa moeda.
    - api_token (str): Token da API necessário para validar as solicitações. Um usuário tem um token diferente para cada empresa.
      Para mais informações: <https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference>
    - company_domain (str): Domínio da empresa no Pipedrive. Para mais informações: <https://pipedrive.readme.io/docs/how-to-get-the-company-domain>

    Retorna:
    dict: Um objeto com a linha do tempo dos negócios.

    Exemplo de uso:
    deals_timeline(start_date='2023-01-01', interval='month', amount=3, field_key='close_date', api_token='seu_token_aqui', company_domain='sua_empresa')
    """
    api_token = check_api_token(api_token)

    url = f'https://{company_domain}.pipedrive.com/v1/deals/timeline'

    params = {
        'start_date': start_date,
        'interval': interval,
        'amount': amount,
        'field_key': field_key,
        'user_id': user_id,
        'pipeline_id': pipeline_id,
        'filter_id': filter_id,
        'exclude_deals': exclude_deals,
        'totals_convert_currency': totals_convert_currency,
        'api_token': api_token
    }

    params = {k: v for k, v in params.items() if v is not None}

    response = requests.get(url, params=params)

    return response.json()
 

def deals_update(id, title=None, value=None, currency=None, user_id=None, person_id=None, org_id=None, stage_id=None, status=None, probability=None, lost_reason=None, visible_to=None, customList=None, api_token=None, company_domain='api', return_type='complete'):
    """
    Atualiza um negócio no Pipedrive.

    Parâmetros:
    - id (str): ID do negócio.
    - title (str, opcional): Título do negócio.
    - value (float, opcional): Valor do negócio.
    - currency (str, opcional): Moeda do negócio. Aceita código de 3 caracteres.
    - user_id (int, opcional): ID do usuário que será marcado como o proprietário do negócio.
    - person_id (int, opcional): ID da pessoa associada ao negócio.
    - org_id (int, opcional): ID da organização associada ao negócio.
    - stage_id (int, opcional): ID do estágio no qual o negócio será colocado em um pipeline.
    - status (str, opcional): Status do negócio. Opções: open, won, lost, deleted.
    - probability (float, opcional): Porcentagem de probabilidade de sucesso do negócio.
    - lost_reason (str, opcional): Mensagem opcional sobre o motivo da perda do negócio (usada quando o status é "lost").
    - visible_to (int, opcional): Visibilidade do negócio. 1 = Proprietário e seguidores (privado), 3 = Empresa inteira (compartilhado).
    - customList (dict, opcional): Lista com campos personalizados. Exemplo: {'custom_field': 'abc'}.
    - api_token (str): Token da API necessário para validar as solicitações. Um usuário tem um token diferente para cada empresa.
      Para mais informações: <https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference>
    - company_domain (str): Domínio da empresa no Pipedrive. Para mais informações: <https://pipedrive.readme.io/docs/how-to-get-the-company-domain>
    - return_type (str, opcional): O retorno padrão é um objeto com todas as informações do processo, ou você pode definir como booleano (True = sucesso, False = erro).

    Retorna:
    dict ou bool: Um objeto com as informações do negócio atualizado ou um booleano se especificado.

    Exemplo de uso:
    deals_update(id='12345', title='Novo Título', api_token='seu_token_aqui', company_domain='sua_empresa')
    """
    api_token = check_api_token(api_token)

    url = f'https://{company_domain}.pipedrive.com/v1/deals/{id}'
    
    body = {
        'title': title,
        'value': value,
        'currency': currency,
        'user_id': user_id,
        'person_id': person_id,
        'org_id': org_id,
        'stage_id': stage_id,
        'status': status,
        'probability': probability,
        'lost_reason': lost_reason,
        'visible_to': visible_to
    }
    
    if isinstance(customList, dict):
        body.update(customList)

    body = {k: v for k, v in body.items() if v is not None}

    params = {'api_token': api_token}

    response = requests.put(url, json=body, params=params)

    if return_type == 'boolean':
        return response.status_code in [200, 201]
    else:
        return response.json()

def deals_update_merge(id, merge_with_id, api_token=None, company_domain='api', return_type='complete'):
    """
    Mescla dois negócios no Pipedrive.

    Parâmetros:
    - id (str): ID do negócio que será mesclado.
    - merge_with_id (str): ID do negócio com o qual o negócio será mesclado.
    - api_token (str): Token da API necessário para validar as solicitações. Um usuário tem um token diferente para cada empresa.
      Para mais informações: <https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference>
    - company_domain (str): Domínio da empresa no Pipedrive.
    - return_type (str, opcional): O retorno padrão é um objeto com todas as informações do processo, ou você pode definir como booleano (True = sucesso, False = erro).

    Retorna:
    dict ou bool: Um objeto com as informações da mesclagem ou um booleano se especificado.
    """
    api_token = check_api_token(api_token)

    url = f'https://{company_domain}.pipedrive.com/v1/deals/{id}/merge'

    body = {
        'merge_with_id': merge_with_id
    }

    params = {'api_token': api_token}

    response = requests.put(url, json=body, params=params)

    if return_type == 'boolean':
        return response.status_code in [200, 201]
    else:
        return response.json()

def deals_update_products(id, deal_product_id, item_price, quantity, discount_percentage=None, duration=None, product_variation_id=None, comments=None, enabled_flag=None, api_token=None, company_domain='api', return_type='complete'):
    """
    Atualiza os detalhes de um produto anexado a um negócio no Pipedrive.

    Parâmetros:
    - id (str): ID do negócio.
    - deal_product_id (str): ID do produto anexado ao negócio.
    - item_price (float): Preço do produto no negócio.
    - quantity (int): Quantidade do produto no negócio.
    - discount_percentage (float, opcional): Percentual de desconto.
    - duration (int, opcional): Duração do produto.
    - product_variation_id (str, opcional): ID da variação do produto.
    - comments (str, opcional): Comentários sobre o produto.
    - enabled_flag (int, opcional): Indica se o produto está ativado no negócio (0 ou 1).
    - api_token (str): Token da API necessário para validar as solicitações.
    - company_domain (str): Domínio da empresa no Pipedrive.
    - return_type (str, opcional): Retorno padrão é um objeto com as informações ou um booleano.

    Retorna:
    dict ou bool: Informações da atualização ou booleano.
    """
    api_token = check_api_token(api_token)

    url = f'https://{company_domain}.pipedrive.com/v1/deals/{id}/products/{deal_product_id}'

    body = {
        'item_price': item_price,
        'quantity': quantity,
        'discount_percentage': discount_percentage,
        'duration': duration,
        'product_variation_id': product_variation_id,
        'comments': comments,
        'enabled_flag': enabled_flag
    }

    body = {k: v for k, v in body.items() if v is not None}
    params = {'api_token': api_token}

    response = requests.put(url, json=body, params=params)

    if return_type == 'boolean':
        return response.status_code in [200, 201]
    else:
        return response.json()


def files_add(file, deal_id=None, person_id=None, org_id=None, product_id=None, activity_id=None, note_id=None, api_token=None, company_domain='api', return_type='complete'):
    """
    Adiciona um arquivo ao Pipedrive.

    Parâmetros:
    - file (str): Caminho e nome do arquivo que será enviado.
    - deal_id (str, opcional): ID do negócio ao qual o arquivo será associado.
    - person_id (str, opcional): ID da pessoa ao qual o arquivo será associado.
    - org_id (str, opcional): ID da organização ao qual o arquivo será associado.
    - product_id (str, opcional): ID do produto ao qual o arquivo será associado.
    - activity_id (str, opcional): ID da atividade ao qual o arquivo será associado.
    - note_id (str, opcional): ID da nota ao qual o arquivo será associado.
    - api_token (str): Token da API necessário para validar as solicitações.
    - company_domain (str): Domínio da empresa no Pipedrive.
    - return_type (str, opcional): Retorno padrão é um objeto com as informações ou booleano.

    Retorna:
    dict ou bool: Informações sobre o arquivo enviado ou um booleano.
    """
    api_token = check_api_token(api_token)

    url = f'https://{company_domain}.pipedrive.com/v1/files'

    files = {'file': open(file, 'rb')}

    body = {
        'deal_id': deal_id,
        'person_id': person_id,
        'org_id': org_id,
        'product_id': product_id,
        'activity_id': activity_id,
        'note_id': note_id
    }

    body = {k: v for k, v in body.items() if v is not None}
    params = {'api_token': api_token}

    response = requests.post(url, files=files, data=body, params=params)

    if return_type == 'boolean':
        return response.status_code in [200, 201]
    else:
        return response.json()


def files_delete(id, api_token=None, company_domain='api', return_type='complete'):
    """
    Exclui um arquivo no Pipedrive.

    Parâmetros:
    - id (str): ID do arquivo a ser excluído.
    - api_token (str): Token da API necessário para validar as solicitações.
    - company_domain (str): Domínio da empresa no Pipedrive.
    - return_type (str, opcional): Retorno padrão é um objeto com as informações ou booleano.

    Retorna:
    dict ou bool: Informações sobre a exclusão do arquivo ou um booleano.
    """
    api_token = check_api_token(api_token)

    url = f'https://{company_domain}.pipedrive.com/v1/files/{id}'

    params = {'api_token': api_token}

    response = requests.delete(url, params=params)

    if return_type == 'boolean':
        return response.status_code in [200, 201]
    else:
        return response.json()

def files_get(id, api_token=None, company_domain='api'):
    """
    Obtém um arquivo específico no Pipedrive.

    Parâmetros:
    - id (str): ID do arquivo a ser recuperado.
    - api_token (str): Token da API necessário para validar as solicitações.
    - company_domain (str): Domínio da empresa no Pipedrive.

    Retorna:
    dict: Um objeto contendo as informações do arquivo.
    """
    api_token = check_api_token(api_token)
    url = f'https://{company_domain}.pipedrive.com/v1/files/{id}'
    
    params = {'api_token': api_token}

    response = requests.get(url, params=params)
    return response.json()

def files_get_download(id, save, api_token=None, company_domain='api'):
    """
    Baixa um arquivo do Pipedrive.

    Parâmetros:
    - id (str): ID do arquivo a ser baixado.
    - save (str): Caminho e nome do arquivo para salvar o download.
    - api_token (str): Token da API necessário para validar as solicitações.
    - company_domain (str): Domínio da empresa no Pipedrive.

    Retorna:
    None: O arquivo será salvo no caminho especificado.
    """
    api_token = check_api_token(api_token)
    url = f'https://{company_domain}.pipedrive.com/v1/files/{id}/download'
    
    params = {'api_token': api_token}

    response = requests.get(url, params=params, stream=True)
    with open(save, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)


def files_get_all(start=None, limit=None, include_deleted_files=None, sort=None, api_token=None, company_domain='api'):
    """
    Função para obter todos os arquivos do Pipedrive.

    Parâmetros:
    - start (int, opcional): Início da paginação. Padrão é 0.
    - limit (int, opcional): Número de itens por página. Padrão é 500.
    - include_deleted_files (int, opcional): Incluir arquivos deletados (0 ou 1).
    - sort (str, opcional): Ordenação de campos, ex: 'field_name_1 ASC, field_name_2 DESC'.
    - api_token (str, opcional): Token de API para autenticação. Se não fornecido, será tratado.
    - company_domain (str, opcional): Domínio da empresa. Padrão é 'api'.

    Retorna:
    - pd.DataFrame: Um DataFrame contendo todos os arquivos.
    """
    api_token = check_api_token(api_token)
    
    url = f'https://{company_domain}.pipedrive.com/v1/files?api_token={api_token}'
    
    params = {
        'start': start if start is not None else 0,
        'limit': limit if limit is not None else 500,
        'include_deleted_files': include_deleted_files,
        'sort': sort
    }
    
    params = clear_list(params)
    
    url = f"{url}&{prepare_url_parameters_(params)}"
    
    return get_all_(url)


def files_remote(file_type, title, item_type, item_id, remote_location, api_token=None, company_domain='api', return_type='complete'):
    """
    Cria um arquivo remoto e o associa a um item no Pipedrive.

    Parâmetros:
    - file_type (str): O tipo de arquivo (gdoc, gslides, gsheet, etc.).
    - title (str): Título do arquivo.
    - item_type (str): Tipo de item (deal, organization, person).
    - item_id (str): ID do item ao qual o arquivo será associado.
    - remote_location (str): Localização remota (googledrive).
    - api_token (str): Token da API necessário para validar as solicitações.
    - company_domain (str): Domínio da empresa no Pipedrive.
    - return_type (str, opcional): Retorno padrão é um objeto ou booleano.


    Retorna:
    dict ou bool: Informações do arquivo remoto criado ou um booleano.
    """
    api_token = check_api_token(api_token)
    url = f'https://{company_domain}.pipedrive.com/v1/files/remote'
    
    body = {
        'file_type': file_type,
        'title': title,
        'item_type': item_type,
        'item_id': item_id,
        'remote_location': remote_location
    }

    body = {k: v for k, v in body.items() if v is not None}
    
    params = {'api_token': api_token}

    response = requests.post(url, json=body, params=params)

    if return_type == 'boolean':
        return response.status_code in [200, 201]
    else:
        return response.json()
    

def files_remotelink(item_type, item_id, remote_id, remote_location, api_token=None, company_domain='api', return_type='complete'):
    """
    Associa um arquivo remoto a um item no Pipedrive.

    Parâmetros:
    - item_type (str): Tipo de item (deal, organization, person).
    - item_id (str): ID do item ao qual o arquivo será associado.
    - remote_id (str): ID remoto do arquivo.
    - remote_location (str): Localização remota (googledrive).
    - api_token (str): Token da API necessário para validar as solicitações.
    - company_domain (str): Domínio da empresa no Pipedrive.
    - return_type (str, opcional): Retorno padrão é um objeto ou booleano.

    Retorna:
    dict ou bool: Informações do arquivo remoto associado ou um booleano.
    """
    api_token = check_api_token(api_token)
    url = f'https://{company_domain}.pipedrive.com/v1/files/remoteLink'
    
    body = {
        'item_type': item_type,
        'item_id': item_id,
        'remote_id': remote_id,
        'remote_location': remote_location
    }

    body = {k: v for k, v in body.items() if v is not None}
    
    params = {'api_token': api_token}

    response = requests.post(url, json=body, params=params)

    if return_type == 'boolean':
        return response.status_code in [200, 201]
    else:
        return response.json()

def files_update(id, name=None, description=None, api_token=None, company_domain='api', return_type='complete'):
    """
    Atualiza os detalhes de um arquivo no Pipedrive.

    Parâmetros:
    - id (str): ID do arquivo a ser atualizado.
    - name (str, opcional): Nome visível do arquivo.
    - description (str, opcional): Descrição do arquivo.
    - api_token (str): Token da API necessário para validar as solicitações.
    - company_domain (str): Domínio da empresa no Pipedrive.
    - return_type (str, opcional): Retorno padrão é um objeto ou booleano.

    Retorna:
    dict ou bool: Informações do arquivo atualizado ou um booleano.
    """
    api_token = check_api_token(api_token)
    url = f'https://{company_domain}.pipedrive.com/v1/files/{id}'
    
    body = {
        'name': name,
        'description': description
    }

    body = {k: v for k, v in body.items() if v is not None}
    
    params = {'api_token': api_token}

    response = requests.put(url, json=body, params=params)

    if return_type == 'boolean':
        return response.status_code in [200, 201]
    else:
        return response.json()

def filters_add(name, conditions, filter_type, api_token=None, company_domain='api', return_type='complete'):
    """
    Adiciona um novo filtro no Pipedrive.

    Parâmetros:
    - name (str): Nome do filtro.
    - conditions (dict): Condições do filtro como objeto JSON.
    - filter_type (str): Tipo do filtro (deals, org, people, products, activity).
    - api_token (str): Token da API necessário para validar as solicitações.
    - company_domain (str): Domínio da empresa no Pipedrive.
    - return_type (str, opcional): Retorno padrão é um objeto ou booleano.

    Retorna:
    dict ou bool: Informações do filtro adicionado ou um booleano.
    """
    api_token = check_api_token(api_token)
    url = f'https://{company_domain}.pipedrive.com/v1/filters'
    
    body = {
        'name': name,
        'conditions': conditions,
        'type': filter_type
    }

    body = {k: v for k, v in body.items() if v is not None}
    
    params = {'api_token': api_token}

    response = requests.post(url, json=body, params=params)

    if return_type == 'boolean':
        return response.status_code in [200, 201]
    else:
        return response.json()

def filters_delete(id, api_token=None, company_domain='api', return_type='complete'):
    """
    Exclui um filtro no Pipedrive.

    Parâmetros:
    - id (str): ID do filtro a ser excluído.
    - api_token (str): Token da API necessário para validar as solicitações.
    - company_domain (str): Domínio da empresa no Pipedrive.
    - return_type (str, opcional): Retorno padrão é um objeto ou booleano.

    Retorna:
    dict ou bool: Informações sobre a exclusão do filtro ou um booleano.
    """
    api_token = check_api_token(api_token)
    url = f'https://{company_domain}.pipedrive.com/v1/filters/{id}'
    
    params = {'api_token': api_token}

    response = requests.delete(url, params=params)

    if return_type == 'boolean':
        return response.status_code in [200, 201]
    else:
        return response.json()

def filters_delete_multiple(ids, api_token=None, company_domain='api', return_type='complete'):
    """
    Função para deletar múltiplos filtros em massa no Pipedrive.

    Parâmetros:
    - ids (str): IDs de filtros separados por vírgulas para deletar.
    - api_token (str, opcional): Token de API para autenticação. Se não fornecido, será tratado.
    - company_domain (str, opcional): Domínio da empresa. Padrão é 'api'.
    - return_type (str, opcional): O retorno padrão é 'complete' com todas as informações do processo,
      ou você pode definir 'boolean' para sucesso (TRUE) ou erro (FALSE).

    Retorna:
    - Se 'complete', retorna um dicionário com as informações do processo.
    - Se 'boolean', retorna True para sucesso ou False para falha.
    """
    api_token = check_api_token_(api_token)
    
    url = f'https://{company_domain}.pipedrive.com/v1/filters?api_token={api_token}'
    
    bodyList = {'ids': ids}
    
    response = requests.delete(url, json=bodyList)
    
    if return_type == 'boolean':
        return response.status_code in [200, 201]
    else:
        return response.json()

def filters_get(id, api_token=None, company_domain='api'):
    """
    Função para obter um filtro específico no Pipedrive, incluindo suporte para paginação.

    Parâmetros:
    - id (str): ID do filtro a ser buscado.
    - api_token (str, opcional): Token de API para autenticação.
    - company_domain (str, opcional): Domínio da empresa. Padrão é 'api'.

    Retorna:
    - Lista com todas as informações do filtro.
    """
    api_token = check_api_token(api_token)
    
    url = f'https://{company_domain}.pipedrive.com/v1/filters/{id}?api_token={api_token}'
    
  
    return get_all_(url)


def filters_get_all(type=None, api_token=None, company_domain='api'):
    """
    Função para obter todos os filtros do Pipedrive, incluindo suporte para paginação.

    Parâmetros:
    - type (str, opcional): Tipo de filtros a buscar (deals, org, people, products, activity).
    - api_token (str, opcional): Token de API para autenticação.
    - company_domain (str, opcional): Domínio da empresa. Padrão é 'api'.

    Retorna:
    - Lista com todos os filtros disponíveis.
    """
    api_token = check_api_token(api_token)
    
    url = f'https://{company_domain}.pipedrive.com/v1/filters?api_token={api_token}'
    
    if type:
        url += f'&type={type}'
    
    return get_all_(url)

def globalmessages_delete(id, api_token=None, company_domain='api', return_type='complete'):
    """
    Função para descartar uma mensagem global no Pipedrive.

    Parâmetros:
    - id (str): ID da mensagem global a ser descartada.
    - api_token (str): Token de API para validar as requisições. Para mais informações:
      https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference
    - company_domain (str): Domínio da empresa. Para mais informações:
      https://pipedrive.readme.io/docs/how-to-get-the-company-domain
    - return_type (str): O retorno padrão é um objeto completo com as informações do processo, ou você pode definir como booleano
      (TRUE = sucesso, FALSE = erro).

    Retorna:
    - Retorno personalizável. O padrão é um objeto completo da resposta, ou um valor booleano baseado no sucesso ou falha da operação.
    """
    api_token = check_api_token(api_token)
    
    url = f'https://{company_domain}.pipedrive.com/v1/globalMessages/{id}?api_token={api_token}'
    
    r = requests.delete(url)
    
    if return_type == 'boolean':
        return r.status_code in [200, 201]
    else:
        return r.json() if r.status_code in [200, 201] else r.text


def globalmessages_get(limit=None, api_token=None, company_domain='api'):
    """
    Função para obter mensagens globais do Pipedrive.

    Parâmetros:
    - limit (int, opcional): Número de mensagens a serem retornadas, de 1 a 100. O padrão é 1.
    - api_token (str): Token de API para validar as requisições. Para mais informações: 
      https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference
    - company_domain (str): Domínio da empresa. Para mais informações: 
      https://pipedrive.readme.io/docs/how-to-get-the-company-domain

    Retorna:
    - pd.DataFrame: Um DataFrame contendo as mensagens globais do Pipedrive.
    """
    api_token = check_api_token(api_token)
    
    limit = 1 if limit is None else limit
    
    url = f'https://{company_domain}.pipedrive.com/v1/globalMessages?limit={limit}&api_token={api_token}'
    
    return get_all_(url)

def mailmessages_get(id, include_body=None, api_token=None, company_domain='api'):
    """
    Função para obter uma mensagem de e-mail do Pipedrive.

    Parâmetros:
    - id (str): ID da mensagem de e-mail a ser buscada.
    - include_body (int, opcional): Incluir ou não o corpo completo da mensagem. 0 = Não incluir, 1 = Incluir.
    - api_token (str): Token de API para validar as requisições. Para mais informações:
      https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference
    - company_domain (str): Domínio da empresa. Para mais informações:
      https://pipedrive.readme.io/docs/how-to-get-the-company-domain

    Retorna:
    - pd.DataFrame: Um DataFrame contendo os dados da mensagem de e-mail.
    """
    api_token = check_api_token(api_token)
    
    params = {
        'include_body': include_body
    }

    params = clear_list(params)

    url = f'https://{company_domain}.pipedrive.com/v1/mailbox/mailMessages/{id}?'
    url += prepare_url_parameters_(params)
    url += f'&api_token={api_token}'
    
    return get_all_(url)


def mailthreads_delete(id, api_token=None, company_domain='api', return_type='complete'):
    """
    Função para deletar um thread de e-mail no Pipedrive.

    Parâmetros:
    - id (str): ID do thread de e-mail a ser deletado.
    - api_token (str): Token de API para validar as requisições. Para mais informações:
      https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference
    - company_domain (str): Domínio da empresa. Para mais informações:
      https://pipedrive.readme.io/docs/how-to-get-the-company-domain
    - return_type (str): O retorno padrão é um objeto completo com as informações do processo, ou você pode definir como booleano
      (True = sucesso, False = erro).

    Retorna:
    - Retorno personalizável. O padrão é um objeto completo da resposta ou um valor booleano baseado no sucesso ou falha da operação.
    """
    api_token = check_api_token(api_token)
    
    url = f'https://{company_domain}.pipedrive.com/v1/mailbox/mailThreads/{id}?api_token={api_token}'
    
    r = requests.delete(url)
    
    if return_type == 'boolean':
        return r.status_code in [200, 201]
    else:
        return r.json() if r.status_code in [200, 201] else r.text

def mailthreads_get(id, api_token=None, company_domain='api'):
    """
    Função para obter um thread de e-mail do Pipedrive.

    Parâmetros:
    - id (str): ID do thread de e-mail a ser buscado.
    - api_token (str): Token de API para validar as requisições. Para mais informações:
      https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference
    - company_domain (str): Domínio da empresa. Para mais informações:
      https://pipedrive.readme.io/docs/how-to-get-the-company-domain

    Retorna:
    - pd.DataFrame: Um DataFrame contendo os dados do thread de e-mail.
    """
    api_token = check_api_token(api_token)
    
    url = f'https://{company_domain}.pipedrive.com/v1/mailbox/mailThreads/{id}?api_token={api_token}'
    
    return get_all_(url)


def mailthreads_get_mailmessages(id, api_token=None, company_domain='api'):
    """
    Função para obter todas as mensagens de e-mail de um thread no Pipedrive.

    Parâmetros:
    - id (str): ID do thread de e-mail.
    - api_token (str): Token de API para validar as requisições. Para mais informações:
      https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference
    - company_domain (str): Domínio da empresa. Para mais informações:
      https://pipedrive.readme.io/docs/how-to-get-the-company-domain

    Retorna:
    - pd.DataFrame: Um DataFrame contendo todas as mensagens de e-mail do thread.
    """
    api_token = check_api_token(api_token)
    
    url = f'https://{company_domain}.pipedrive.com/v1/mailbox/mailThreads/{id}/mailMessages?api_token={api_token}'
    
    return get_all_(url)

def mailthreads_get_all(folder, start=None, limit=None, api_token=None, company_domain='api'):
    """
    Função para obter threads de e-mail no Pipedrive.

    Parâmetros:
    - folder (str): Tipo de pasta a ser buscada. Domínios possíveis: (inbox; drafts; sent; archive).
    - start (int, opcional): Índice do primeiro item. Se não definido, o padrão é 0.
    - limit (int, opcional): Quantidade de threads a buscar. Se não definido, o padrão é 50.
    - api_token (str): Token de API para validar as requisições. Para mais informações:
      https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference
    - company_domain (str): Domínio da empresa. Para mais informações:
      https://pipedrive.readme.io/docs/how-to-get-the-company-domain

    Retorna:
    - pd.DataFrame: Um DataFrame contendo os threads de e-mail.
    """
    api_token = check_api_token(api_token)
    
    params = {
        'folder': folder,
        'start': start if start is not None else 0,
        'limit': limit if limit is not None else 50
    }

    params = clear_list(params)

    url = f'https://{company_domain}.pipedrive.com/v1/mailbox/mailThreads?'
    url += prepare_url_parameters_(params)
    url += f'&api_token={api_token}'
    
    return get_all_(url)

def mailthreads_update(id, deal_id=None, shared_flag=None, read_flag=None, archived_flag=None, api_token=None, company_domain='api', return_type='complete'):
    """
    Função para atualizar os detalhes de um thread de e-mail no Pipedrive.

    Parâmetros:
    - id (str): ID do thread de e-mail.
    - deal_id (str, opcional): ID do negócio associado a este thread.
    - shared_flag (int, opcional): Se o thread é compartilhado com outros usuários da empresa. (0; 1)
    - read_flag (int, opcional): Se o thread foi lido ou não. (0; 1)
    - archived_flag (int, opcional): Se o thread está arquivado ou não. Pode arquivar apenas threads na pasta Inbox. (0; 1)
    - api_token (str): Token de API para validar as requisições. Para mais informações:
      https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference
    - company_domain (str): Domínio da empresa. Para mais informações:
      https://pipedrive.readme.io/docs/how-to-get-the-company-domain
    - return_type (str): O retorno padrão é um objeto completo com as informações do processo, ou você pode definir como booleano
      (True = sucesso, False = erro).

    Retorna:
    - Retorno personalizável. O padrão é um objeto completo da resposta ou um valor booleano baseado no sucesso ou falha da operação.
    """
    api_token = check_api_token(api_token)
    
    url = f'https://{company_domain}.pipedrive.com/v1/mailbox/mailThreads/{id}?api_token={api_token}'
    
    body = {
        'deal_id': deal_id,
        'shared_flag': shared_flag,
        'read_flag': read_flag,
        'archived_flag': archived_flag
    }

    body = clear_list(body)
    
    r = requests.put(url, json=body)
    
    if return_type == 'boolean':
        return r.status_code in [200, 201]
    else:
        return r.json() if r.status_code in [200, 201] else r.text

def mailthreads_update(id, deal_id=None, shared_flag=None, read_flag=None, archived_flag=None, api_token=None, company_domain='api', return_type='complete'):
    """
    Função para atualizar os detalhes de um thread de e-mail no Pipedrive.

    Parâmetros:
    - id (str): ID do thread de e-mail.
    - deal_id (str, opcional): ID do negócio associado a este thread.
    - shared_flag (int, opcional): Se o thread é compartilhado com outros usuários da empresa. (0; 1)
    - read_flag (int, opcional): Se o thread foi lido ou não. (0; 1)
    - archived_flag (int, opcional): Se o thread está arquivado ou não. Pode arquivar apenas threads na pasta Inbox. (0; 1)
    - api_token (str): Token de API para validar as requisições. Para mais informações:
      https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference
    - company_domain (str): Domínio da empresa. Para mais informações:
      https://pipedrive.readme.io/docs/how-to-get-the-company-domain
    - return_type (str): O retorno padrão é um objeto completo com as informações do processo, ou você pode definir como booleano
      (True = sucesso, False = erro).

    Retorna:
    - Retorno personalizável. O padrão é um objeto completo da resposta ou um valor booleano baseado no sucesso ou falha da operação.
    """

    api_token = check_api_token(api_token)
    

    url = f'https://{company_domain}.pipedrive.com/v1/mailbox/mailThreads/{id}?api_token={api_token}'
    
    body = {
        'deal_id': deal_id,
        'shared_flag': shared_flag,
        'read_flag': read_flag,
        'archived_flag': archived_flag
    }


    body = clear_list(body)
    
    r = requests.put(url, json=body)
    
    if return_type == 'boolean':
        return r.status_code in [200, 201]
    else:
        return r.json() if r.status_code in [200, 201] else r.text

def notes_add(content, deal_id=None, person_id=None, org_id=None, add_time=None, pinned_to_deal_flag=None, pinned_to_organization_flag=None, pinned_to_person_flag=None, api_token=None, company_domain='api', return_type='complete'):
    """
    Função para adicionar uma nota no Pipedrive.

    Parâmetros:
    - content (str): Conteúdo da nota em formato HTML.
    - deal_id (str, opcional): ID do negócio ao qual a nota será anexada.
    - person_id (str, opcional): ID da pessoa à qual a nota será anexada.
    - org_id (str, opcional): ID da organização à qual a nota será anexada.
    - add_time (str, opcional): Data e hora de criação da nota em UTC. Exemplo de formato: YYYY-MM-DD HH:MM:SS.
    - pinned_to_deal_flag (int, opcional): Se a nota está vinculada a um negócio. (0; 1)
    - pinned_to_organization_flag (int, opcional): Se a nota está vinculada a uma organização. (0; 1)
    - pinned_to_person_flag (int, opcional): Se a nota está vinculada a uma pessoa. (0; 1)
    - api_token (str): Token de API para validar as requisições.
    - company_domain (str): Domínio da empresa no Pipedrive.
    - return_type (str): O retorno padrão é um objeto completo com as informações do processo ou um valor booleano.

    Retorna:
    - Retorno personalizável. O padrão é um objeto completo da resposta ou um valor booleano baseado no sucesso ou falha da operação.
    """


    api_token = check_api_token(api_token)


    url = f'https://{company_domain}.pipedrive.com/v1/notes?api_token={api_token}'


    body = {
        'content': content,
        'deal_id': deal_id,
        'person_id': person_id,
        'org_id': org_id,
        'add_time': add_time,
        'pinned_to_deal_flag': pinned_to_deal_flag,
        'pinned_to_organization_flag': pinned_to_organization_flag,
        'pinned_to_person_flag': pinned_to_person_flag
    }

    body = clear_list(body)

    try:

        r = requests.post(url, json=body)

        if return_type == 'boolean':
            return r.status_code in [200, 201]
        else:
            return r.json() if r.status_code in [200, 201] else r.text

    except requests.exceptions.RequestException as e:
        return f"Erro ao fazer a requisição: {e}"

def notes_delete(id, api_token=None, company_domain='api', return_type='complete'):
    """
    Função para deletar uma nota no Pipedrive.

    Parâmetros:
    - id (str): ID da nota.
    - api_token (str): Token de API para validar as requisições. Para mais informações:
      https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference
    - company_domain (str): Domínio da empresa no Pipedrive.
    - return_type (str): O retorno padrão é um objeto completo com as informações do processo ou um valor booleano.

    Retorna:
    - Retorno personalizável. O padrão é um objeto completo da resposta ou um valor booleano baseado no sucesso ou falha da operação.
    """

    if not id:
        raise ValueError("O parâmetro 'id' é obrigatório.")

    api_token = check_api_token(api_token)

    url = f'https://{company_domain}.pipedrive.com/v1/notes/{id}?api_token={api_token}'

    try:
        r = requests.delete(url)

        if return_type == 'boolean':
            return r.status_code in [200, 201]
        else:
            return r.json() if r.status_code in [200, 201] else r.text

    except requests.exceptions.RequestException as e:
        return f"Erro ao fazer a requisição: {e}"

def notes_get(id, api_token=None, company_domain='api'):
    """
    Função para obter uma nota específica no Pipedrive.

    Parâmetros:
    - id (str): ID da nota.
    - api_token (str): Token de API para validar as requisições. Para mais informações:
      https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference
    - company_domain (str): Domínio da empresa no Pipedrive.

    Retorna:
    - pd.DataFrame: Um DataFrame contendo as informações da nota.
    """

    if not id:
        raise ValueError("O parâmetro 'id' é obrigatório.")

    api_token = check_api_token(api_token)

    url = f'https://{company_domain}.pipedrive.com/v1/notes/{id}?api_token={api_token}'

    return get_all_(url)


def notes_get_all(user_id=None, deal_id=None, person_id=None, org_id=None, start=None, limit=None, sort=None, start_date=None, end_date=None, pinned_to_deal_flag=None, pinned_to_organization_flag=None, pinned_to_person_flag=None, api_token=None, company_domain='api'):
    """
    Função para obter todas as notas do Pipedrive.

    Parâmetros:
    - user_id (str, opcional): ID do usuário cujas notas serão buscadas. Se omitido, retorna notas de todos os usuários.
    - deal_id (str, opcional): ID do negócio cujas notas serão buscadas. Se omitido, retorna notas de todos os negócios.
    - person_id (str, opcional): ID da pessoa cujas notas serão buscadas. Se omitido, retorna notas de todas as pessoas.
    - org_id (str, opcional): ID da organização cujas notas serão buscadas. Se omitido, retorna notas de todas as organizações.
    - start (int, opcional): Início da paginação.
    - limit (int, opcional): Número de itens por página.
    - sort (str, opcional): Nome dos campos e modo de ordenação (ex: "field_name_1 ASC, field_name_2 DESC").
    - start_date (str, opcional): Data de início no formato YYYY-MM-DD.
    - end_date (str, opcional): Data final no formato YYYY-MM-DD.
    - pinned_to_deal_flag (int, opcional): Filtra as notas com status de vinculação ao negócio. (0; 1)
    - pinned_to_organization_flag (int, opcional): Filtra as notas com status de vinculação à organização. (0; 1)
    - pinned_to_person_flag (int, opcional): Filtra as notas com status de vinculação à pessoa. (0; 1)
    - api_token (str): Token de API para validar as requisições.
    - company_domain (str): Domínio da empresa no Pipedrive.

    Retorna:
    - pd.DataFrame: Um DataFrame contendo as notas.
    """

    api_token = check_api_token(api_token)

    params = {
        'user_id': user_id,
        'deal_id': deal_id,
        'person_id': person_id,
        'org_id': org_id,
        'start': start if start is not None else 0,
        'limit': limit if limit is not None else 500,
        'sort': sort,
        'start_date': start_date,
        'end_date': end_date,
        'pinned_to_deal_flag': pinned_to_deal_flag,
        'pinned_to_organization_flag': pinned_to_organization_flag,
        'pinned_to_person_flag': pinned_to_person_flag
    }

    params = clear_list(params)

    url = f'https://{company_domain}.pipedrive.com/v1/notes?'
    url += prepare_url_parameters_(params)
    url += f'&api_token={api_token}'

    return get_all_(url)

def notes_update(id, content, deal_id=None, person_id=None, org_id=None, add_time=None, pinned_to_deal_flag=None, pinned_to_organization_flag=None, pinned_to_person_flag=None, api_token=None, company_domain='api', return_type='complete'):
    """
    Função para atualizar uma nota no Pipedrive.

    Parâmetros:
    - id (str): ID da nota.
    - content (str): Conteúdo da nota em formato HTML.
    - deal_id (str, opcional): ID do negócio ao qual a nota será anexada.
    - person_id (str, opcional): ID da pessoa à qual a nota será anexada.
    - org_id (str, opcional): ID da organização à qual a nota será anexada.
    - add_time (str, opcional): Data e hora de criação da nota em UTC (formato: YYYY-MM-DD HH:MM:SS).
    - pinned_to_deal_flag (int, opcional): Status de vinculação da nota ao negócio. (0; 1)
    - pinned_to_organization_flag (int, opcional): Status de vinculação da nota à organização. (0; 1)
    - pinned_to_person_flag (int, opcional): Status de vinculação da nota à pessoa. (0; 1)
    - api_token (str): Token de API para validar as requisições.
    - company_domain (str): Domínio da empresa no Pipedrive.
    - return_type (str): O retorno padrão é um objeto completo com as informações do processo ou um valor booleano.

    Retorna:
    - Retorno personalizável. O padrão é um objeto completo da resposta ou um valor booleano baseado no sucesso ou falha da operação.
    """

    api_token = check_api_token(api_token)

    url = f'https://{company_domain}.pipedrive.com/v1/notes/{id}?api_token={api_token}'

    body = {
        'content': content,
        'deal_id': deal_id,
        'person_id': person_id,
        'org_id': org_id,
        'add_time': add_time,
        'pinned_to_deal_flag': pinned_to_deal_flag,
        'pinned_to_organization_flag': pinned_to_organization_flag,
        'pinned_to_person_flag': pinned_to_person_flag
    }

    body = clear_list(body)

    try:
        r = requests.put(url, json=body)
        if return_type == 'boolean':
            return r.status_code in [200, 201]
        else:
            return r.json() if r.status_code in [200, 201] else r.text

    except requests.exceptions.RequestException as e:
        return f"Erro ao fazer a requisição: {e}"



def organizationfields_delete(id, api_token=None, company_domain='api', return_type='complete'):
    """
    Função para deletar um campo de organização no Pipedrive.

    Parâmetros:
    - id (str): ID do campo a ser deletado.
    - api_token (str): Token de API para validar as requisições.
    - company_domain (str): Domínio da empresa no Pipedrive.
    - return_type (str): O retorno padrão é um objeto completo com as informações do processo ou um valor booleano.

    Retorna:
    - Retorno personalizável. O padrão é um objeto completo da resposta ou um valor booleano baseado no sucesso ou falha da operação.
    """

    if not id:
        raise ValueError("O parâmetro 'id' é obrigatório.")

    api_token = check_api_token(api_token)

    url = f'https://{company_domain}.pipedrive.com/v1/organizationFields/{id}?api_token={api_token}'

    try:
        r = requests.delete(url)

        if return_type == 'boolean':
            return r.status_code in [200, 201]
        else:
            return r.json() if r.status_code in [200, 201] else r.text

    except requests.exceptions.RequestException as e:
        return f"Erro ao fazer a requisição: {e}"

import requests

def organizationfields_delete_multiple(ids, api_token=None, company_domain='api', return_type='complete'):
    """
    Função para deletar múltiplos campos de organização no Pipedrive em lote.

    Parâmetros:
    - ids (str): IDs dos campos a serem deletados, separados por vírgula.
    - api_token (str): Token de API para validar as requisições.
    - company_domain (str): Domínio da empresa no Pipedrive.
    - return_type (str): O retorno padrão é um objeto completo com as informações do processo ou um valor booleano.

    Retorna:
    - Retorno personalizável. O padrão é um objeto completo da resposta ou um valor booleano baseado no sucesso ou falha da operação.
    """

    if not ids:
        raise ValueError("O parâmetro 'ids' é obrigatório.")

    api_token = check_api_token(api_token)

    url = f'https://{company_domain}.pipedrive.com/v1/organizationFields?api_token={api_token}'

    body = {
        'ids': ids
    }

    try:
        r = requests.delete(url, json=body)

        if return_type == 'boolean':
            return r.status_code in [200, 201]
        else:
            return r.json() if r.status_code in [200, 201] else r.text

    except requests.exceptions.RequestException as e:
        return f"Erro ao fazer a requisição: {e}"
def organizationfields_get(id, api_token=None, company_domain='api'):
    """
    Função para obter um campo de organização específico no Pipedrive.

    Parâmetros:
    - id (str): ID do campo a ser buscado.
    - api_token (str): Token de API para validar as requisições. Para mais informações:
      https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference
    - company_domain (str): Domínio da empresa no Pipedrive.

    Retorna:
    - pd.DataFrame: Um DataFrame contendo as informações do campo de organização.
    """

    if not id:
        raise ValueError("O parâmetro 'id' é obrigatório.")

    api_token = check_api_token(api_token)

    url = f'https://{company_domain}.pipedrive.com/v1/organizationFields/{id}?api_token={api_token}'

    return get_all_(url)

def organizationfields_get_all(api_token=None, company_domain='api'):
    """
    Função para obter todos os campos de organização no Pipedrive.

    Parâmetros:
    - api_token (str): Token de API para validar as requisições. Para mais informações:
      https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference
    - company_domain (str): Domínio da empresa no Pipedrive.

    Retorna:
    - pd.DataFrame: Um DataFrame contendo todos os campos de organização.
    """

    api_token = check_api_token(api_token)

    url = f'https://{company_domain}.pipedrive.com/v1/organizationFields?api_token={api_token}'

    return get_all_(url)

def organizationfields_update(id, name, options=None, api_token=None, company_domain='api', return_type='complete'):
    """
    Função para atualizar um campo de organização no Pipedrive.

    Parâmetros:
    - id (str): ID do campo a ser atualizado.
    - name (str): Nome do campo.
    - options (list, opcional): Quando o tipo do campo é set ou enum, as opções possíveis devem ser fornecidas como uma lista de dicionários.
      Exemplo: [{'id': 123, 'label': 'Existing Item'}, {'label': 'New Item'}].
    - api_token (str): Token de API para validar as requisições. Para mais informações:
      https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference
    - company_domain (str): Domínio da empresa no Pipedrive.
    - return_type (str): O retorno padrão é um objeto completo com as informações do processo ou um valor booleano.

    Retorna:
    - Retorno personalizável. O padrão é um objeto completo da resposta ou um valor booleano baseado no sucesso ou falha da operação.
    """

    if not id:
        raise ValueError("O parâmetro 'id' é obrigatório.")

    api_token = check_api_token(api_token)

    url = f'https://{company_domain}.pipedrive.com/v1/organizationFields/{id}?api_token={api_token}'

    body = {
        'name': name,
        'options': json.dumps(options) if options else None 
    }

    body = clear_list(body)

    try:
        r = requests.put(url, json=body)

        if return_type == 'boolean':
            return r.status_code in [200, 201]
        else:
            return r.json() if r.status_code in [200, 201] else r.text

    except requests.exceptions.RequestException as e:
        return f"Erro ao fazer a requisição: {e}"

def organizationrelationships_add(type, rel_owner_org_id, rel_linked_org_id, org_id=None, api_token=None, company_domain='api', return_type='complete'):
    """
    Função para criar um relacionamento de organização no Pipedrive.

    Parâmetros:
    - type (str): O tipo de relacionamento de organização. (parent; related)
    - rel_owner_org_id (str): O proprietário deste relacionamento. Se o tipo for 'parent', o proprietário é a organização mãe.
    - rel_linked_org_id (str): A organização vinculada neste relacionamento. Se o tipo for 'parent', a organização vinculada é a filha.
    - org_id (str, opcional): ID da organização base para os valores calculados retornados.
    - api_token (str): Token de API para validar as requisições. Para mais informações:
      https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference
    - company_domain (str): Domínio da empresa no Pipedrive.
    - return_type (str): O retorno padrão é um objeto completo com as informações do processo ou um valor booleano.

    Retorna:
    - Retorno personalizável. O padrão é um objeto completo da resposta ou um valor booleano baseado no sucesso ou falha da operação.
    """

    api_token = check_api_token(api_token)

    url = f'https://{company_domain}.pipedrive.com/v1/organizationRelationships?api_token={api_token}'

    body = {
        'org_id': org_id,
        'type': type,
        'rel_owner_org_id': rel_owner_org_id,
        'rel_linked_org_id': rel_linked_org_id
    }

    body = clear_list(body)

    try:
        r = requests.post(url, json=body)
        if return_type == 'boolean':
            return r.status_code in [200, 201]
        else:
            return r.json() if r.status_code in [200, 201] else r.text

    except requests.exceptions.RequestException as e:
        return f"Erro ao fazer a requisição: {e}"
    
def organizationrelationships_delete(id, api_token=None, company_domain='api', return_type='complete'):
    """
    Função para deletar um relacionamento de organização no Pipedrive.

    Parâmetros:
    - id (str): ID do relacionamento de organização a ser deletado.
    - api_token (str): Token de API para validar as requisições. Para mais informações:
      https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference
    - company_domain (str): Domínio da empresa no Pipedrive.
    - return_type (str): O retorno padrão é um objeto completo com as informações do processo ou um valor booleano.

    Retorna:
    - Retorno personalizável. O padrão é um objeto completo da resposta ou um valor booleano baseado no sucesso ou falha da operação.
    """

    if not id:
        raise ValueError("O parâmetro 'id' é obrigatório.")

    api_token = check_api_token(api_token)

    url = f'https://{company_domain}.pipedrive.com/v1/organizationRelationships/{id}?api_token={api_token}'

    try:
        r = requests.delete(url)
        if return_type == 'boolean':
            return r.status_code in [200, 201]
        else:
            return r.json() if r.status_code in [200, 201] else r.text

    except requests.exceptions.RequestException as e:
        return f"Erro ao fazer a requisição: {e}"


def organizationrelationships_get(id, org_id=None, api_token=None, company_domain='api'):
    """
    Função para obter um relacionamento de organização específico no Pipedrive.

    Parâmetros:
    - id (str): ID do relacionamento de organização.
    - org_id (str, opcional): ID da organização base para os valores calculados retornados.
    - api_token (str): Token de API para validar as requisições. Para mais informações:
      https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference
    - company_domain (str): Domínio da empresa no Pipedrive.

    Retorna:
    - pd.DataFrame: Um DataFrame contendo as informações do relacionamento de organização.
    """

    if not id:
        raise ValueError("O parâmetro 'id' é obrigatório.")

    api_token = check_api_token(api_token)

    params = {
        'org_id': org_id
    }


    params = clear_list(params)


    url = f'https://{company_domain}.pipedrive.com/v1/organizationRelationships/{id}?'
    url += prepare_url_parameters_(params)
    url += f'&api_token={api_token}'

    return get_all_(url)

def organizationrelationships_get_all(org_id, api_token=None, company_domain='api'):
    """
    Função para obter todos os relacionamentos de uma organização no Pipedrive.

    Parâmetros:
    - org_id (str): ID da organização para obter os relacionamentos.
    - api_token (str): Token de API para validar as requisições. Para mais informações:
      https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference
    - company_domain (str): Domínio da empresa no Pipedrive.

    Retorna:
    - pd.DataFrame: Um DataFrame contendo todos os relacionamentos da organização.
    """

    if not org_id:
        raise ValueError("O parâmetro 'org_id' é obrigatório.")

    api_token = check_api_token(api_token)

    params = {
        'org_id': org_id
    }

    params = clear_list(params)

    url = f'https://{company_domain}.pipedrive.com/v1/organizationRelationships?'
    url += prepare_url_parameters_(params)
    url += f'&api_token={api_token}'

    return get_all_(url)

def organizationrelationships_update(id, org_id=None, type=None, rel_owner_org_id=None, rel_linked_org_id=None, api_token=None, company_domain='api', return_type='complete'):
    """
    Função para atualizar um relacionamento de organização no Pipedrive.

    Parâmetros:
    - id (str): ID do relacionamento de organização.
    - org_id (str, opcional): ID da organização base para os valores calculados retornados.
    - type (str, opcional): Tipo de relacionamento da organização (parent; related).
    - rel_owner_org_id (str, opcional): O proprietário deste relacionamento. Se o tipo for 'parent', o proprietário é a organização mãe.
    - rel_linked_org_id (str, opcional): A organização vinculada neste relacionamento. Se o tipo for 'parent', a organização vinculada é a filha.
    - api_token (str): Token de API para validar as requisições.
    - company_domain (str): Domínio da empresa no Pipedrive.
    - return_type (str): O retorno padrão é um objeto completo com as informações do processo ou um valor booleano.

    Retorna:
    - Retorno personalizável. O padrão é um objeto completo da resposta ou um valor booleano baseado no sucesso ou falha da operação.
    """

    if not id:
        raise ValueError("O parâmetro 'id' é obrigatório.")

    api_token = check_api_token(api_token)

    url = f'https://{company_domain}.pipedrive.com/v1/organizationRelationships/{id}?api_token={api_token}'

    body = {
        'org_id': org_id,
        'type': type,
        'rel_owner_org_id': rel_owner_org_id,
        'rel_linked_org_id': rel_linked_org_id
    }

    body = clear_list(body)

    try:
        r = requests.put(url, json=body)

        if return_type == 'boolean':
            return r.status_code in [200, 201]
        else:
            return r.json() if r.status_code in [200, 201] else r.text

    except requests.exceptions.RequestException as e:
        return f"Erro ao fazer a requisição: {e}"

def organizations_add(name, owner_id=None, visible_to=None, add_time=None, customList=None, api_token=None, company_domain='api', return_type='complete'):
    """
    Função para adicionar uma organização no Pipedrive.

    Parâmetros:
    - name (str): Nome da organização.
    - owner_id (str, opcional): ID do usuário que será marcado como proprietário desta organização. Se omitido, será usado o ID do usuário autorizado.
    - visible_to (int, opcional): Visibilidade da organização. 1 = Proprietário e seguidores (privado); 3 = Empresa inteira (compartilhado).
    - add_time (str, opcional): Data e hora de criação da organização em UTC. Requer token de API de usuário administrador (formato: YYYY-MM-DD HH:MM:SS).
    - customList (dict, opcional): Dicionário com campos personalizados. Exemplo: {'custom_field': 'abc'}.
    - api_token (str): Token de API para validar as requisições.
    - company_domain (str): Domínio da empresa no Pipedrive.
    - return_type (str): O retorno padrão é um objeto completo com as informações do processo ou um valor booleano.

    Retorna:
    - Retorno personalizável. O padrão é um objeto completo da resposta ou um valor booleano baseado no sucesso ou falha da operação.
    """

    if not name:
        raise ValueError("O parâmetro 'name' é obrigatório.")

    api_token = check_api_token(api_token)

    url = f'https://{company_domain}.pipedrive.com/v1/organizations?api_token={api_token}'

    body = {
        'name': name,
        'owner_id': owner_id,
        'visible_to': visible_to,
        'add_time': add_time
    }

    if isinstance(customList, dict):
        body.update(customList)

    body = clear_list(body)

    try:
        r = requests.post(url, json=body)

        if return_type == 'boolean':
            return r.status_code in [200, 201]
        else:
            return r.json() if r.status_code in [200, 201] else r.text

    except requests.exceptions.RequestException as e:
        return f"Erro ao fazer a requisição: {e}"


def organizations_add_followers(id, user_id, api_token=None, company_domain='api', return_type='complete'):
    """
    Função para adicionar um seguidor a uma organização no Pipedrive.

    Parâmetros:
    - id (str): ID da organização.
    - user_id (str): ID do usuário a ser adicionado como seguidor.
    - api_token (str): Token de API para validar as requisições. Para mais informações:
      https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference
    - company_domain (str): Domínio da empresa no Pipedrive.
    - return_type (str): O retorno padrão é um objeto completo com as informações do processo ou um valor booleano.

    Retorna:
    - Retorno personalizável. O padrão é um objeto completo da resposta ou um valor booleano baseado no sucesso ou falha da operação.
    """

    if not id or not user_id:
        raise ValueError("Os parâmetros 'id' e 'user_id' são obrigatórios.")

    api_token = check_api_token(api_token)

    url = f'https://{company_domain}.pipedrive.com/v1/organizations/{id}/followers?api_token={api_token}'

    body = {
        'user_id': user_id
    }

    body = clear_list(body)

    try:
        r = requests.post(url, json=body)

        if return_type == 'boolean':
            return r.status_code in [200, 201]
        else:
            return r.json() if r.status_code in [200, 201] else r.text

    except requests.exceptions.RequestException as e:
        return f"Erro ao fazer a requisição: {e}"

import requests

def organizations_delete(id, api_token=None, company_domain='api', return_type='complete'):
    """
    Função para deletar uma organização no Pipedrive.

    Parâmetros:
    - id (str): ID da organização a ser deletada.
    - api_token (str): Token de API para validar as requisições. Para mais informações:
      https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference
    - company_domain (str): Domínio da empresa no Pipedrive.
    - return_type (str): O retorno padrão é um objeto completo com as informações do processo ou um valor booleano.

    Retorna:
    - Retorno personalizável. O padrão é um objeto completo da resposta ou um valor booleano baseado no sucesso ou falha da operação.
    """
    if not id:
        raise ValueError("O parâmetro 'id' é obrigatório.")

    api_token = check_api_token(api_token)

    url = f'https://{company_domain}.pipedrive.com/v1/organizations/{id}?api_token={api_token}'

    try:
        r = requests.delete(url)

        if return_type == 'boolean':
            return r.status_code in [200, 201]
        else:
            return r.json() if r.status_code in [200, 201] else r.text

    except requests.exceptions.RequestException as e:
        return f"Erro ao fazer a requisição: {e}"

import requests

def organizations_delete_followers(id, follower_id, api_token=None, company_domain='api', return_type='complete'):
    """
    Função para deletar um seguidor de uma organização no Pipedrive.

    Parâmetros:
    - id (str): ID da organização.
    - follower_id (str): ID do seguidor a ser removido.
    - api_token (str): Token de API para validar as requisições. Para mais informações:
      https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference
    - company_domain (str): Domínio da empresa no Pipedrive.
    - return_type (str): O retorno padrão é um objeto completo com as informações do processo ou um valor booleano.

    Retorna:
    - Retorno personalizável. O padrão é um objeto completo da resposta ou um valor booleano baseado no sucesso ou falha da operação.
    """

    if not id or not follower_id:
        raise ValueError("Os parâmetros 'id' e 'follower_id' são obrigatórios.")

    api_token = check_api_token(api_token)

    url = f'https://{company_domain}.pipedrive.com/v1/organizations/{id}/followers/{follower_id}?api_token={api_token}'

    try:
        r = requests.delete(url)
        if return_type == 'boolean':
            return r.status_code in [200, 201]
        else:
            return r.json() if r.status_code in [200, 201] else r.text

    except requests.exceptions.RequestException as e:
        return f"Erro ao fazer a requisição: {e}"


def organizations_delete_multiple(ids, api_token=None, company_domain='api', return_type='complete'):
    """
    Função para deletar múltiplas organizações em lote no Pipedrive.

    Parâmetros:
    - ids (str): IDs separados por vírgula das organizações que serão deletadas.
    - api_token (str): Token de API para validar as requisições. Para mais informações:
      https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference
    - company_domain (str): Domínio da empresa no Pipedrive.
    - return_type (str): O retorno padrão é um objeto completo com as informações do processo ou um valor booleano.

    Retorna:
    - Retorno personalizável. O padrão é um objeto completo da resposta ou um valor booleano baseado no sucesso ou falha da operação.
    """

    if not ids:
        raise ValueError("O parâmetro 'ids' é obrigatório.")

    api_token = check_api_token(api_token)

    url = f'https://{company_domain}.pipedrive.com/v1/organizations?api_token={api_token}'
    body = {
        'ids': ids
    }

    try:
        r = requests.delete(url, json=body)
        if return_type == 'boolean':
            return r.status_code in [200, 201]
        else:
            return r.json() if r.status_code in [200, 201] else r.text

    except requests.exceptions.RequestException as e:
        return f"Erro ao fazer a requisição: {e}"


def organizations_find(term, start=None, limit=None, api_token=None, company_domain='api'):
    """
    Função para encontrar organizações por nome no Pipedrive.

    Parâmetros:
    - term (str): Termo de busca para procurar organizações.
    - start (int, opcional): Paginação inicial.
    - limit (int, opcional): Número de itens por página.
    - api_token (str): Token de API para validar as requisições. Para mais informações:
      https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference
    - company_domain (str): Domínio da empresa no Pipedrive.

    Retorna:
    - pd.DataFrame: Um DataFrame contendo as organizações encontradas.
    """
    if not term:
        raise ValueError("O parâmetro 'term' é obrigatório.")

    api_token = check_api_token(api_token)

    params = {
        'term': term,
        'start': start if start is not None else 0,
        'limit': limit if limit is not None else 500
    }

    params = clear_list(params)
    url = f'https://{company_domain}.pipedrive.com/v1/organizations/find?'
    url += prepare_url_parameters_(params)
    url += f'&api_token={api_token}'
    return get_all_(url)


def organizations_get(id, api_token=None, company_domain='api'):
    """
    Função para obter os detalhes de uma organização no Pipedrive.

    Parâmetros:
    - id (str): ID da organização.
    - api_token (str): Token de API para validar as requisições. Para mais informações:
      https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference
    - company_domain (str): Domínio da empresa no Pipedrive.

    Retorna:
    - pd.DataFrame: Um DataFrame contendo os detalhes da organização.
    """

    if not id:
        raise ValueError("O parâmetro 'id' é obrigatório.")

    api_token = check_api_token(api_token)

    url = f'https://{company_domain}.pipedrive.com/v1/organizations/{id}?api_token={api_token}'

    return get_all_(url)

def organizations_get_activities(id, start=None, limit=None, done=None, exclude=None, api_token=None, company_domain='api'):
    """
    Função para listar as atividades associadas a uma organização no Pipedrive.

    Parâmetros:
    - id (str): ID da organização.
    - start (int, opcional): Paginação inicial.
    - limit (int, opcional): Número de itens por página.
    - done (int, opcional): 1 para atividades concluídas, 0 para atividades não concluídas. Se omitido, ambas são retornadas.
    - exclude (str, opcional): String com IDs de atividades separados por vírgula para serem excluídos do resultado.
    - api_token (str): Token de API para validar as requisições. Para mais informações:
      https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference
    - company_domain (str): Domínio da empresa no Pipedrive.

    Retorna:
    - pd.DataFrame: Um DataFrame contendo as atividades associadas à organização.
    """

    if not id:
        raise ValueError("O parâmetro 'id' é obrigatório.")

    api_token = check_api_token(api_token)


    params = {
        'start': start if start is not None else 0,
        'limit': limit if limit is not None else 500,
        'done': done,
        'exclude': exclude
    }


    params = clear_list(params)

    url = f'https://{company_domain}.pipedrive.com/v1/organizations/{id}/activities?'
    url += prepare_url_parameters_(params)
    url += f'&api_token={api_token}'

    return get_all_(url)

def organizations_get_deals(id, start=None, limit=None, status=None, sort=None, only_primary_association=None, api_token=None, company_domain='api'):
    """
    Função para listar os negócios associados a uma organização no Pipedrive.

    Parâmetros:
    - id (str): ID da organização.
    - start (int, opcional): Paginação inicial.
    - limit (int, opcional): Número de itens por página.
    - status (str, opcional): Status dos negócios a serem buscados (open; won; lost; deleted; all_not_deleted).
    - sort (str, opcional): Campo e ordem de classificação (ex: 'field_name ASC, field_name_2 DESC').
    - only_primary_association (int, opcional): 1 para buscar apenas negócios diretamente associados à organização, 0 para buscar todos.
    - api_token (str): Token de API para validar as requisições. Para mais informações:
      https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference
    - company_domain (str): Domínio da empresa no Pipedrive.

    Retorna:
    - pd.DataFrame: Um DataFrame contendo os negócios associados à organização.
    """

    if not id:
        raise ValueError("O parâmetro 'id' é obrigatório.")

    api_token = check_api_token(api_token)

    params = {
        'start': start if start is not None else 0,
        'limit': limit if limit is not None else 500,
        'status': status,
        'sort': sort,
        'only_primary_association': only_primary_association
    }

    params = clear_list(params)

    url = f'https://{company_domain}.pipedrive.com/v1/organizations/{id}/deals?'
    url += prepare_url_parameters_(params)
    url += f'&api_token={api_token}'

    return get_all_(url)

def organizations_get_files(id, start=None, limit=None, include_deleted_files=None, sort=None, api_token=None, company_domain='api'):
    """
    Função para listar os arquivos anexados a uma organização no Pipedrive.

    Parâmetros:
    - id (str): ID da organização.
    - start (int, opcional): Paginação inicial.
    - limit (int, opcional): Número de itens por página.
    - include_deleted_files (int, opcional): 1 para incluir arquivos deletados, 0 para não incluir.
    - sort (str, opcional): Campo e ordem de classificação (ex: 'field_name ASC, field_name_2 DESC').
    - api_token (str): Token de API para validar as requisições. Para mais informações:
      https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference
    - company_domain (str): Domínio da empresa no Pipedrive.

    Retorna:
    - pd.DataFrame: Um DataFrame contendo os arquivos associados à organização.
    """

    if not id:
        raise ValueError("O parâmetro 'id' é obrigatório.")

    api_token = check_api_token(api_token)

    params = {
        'start': start if start is not None else 0,
        'limit': limit if limit is not None else 500,
        'include_deleted_files': include_deleted_files,
        'sort': sort
    }
    params = clear_list(params)

    url = f'https://{company_domain}.pipedrive.com/v1/organizations/{id}/files?'
    url += prepare_url_parameters_(params)
    url += f'&api_token={api_token}'

    return get_all_(url)

def organizations_get_flow(id, start=None, limit=None, api_token=None, company_domain='api'):
    """
    Função para listar as atualizações sobre uma organização no Pipedrive.

    Parâmetros:
    - id (str): ID da organização.
    - start (int, opcional): Paginação inicial.
    - limit (int, opcional): Número de itens por página.
    - api_token (str): Token de API para validar as requisições. Para mais informações:
      https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference
    - company_domain (str): Domínio da empresa no Pipedrive.

    Retorna:
    - pd.DataFrame: Um DataFrame contendo as atualizações associadas à organização.
    """


    if not id:
        raise ValueError("O parâmetro 'id' é obrigatório.")

    api_token = check_api_token(api_token)


    params = {
        'start': start if start is not None else 0,
        'limit': limit if limit is not None else 500
    }

    params = clear_list(params)

    url = f'https://{company_domain}.pipedrive.com/v1/organizations/{id}/flow?'
    url += prepare_url_parameters_(params)
    url += f'&api_token={api_token}'

    return get_all_(url)


def organizations_get_followers(id, api_token=None, company_domain='api'):
    """
    Função para listar os seguidores de uma organização no Pipedrive.

    Parâmetros:
    - id (str): ID da organização.
    - api_token (str): Token de API para validar as requisições. Para mais informações:
      https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference
    - company_domain (str): Domínio da empresa no Pipedrive.

    Retorna:
    - pd.DataFrame: Um DataFrame contendo os seguidores da organização.
    """

    if not id:
        raise ValueError("O parâmetro 'id' é obrigatório.")

    api_token = check_api_token(api_token)

    url = f'https://{company_domain}.pipedrive.com/v1/organizations/{id}/followers?api_token={api_token}'

    return get_all_(url)

def organizations_get_mailmessages(id, start=None, limit=None, api_token=None, company_domain='api'):
    """
    Função para listar as mensagens de e-mail associadas a uma organização no Pipedrive.

    Parâmetros:
    - id (str): ID da organização.
    - start (int, opcional): Paginação inicial.
    - limit (int, opcional): Número de itens por página.
    - api_token (str): Token de API para validar as requisições. Para mais informações:
      https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference
    - company_domain (str): Domínio da empresa no Pipedrive.

    Retorna:
    - pd.DataFrame: Um DataFrame contendo as mensagens de e-mail associadas à organização.
    """
    if not id:
        raise ValueError("O parâmetro 'id' é obrigatório.")


    api_token = check_api_token(api_token)


    params = {
        'start': start if start is not None else 0,
        'limit': limit if limit is not None else 500
    }

    params = clear_list(params)

    url = f'https://{company_domain}.pipedrive.com/v1/organizations/{id}/mailMessages?'
    url += prepare_url_parameters_(params)
    url += f'&api_token={api_token}'

    return get_all_(url)



def organizations_get_permittedusers(id, access_level=None, api_token=None, company_domain='api'):
    """
    Função para listar os usuários permitidos para uma organização no Pipedrive.

    Parâmetros:
    - id (str): ID da organização.
    - access_level (int, opcional): Filtrar resultados pelo nível de acesso permitido (1 = Ler, 2 = Escrever, 3 = Ler + Escrever).
    - api_token (str): Token de API para validar as requisições. Para mais informações:
      https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference
    - company_domain (str): Domínio da empresa no Pipedrive.

    Retorna:
    - pd.DataFrame: Um DataFrame contendo os usuários permitidos.
    """

    if not id:
        raise ValueError("O parâmetro 'id' é obrigatório.")

    api_token = check_api_token(api_token)

    params = {
        'access_level': access_level
    }

    params = clear_list(params)

    url = f'https://{company_domain}.pipedrive.com/v1/organizations/{id}/permittedUsers?'
    url += prepare_url_parameters_(params)
    url += f'&api_token={api_token}'

    return get_all_(url)


def organizations_get_persons(id, start=None, limit=None, api_token=None, company_domain='api'):
    """
    Função para listar pessoas de uma organização no Pipedrive.

    Parâmetros:
    - id (str): ID da organização.
    - start (int, opcional): Paginação inicial. Padrão é None.
    - limit (int, opcional): Limite de itens por página. Padrão é None.
    - api_token (str): Token da API para autenticação. Necessário.
    - company_domain (str): Domínio da empresa no Pipedrive. Padrão é 'api'.

    Retorna:
    pd.DataFrame: DataFrame contendo as pessoas da organização.
    """
    api_token = check_api_token(api_token)

    url = 'https://{company_domain}.pipedrive.com/v1/organizations/{id}/persons?'

    bodyList = {
        'id': id,
        'start': 0 if start is None else start,
        'limit': 500 if limit is None else limit
    }

    bodyList = clear_list(bodyList)

    url = f"https://{company_domain}.pipedrive.com/v1/organizations/{id}/persons?"
    url += prepare_url_parameters_(bodyList)

    url = url.replace("{company_domain}", company_domain)
    url += f'&api_token={api_token}'

    return get_all_(url)

def organizations_get_all(user_id=None, filter_id=None, first_char=None, start=None, limit=None, sort=None, api_token=None, company_domain='api'):
    """
    Função para obter todas as organizações no Pipedrive.

    Parâmetros:
    - user_id (str, opcional): Se fornecido, apenas organizações pertencentes ao usuário serão retornadas.
    - filter_id (str, opcional): ID do filtro a ser utilizado.
    - first_char (str, opcional): Se fornecido, retorna organizações cujo nome começa com a letra especificada.
    - start (int, opcional): Paginação inicial. Padrão é None.
    - limit (int, opcional): Limite de itens por página. Padrão é None.
    - sort (str, opcional): Nome dos campos e modo de ordenação (ex: "field_name_1 ASC, field_name_2 DESC").
    - api_token (str): Token da API para autenticação. Necessário.
    - company_domain (str): Domínio da empresa no Pipedrive. Padrão é 'api'.

    Retorna:
    pd.DataFrame: DataFrame contendo as organizações.
    """
    api_token = check_api_token(api_token)

    url = 'https://{company_domain}.pipedrive.com/v1/organizations?'

    bodyList = {
        'user_id': user_id,
        'filter_id': filter_id,
        'first_char': first_char,
        'start': 0 if start is None else start,
        'limit': 500 if limit is None else limit,
        'sort': sort
    }

    bodyList = clear_list(bodyList)

    url += prepare_url_parameters_(bodyList)

    url = url.replace("{company_domain}", company_domain)
    url += f'&api_token={api_token}'

    return get_all_(url)


def organizations_update(id, name=None, owner_id=None, visible_to=None, custom_list=None, api_token=None, company_domain='api', return_type='complete'):
    """
    Função para atualizar uma organização no Pipedrive.

    Parâmetros:
    - id (str): ID da organização.
    - name (str, opcional): Nome da organização.
    - owner_id (int, opcional): ID do usuário que será marcado como proprietário da organização. Quando omitido, o usuário autorizado será usado.
    - visible_to (int, opcional): Visibilidade da organização. 1 = Dono e seguidores (privado); 3 = Toda a empresa (compartilhado).
    - custom_list (dict, opcional): Dicionário com campos personalizados. Exemplo: {'custom_field': 'abc'}.
    - api_token (str): Token da API para autenticação. Necessário.
    - company_domain (str): Domínio da empresa no Pipedrive. Padrão é 'api'.
    - return_type (str): O retorno padrão é um objeto completo ou pode ser definido como booleano ('complete' ou 'boolean').

    Retorna:
    - Dependendo do parâmetro return_type, retorna um DataFrame completo ou um booleano indicando sucesso ou falha.
    """
    api_token = check_api_token(api_token)

    url = 'https://{company_domain}.pipedrive.com/v1/organizations/{id}?'
    url = url.replace("{company_domain}", company_domain)
    url = url.replace("{id}", str(id))

    bodyList = {
        'name': name,
        'owner_id': owner_id,
        'visible_to': visible_to
    }

    if isinstance(custom_list, dict):
        bodyList.update(custom_list)

    bodyList = clear_list(bodyList)

    bodyList.pop('id', None)

    url += f'api_token={api_token}'

    response = requests.put(url, json=bodyList)

    if return_type == 'boolean':
        return response.status_code in [200, 201]
    else:
        return response.json()

def organizations_update_merge(id, merge_with_id, api_token=None, company_domain='api', return_type='complete'):
    """
    Função para mesclar duas organizações no Pipedrive.

    Parâmetros:
    - id (str): ID da organização que será mesclada.
    - merge_with_id (str): ID da organização com a qual a organização será mesclada.
    - api_token (str): Token da API para autenticação. Necessário.
    - company_domain (str): Domínio da empresa no Pipedrive. Padrão é 'api'.
    - return_type (str): O retorno padrão é um objeto completo ou pode ser definido como booleano ('complete' ou 'boolean').

    Retorna:
    - Dependendo do parâmetro return_type, retorna um objeto JSON completo ou um booleano indicando sucesso ou falha.
    """
    api_token = check_api_token(api_token)

    url = 'https://{company_domain}.pipedrive.com/v1/organizations/{id}/merge?'
    url = url.replace("{company_domain}", company_domain)
    url = url.replace("{id}", str(id))

    bodyList = {
        'merge_with_id': merge_with_id
    }

    bodyList = clear_list(bodyList)

    url += f'api_token={api_token}'

    response = requests.put(url, json=bodyList)
    if return_type == 'boolean':
        return response.status_code in [200, 201]
    else:
        return response.json()

def permissionsets_add(id, user_id, api_token=None, company_domain='api', return_type='complete'):
    """
    Função para adicionar uma atribuição de conjunto de permissões no Pipedrive.

    Parâmetros:
    - id (str): ID do conjunto de permissões.
    - user_id (str): ID do usuário.
    - api_token (str): Token da API para autenticação. Necessário.
    - company_domain (str): Domínio da empresa no Pipedrive. Padrão é 'api'.
    - return_type (str): O retorno padrão é um objeto completo ou pode ser definido como booleano ('complete' ou 'boolean').

    Retorna:
    - Dependendo do parâmetro return_type, retorna um objeto JSON completo ou um booleano indicando sucesso ou falha.
    """
    api_token = check_api_token(api_token)

    url = 'https://{company_domain}.pipedrive.com/v1/permissionSets/{id}/assignments?'
    url = url.replace("{company_domain}", company_domain)
    url = url.replace("{id}", str(id))

    bodyList = {
        'user_id': user_id
    }

    bodyList = clear_list(bodyList)

    url += f'api_token={api_token}'

    response = requests.post(url, json=bodyList)

    if return_type == 'boolean':
        return response.status_code in [200, 201]
    else:
        return response.json()

def permissionsets_delete(id, user_id, api_token=None, company_domain='api', return_type='complete'):
    """
    Função para deletar uma atribuição de conjunto de permissões no Pipedrive.

    Parâmetros:
    - id (str): ID do conjunto de permissões.
    - user_id (str): ID do usuário.
    - api_token (str): Token da API para autenticação. Necessário.
    - company_domain (str): Domínio da empresa no Pipedrive. Padrão é 'api'.
    - return_type (str): O retorno padrão é um objeto completo ou pode ser definido como booleano ('complete' ou 'boolean').

    Retorna:
    - Dependendo do parâmetro return_type, retorna um objeto JSON completo ou um booleano indicando sucesso ou falha.
    """
    api_token = check_api_token(api_token)

    url = 'https://{company_domain}.pipedrive.com/v1/permissionSets/{id}/assignments?'
    url = url.replace("{company_domain}", company_domain)
    url = url.replace("{id}", str(id))

    url += f'api_token={api_token}'

    response = requests.delete(url)

    if return_type == 'boolean':
        return response.status_code in [200, 201]
    else:
        return response.json()

def permissionsets_get(id, api_token=None, company_domain='api'):
    """
    Função para obter um conjunto de permissões do Pipedrive.

    Parâmetros:
    - id (str): ID do conjunto de permissões.
    - api_token (str): Token da API para autenticação. Necessário.
    - company_domain (str): Domínio da empresa no Pipedrive. Padrão é 'api'.

    Retorna:
    - pd.DataFrame: DataFrame contendo os dados do conjunto de permissões.
    """
    api_token = check_api_token(api_token)

    url = 'https://{company_domain}.pipedrive.com/v1/permissionSets/{id}?'
    url = url.replace("{company_domain}", company_domain)
    url = url.replace("{id}", str(id))
    url += f'api_token={api_token}'

    return get_all_(url)

def permissionsets_get_assignments(id, start=None, limit=None, api_token=None, company_domain='api'):
    """
    Função para listar atribuições de conjuntos de permissões no Pipedrive.

    Parâmetros:
    - id (str): ID do conjunto de permissões.
    - start (int, opcional): Paginação inicial. Padrão é None.
    - limit (int, opcional): Limite de itens por página. Padrão é None.
    - api_token (str): Token da API para autenticação. Necessário.
    - company_domain (str): Domínio da empresa no Pipedrive. Padrão é 'api'.

    Retorna:
    - pd.DataFrame: DataFrame contendo as atribuições do conjunto de permissões.
    """
    api_token = check_api_token(api_token)

    
    url = 'https://{company_domain}.pipedrive.com/v1/permissionSets/{id}/assignments?'
    url = url.replace("{company_domain}", company_domain)
    url = url.replace("{id}", str(id))

    
    bodyList = {
        'start': 0 if start is None else start,
        'limit': 500 if limit is None else limit
    }

    
    bodyList = clear_list(bodyList)

    
    url += prepare_url_parameters_(bodyList)

    
    url += f'&api_token={api_token}'

    
    return get_all_(url)


def permissionsets_get_all(api_token=None, company_domain='api'):
    """
    Função para obter todos os conjuntos de permissões no Pipedrive.

    Parâmetros:
    - api_token (str): Token da API para autenticação. Necessário.
    - company_domain (str): Domínio da empresa no Pipedrive. Padrão é 'api'.

    Retorna:
    - pd.DataFrame: DataFrame contendo todos os conjuntos de permissões.
    """
    
    api_token = check_api_token(api_token)

    
    url = 'https://{company_domain}.pipedrive.com/v1/permissionSets?'
    url = url.replace("{company_domain}", company_domain)

    
    url += f'api_token={api_token}'

    
    return get_all_(url)

def permissionsets_update(id, contents, api_token=None, company_domain='api', return_type='complete'):
    """
    Função para atualizar os detalhes de um conjunto de permissões no Pipedrive.

    Parâmetros:
    - id (str): ID do conjunto de permissões.
    - contents (str): Permissões que este conjunto contém como uma string JSON ou uma string comum separada por vírgulas.
    - api_token (str): Token da API para autenticação. Necessário.
    - company_domain (str): Domínio da empresa no Pipedrive. Padrão é 'api'.
    - return_type (str): O retorno padrão é um objeto completo ou pode ser definido como booleano ('complete' ou 'boolean').

    Retorna:
    - Dependendo do parâmetro return_type, retorna um objeto JSON completo ou um booleano indicando sucesso ou falha.
    """
    api_token = check_api_token(api_token)

    url = 'https://{company_domain}.pipedrive.com/v1/permissionSets/{id}?'
    url = url.replace("{company_domain}", company_domain)
    url = url.replace("{id}", str(id))

    bodyList = {
        'contents': contents
    }

    bodyList = clear_list(bodyList)

    url += f'api_token={api_token}'

    response = requests.put(url, json=bodyList)

    if return_type == 'boolean':
        return response.status_code in [200, 201]
    else:
        return response.json()


def personfields_add(name, field_type, options=None, api_token=None, company_domain='api', return_type='complete'):
    """
    Função para adicionar um novo campo de pessoa no Pipedrive.

    Parâmetros:
    - name (str): Nome do campo.
    - field_type (str): Tipo do campo. Exemplo: varchar, varchar_auto, text, double, monetary, etc.
    - options (str, opcional): Quando field_type for 'set' ou 'enum', as opções devem ser fornecidas como uma string JSON.
    - api_token (str): Token da API para autenticação. Necessário.
    - company_domain (str): Domínio da empresa no Pipedrive. Padrão é 'api'.
    - return_type (str): O retorno padrão é um objeto completo ou pode ser definido como booleano ('complete' ou 'boolean').

    Retorna:
    - Dependendo do parâmetro return_type, retorna um objeto JSON completo ou um booleano indicando sucesso ou falha.
    """
    api_token = check_api_token(api_token)

    url = 'https://{company_domain}.pipedrive.com/v1/personFields?'
    url = url.replace("{company_domain}", company_domain)

    bodyList = {
        'name': name,
        'field_type': field_type,
        'options': options
    }

    bodyList = clear_list(bodyList)

    url += f'api_token={api_token}'

    response = requests.post(url, json=bodyList)

    if return_type == 'boolean':
        return response.status_code in [200, 201]
    else:
        return response.json()

def personfields_delete(id, api_token=None, company_domain='api', return_type='complete'):
    """
    Função para deletar um campo de pessoa no Pipedrive.

    Parâmetros:
    - id (str): ID do campo a ser deletado.
    - api_token (str): Token da API para autenticação. Necessário.
    - company_domain (str): Domínio da empresa no Pipedrive. Padrão é 'api'.
    - return_type (str): O retorno padrão é um objeto completo ou pode ser definido como booleano ('complete' ou 'boolean').

    Retorna:
    - Dependendo do parâmetro return_type, retorna um objeto JSON completo ou um booleano indicando sucesso ou falha.
    """
    api_token = check_api_token(api_token)

    url = 'https://{company_domain}.pipedrive.com/v1/personFields/{id}?'
    url = url.replace("{company_domain}", company_domain)
    url = url.replace("{id}", str(id))

    url += f'api_token={api_token}'

    response = requests.delete(url)

    if return_type == 'boolean':
        return response.status_code in [200, 201]
    else:
        return response.json()


def personfields_delete_multiple(ids, api_token=None, company_domain='api', return_type='complete'):
    """
    Função para deletar múltiplos campos de pessoa no Pipedrive em massa.

    Parâmetros:
    - ids (str): IDs dos campos, separados por vírgula, a serem deletados.
    - api_token (str): Token da API para autenticação. Necessário.
    - company_domain (str): Domínio da empresa no Pipedrive. Padrão é 'api'.
    - return_type (str): O retorno padrão é um objeto completo ou pode ser definido como booleano ('complete' ou 'boolean').

    Retorna:
    - Dependendo do parâmetro return_type, retorna um objeto JSON completo ou um booleano indicando sucesso ou falha.
    """
    api_token = check_api_token(api_token)

    url = 'https://{company_domain}.pipedrive.com/v1/personFields?'
    url = url.replace("{company_domain}", company_domain)

    bodyList = {
        'ids': ids
    }

    url += f'api_token={api_token}'

    response = requests.delete(url, json=bodyList)

    if return_type == 'boolean':
        return response.status_code in [200, 201]
    else:
        return response.json()

def personfields_get(id, api_token=None, company_domain='api'):
    """
    Função para obter um campo de pessoa no Pipedrive.

    Parâmetros:
    - id (str): ID do campo a ser buscado.
    - api_token (str): Token da API para autenticação. Necessário.
    - company_domain (str): Domínio da empresa no Pipedrive. Padrão é 'api'.

    Retorna:
    - dict: Um dicionário contendo as informações do campo de pessoa.

    Exemplo de uso:
    --------------
    field_id = '1234'  # ID do campo de pessoa a ser buscado
    api_token = 'seu_api_token'  # Substitua pelo seu token da API do Pipedrive
    company_domain = 'sua_empresa'  # Substitua pelo domínio da sua empresa

    # Chama a função para obter os detalhes do campo
    field_details = personfields_get(id=field_id, api_token=api_token, company_domain=company_domain)

    # Exibe os detalhes do campo retornado
    print(field_details)
    """
    api_token = check_api_token(api_token)

    url = 'https://{company_domain}.pipedrive.com/v1/personFields/{id}?'
    url = url.replace("{company_domain}", company_domain)
    url = url.replace("{id}", str(id))

    url += f'api_token={api_token}'

    return get_all_(url)



def personfields_get_all(api_token=None, company_domain='api'):
    """
    Função para obter todos os campos de pessoa no Pipedrive.

    Parâmetros:
    - api_token (str): Token da API para autenticação. Necessário.
    - company_domain (str): Domínio da empresa no Pipedrive. Padrão é 'api'.

    Retorna:
    - dict: Um dicionário contendo todos os campos de pessoa.

    Exemplo de uso:
    --------------
    api_token = 'seu_api_token'  # Substitua pelo seu token da API do Pipedrive
    company_domain = 'sua_empresa'  # Substitua pelo domínio da sua empresa

    # Chama a função para obter todos os campos de pessoa
    person_fields = personfields_get_all(api_token=api_token, company_domain=company_domain)

    # Exibe os campos de pessoa retornados
    print(person_fields)
    """
    api_token = check_api_token(api_token)

    url = 'https://{company_domain}.pipedrive.com/v1/personFields?'
    url = url.replace("{company_domain}", company_domain)

    url += f'api_token={api_token}'

    return get_all_(url)

def personfields_update(id, name, options=None, api_token=None, company_domain='api', return_type='complete'):
    """
    Função para atualizar um campo de pessoa no Pipedrive.

    Parâmetros:
    - id (str): ID do campo a ser atualizado.
    - name (str): Nome do campo.
    - options (str, opcional): Quando field_type for 'set' ou 'enum', as opções devem ser fornecidas como uma string JSON.
      Exemplo: [{"id":123,"label":"Existing Item"},{"label":"New Item"}].
    - api_token (str): Token da API para autenticação. Necessário.
    - company_domain (str): Domínio da empresa no Pipedrive. Padrão é 'api'.
    - return_type (str): O retorno padrão é um objeto completo ou pode ser definido como booleano ('complete' ou 'boolean').

    Retorna:
    - dict: Um dicionário contendo os detalhes da operação, ou um booleano indicando sucesso ou falha, dependendo de return_type.

    Exemplo de uso:
    --------------
    field_id = '1234'  # ID do campo de pessoa a ser atualizado
    api_token = 'seu_api_token'  # Substitua pelo seu token da API do Pipedrive
    company_domain = 'sua_empresa'  # Substitua pelo domínio da sua empresa

    # Chama a função para atualizar o campo
    updated_field = personfields_update(id=field_id, name='Novo Nome', api_token=api_token, company_domain=company_domain)

    # Exibe os detalhes da atualização
    print(updated_field)
    """
    api_token = check_api_token(api_token)

    url = 'https://{company_domain}.pipedrive.com/v1/personFields/{id}?'
    url = url.replace("{company_domain}", company_domain)
    url = url.replace("{id}", str(id))

    bodyList = {
        'name': name,
        'options': options
    }

    bodyList = clear_list(bodyList)

    url += f'api_token={api_token}'

    bodyList.pop('id', None)

    response = requests.put(url, json=bodyList)

    if return_type == 'boolean':
        return response.status_code in [200, 201]
    else:
        return response.json()


def persons_add(name, owner_id=None, org_id=None, email=None, phone=None, visible_to=None, add_time=None, custom_list=None, api_token=None, company_domain='api', return_type='complete'):
    """
    Função para adicionar uma pessoa no Pipedrive.

    Parâmetros:
    - name (str): Nome da pessoa.
    - owner_id (int, opcional): ID do usuário que será marcado como proprietário desta pessoa. Se omitido, o usuário autorizado será usado.
    - org_id (int, opcional): ID da organização à qual esta pessoa pertencerá.
    - email (str, opcional): Endereços de email associados à pessoa.
    - phone (str, opcional): Números de telefone associados à pessoa.
    - visible_to (int, opcional): Visibilidade da pessoa. 1 = Privado (apenas proprietário e seguidores); 3 = Compartilhado (toda a empresa).
    - add_time (str, opcional): Data e hora de criação da pessoa no formato UTC (YYYY-MM-DD HH:MM:SS). Requer token de administrador.
    - custom_list (dict, opcional): Dicionário com campos personalizados. Exemplo: {'custom_field': 'valor'}.
    - api_token (str): Token da API para autenticação. Necessário.
    - company_domain (str): Domínio da empresa no Pipedrive. Padrão é 'api'.
    - return_type (str): O retorno padrão é um objeto completo ou pode ser definido como booleano ('complete' ou 'boolean').

    Retorna:
    - dict: Um dicionário contendo os detalhes da pessoa adicionada ou um booleano indicando sucesso ou falha, dependendo do return_type.

    Exemplo de uso:
    --------------
    api_token = 'seu_api_token'  # Substitua pelo seu token da API do Pipedrive
    company_domain = 'sua_empresa'  # Substitua pelo domínio da sua empresa

    # Chama a função para adicionar uma nova pessoa
    new_person = persons_add(name='Nome da Pessoa', api_token=api_token, company_domain=company_domain)

    # Exibe os detalhes da pessoa adicionada
    print(new_person)
    """
    api_token = check_api_token(api_token)

    url = 'https://{company_domain}.pipedrive.com/v1/persons?'
    url = url.replace("{company_domain}", company_domain)

    bodyList = {
        'name': name,
        'owner_id': owner_id,
        'org_id': org_id,
        'email': email,
        'phone': phone,
        'visible_to': visible_to,
        'add_time': add_time
    }

    if isinstance(custom_list, dict):
        bodyList.update(custom_list)

    bodyList = clear_list(bodyList)

    url += f'api_token={api_token}'

    response = requests.post(url, json=bodyList)

    if return_type == 'boolean':
        return response.status_code in [200, 201]
    else:
        return response.json()

def persons_add_follower(id, user_id, api_token=None, company_domain='api', return_type='complete'):
    """
    Função para adicionar um seguidor a uma pessoa no Pipedrive.

    Parâmetros:
    - id (str): ID da pessoa.
    - user_id (str): ID do usuário que será adicionado como seguidor.
    - api_token (str): Token da API para autenticação. Necessário.
    - company_domain (str): Domínio da empresa no Pipedrive. Padrão é 'api'.
    - return_type (str): O retorno padrão é um objeto completo ou pode ser definido como booleano ('complete' ou 'boolean').

    Retorna:
    - dict: Um dicionário contendo os detalhes da operação ou um booleano indicando sucesso ou falha, dependendo do return_type.

    Exemplo de uso:
    --------------
    api_token = 'seu_api_token'  # Substitua pelo seu token da API do Pipedrive
    company_domain = 'sua_empresa'  # Substitua pelo domínio da sua empresa
    person_id = '1234'  # ID da pessoa
    user_id = '5678'  # ID do usuário que será adicionado como seguidor

    # Chama a função para adicionar um seguidor
    response = persons_add_follower(id=person_id, user_id=user_id, api_token=api_token, company_domain=company_domain)

    # Exibe o resultado da operação
    print(response)
    """
    api_token = check_api_token(api_token)


    url = 'https://{company_domain}.pipedrive.com/v1/persons/{id}/followers?'
    url = url.replace("{company_domain}", company_domain)
    url = url.replace("{id}", str(id))

    
    bodyList = {
        'user_id': user_id
    }

    
    bodyList = clear_list(bodyList)

    
    url += f'api_token={api_token}'

    
    response = requests.post(url, json=bodyList)

    
    if return_type == 'boolean':
        return response.status_code in [200, 201]
    else:
        return response.json()


def persons_add_picture(id, file, crop_x=None, crop_y=None, crop_width=None, crop_height=None, api_token=None, company_domain='api', return_type='complete'):
    """
    Função para adicionar uma imagem a uma pessoa no Pipedrive.

    Parâmetros:
    - id (str): ID da pessoa.
    - file (str): Caminho para a imagem a ser enviada no formato multipart/form-data.
    - crop_x (int, opcional): Coordenada X de onde começar o corte (em pixels).
    - crop_y (int, opcional): Coordenada Y de onde começar o corte (em pixels).
    - crop_width (int, opcional): Largura da área de corte (em pixels).
    - crop_height (int, opcional): Altura da área de corte (em pixels).
    - api_token (str): Token da API para autenticação. Necessário.
    - company_domain (str): Domínio da empresa no Pipedrive. Padrão é 'api'.
    - return_type (str): O retorno padrão é um objeto completo ou pode ser definido como booleano ('complete' ou 'boolean').

    Retorna:
    - dict: Um dicionário contendo os detalhes do processo ou um booleano indicando sucesso ou falha, dependendo do return_type.

    Exemplo de uso:
    --------------
    api_token = 'seu_api_token'  # Substitua pelo seu token da API do Pipedrive
    company_domain = 'sua_empresa'  # Substitua pelo domínio da sua empresa
    person_id = '1234'  # ID da pessoa
    file_path = 'caminho/para/imagem.jpg'  # Caminho para a imagem

    # Chama a função para adicionar a imagem
    response = persons_add_picture(id=person_id, file=file_path, api_token=api_token, company_domain=company_domain)

    # Exibe o resultado da operação
    print(response)
    """
    api_token = check_api_token(api_token)


    url = 'https://{company_domain}.pipedrive.com/v1/persons/{id}/picture?'
    url = url.replace("{company_domain}", company_domain)
    url = url.replace("{id}", str(id))

    
    bodyList = {
        'crop_x': crop_x,
        'crop_y': crop_y,
        'crop_width': crop_width,
        'crop_height': crop_height
    }

    
    bodyList = clear_list(bodyList)

    
    files = {
        'file': open(file, 'rb')
    }

    
    url += f'api_token={api_token}'

     
    response = requests.post(url, data=bodyList, files=files)

    
    if return_type == 'boolean':
        return response.status_code in [200, 201]
    else:
        return response.json()


def persons_delete(id, api_token=None, company_domain='api', return_type='complete'):
    """
    Função para deletar uma pessoa no Pipedrive.

    Parâmetros:
    - id (str): ID da pessoa a ser deletada.
    - api_token (str): Token da API para autenticação. Necessário.
    - company_domain (str): Domínio da empresa no Pipedrive. Padrão é 'api'.
    - return_type (str): O retorno padrão é um objeto completo ou pode ser definido como booleano ('complete' ou 'boolean').

    Retorna:
    - dict: Um dicionário contendo os detalhes do processo de exclusão ou um booleano indicando sucesso ou falha, dependendo do return_type.

    Exemplo de uso:
    --------------
    api_token = 'seu_api_token'  # Substitua pelo seu token da API do Pipedrive
    company_domain = 'sua_empresa'  # Substitua pelo domínio da sua empresa
    person_id = '1234'  # ID da pessoa

    # Chama a função para deletar uma pessoa
    response = persons_delete(id=person_id, api_token=api_token, company_domain=company_domain)

    # Exibe o resultado da operação
    print(response)
    """
    api_token = check_api_token(api_token)


    url = 'https://{company_domain}.pipedrive.com/v1/persons/{id}?'
    url = url.replace("{company_domain}", company_domain)
    url = url.replace("{id}", str(id))

    
    url += f'api_token={api_token}'

    
    response = requests.delete(url)

    
    if return_type == 'boolean':
        return response.status_code in [200, 201]
    else:
        return response.json()


def persons_delete_followers(id, follower_id, api_token=None, company_domain='api', return_type='complete'):
    """
    Função para deletar um seguidor de uma pessoa no Pipedrive.

    Parâmetros:
    - id (str): ID da pessoa.
    - follower_id (str): ID do seguidor a ser deletado.
    - api_token (str): Token da API para autenticação. Necessário.
    - company_domain (str): Domínio da empresa no Pipedrive. Padrão é 'api'.
    - return_type (str): O retorno padrão é um objeto completo ou pode ser definido como booleano ('complete' ou 'boolean').

    Retorna:
    - dict: Um dicionário contendo os detalhes do processo de exclusão ou um booleano indicando sucesso ou falha, dependendo do return_type.

    Exemplo de uso:
    --------------
    api_token = 'seu_api_token'  # Substitua pelo seu token da API do Pipedrive
    company_domain = 'sua_empresa'  # Substitua pelo domínio da sua empresa
    person_id = '1234'  # ID da pessoa
    follower_id = '5678'  # ID do seguidor a ser deletado

    # Chama a função para deletar o seguidor
    response = persons_delete_follower(id=person_id, follower_id=follower_id, api_token=api_token, company_domain=company_domain)

    # Exibe o resultado da operação
    print(response)
    """
    api_token = check_api_token(api_token)


    url = 'https://{company_domain}.pipedrive.com/v1/persons/{id}/followers/{follower_id}?'
    url = url.replace("{company_domain}", company_domain)
    url = url.replace("{id}", str(id))
    url = url.replace("{follower_id}", str(follower_id))

    
    url += f'api_token={api_token}'

    
    response = requests.delete(url)

    
    if return_type == 'boolean':
        return response.status_code in [200, 201]
    else:
        return response.json()

def persons_delete_picture(id, api_token=None, company_domain='api', return_type='complete'):
    """
    Função para deletar a imagem de uma pessoa no Pipedrive.

    Parâmetros:
    - id (str): ID da pessoa cuja imagem será deletada.
    - api_token (str): Token da API para autenticação. Necessário.
    - company_domain (str): Domínio da empresa no Pipedrive. Padrão é 'api'.
    - return_type (str): O retorno padrão é um objeto completo ou pode ser definido como booleano ('complete' ou 'boolean').

    Retorna:
    - dict: Um dicionário contendo os detalhes do processo de exclusão ou um booleano indicando sucesso ou falha, dependendo do return_type.

    Exemplo de uso:
    --------------
    api_token = 'seu_api_token'  # Substitua pelo seu token da API do Pipedrive
    company_domain = 'sua_empresa'  # Substitua pelo domínio da sua empresa
    person_id = '1234'  # ID da pessoa

    # Chama a função para deletar a imagem da pessoa
    response = persons_delete_picture(id=person_id, api_token=api_token, company_domain=company_domain)

    # Exibe o resultado da operação
    print(response)
    """
    api_token = check_api_token(api_token)


    url = 'https://{company_domain}.pipedrive.com/v1/persons/{id}/picture?'
    url = url.replace("{company_domain}", company_domain)
    url = url.replace("{id}", str(id))

    
    url += f'api_token={api_token}'

    
    response = requests.delete(url)

    
    if return_type == 'boolean':
        return response.status_code in [200, 201]
    else:
        return response.json()


def persons_delete_multiple(ids, api_token=None, company_domain='api', return_type='complete'):
    """
    Função para deletar várias pessoas em massa no Pipedrive.

    Parâmetros:
    - ids (str): IDs das pessoas, separados por vírgula, que serão deletados.
    - api_token (str): Token da API para autenticação. Necessário.
    - company_domain (str): Domínio da empresa no Pipedrive. Padrão é 'api'.
    - return_type (str): O retorno padrão é um objeto completo ou pode ser definido como booleano ('complete' ou 'boolean').

    Retorna:
    - dict: Um dicionário contendo os detalhes do processo de exclusão ou um booleano indicando sucesso ou falha, dependendo do return_type.

    Exemplo de uso:
    --------------
    api_token = 'seu_api_token'  # Substitua pelo seu token da API do Pipedrive
    company_domain = 'sua_empresa'  # Substitua pelo domínio da sua empresa
    ids = '1234,5678'  # IDs das pessoas a serem deletadas, separados por vírgula

    # Chama a função para deletar múltiplas pessoas
    response = persons_delete_multiple(ids=ids, api_token=api_token, company_domain=company_domain)

    # Exibe o resultado da operação
    print(response)
    """
    api_token = check_api_token(api_token)


    url = 'https://{company_domain}.pipedrive.com/v1/persons?'
    url = url.replace("{company_domain}", company_domain)

    
    bodyList = {
        'ids': ids
    }

    
    url += f'api_token={api_token}'

    response = requests.delete(url, json=bodyList)

    
    if return_type == 'boolean':
        return response.status_code in [200, 201]
    else:
        return response.json()

def persons_find(term, org_id=None, start=None, limit=None, search_by_email=None, api_token=None, company_domain='api'):
    """
    Função para buscar pessoas por nome no Pipedrive.

    Parâmetros:
    - term (str): Termo de busca para encontrar a pessoa.
    - org_id (int, opcional): ID da organização associada à pessoa.
    - start (int, opcional): Início da paginação.
    - limit (int, opcional): Número de itens mostrados por página.
    - search_by_email (int, opcional): Quando habilitado, o termo será comparado apenas aos endereços de e-mail das pessoas. Padrão: 0 (desabilitado).
    - api_token (str): Token da API para autenticação. Necessário.
    - company_domain (str): Domínio da empresa no Pipedrive. Padrão é 'api'.

    Retorna:
    - dict: Um dicionário contendo os resultados da busca de pessoas.

    Exemplo de uso:
    --------------
    api_token = 'seu_api_token'  # Substitua pelo seu token da API do Pipedrive
    company_domain = 'sua_empresa'  # Substitua pelo domínio da sua empresa
    term = 'Nome da Pessoa'

    # Chama a função para buscar uma pessoa pelo nome
    response = persons_find(term=term, api_token=api_token, company_domain=company_domain)

    # Exibe o resultado da busca
    print(response)
    """
    api_token = check_api_token(api_token)

    url = 'https://{company_domain}.pipedrive.com/v1/persons/find?'
    url = url.replace("{company_domain}", company_domain)

    bodyList = {
        'term': term,
        'org_id': org_id,
        'start': 0 if start is None else start,
        'limit': 500 if limit is None else limit,
        'search_by_email': search_by_email
    }

    bodyList = clear_list(bodyList)

    url += prepare_url_parameters_(bodyList)

    url += f'&api_token={api_token}'

    return get_all_(url)


def persons_get(id, api_token=None, company_domain='api'):
    """
    Função para obter detalhes de uma pessoa no Pipedrive.

    Parâmetros:
    - id (str): ID da pessoa cujos detalhes serão obtidos.
    - api_token (str): Token da API para autenticação. Necessário.
    - company_domain (str): Domínio da empresa no Pipedrive. Padrão é 'api'.

    Retorna:
    - dict: Um dicionário contendo os detalhes da pessoa.

    Exemplo de uso:
    --------------
    api_token = 'seu_api_token'  # Substitua pelo seu token da API do Pipedrive
    company_domain = 'sua_empresa'  # Substitua pelo domínio da sua empresa
    person_id = '1234'  # ID da pessoa

    # Chama a função para obter os detalhes da pessoa
    response = persons_get(id=person_id, api_token=api_token, company_domain=company_domain)

    # Exibe os detalhes da pessoa
    print(response)
    """
    api_token = check_api_token(api_token)

    url = 'https://{company_domain}.pipedrive.com/v1/persons/{id}?'
    url = url.replace("{company_domain}", company_domain)
    url = url.replace("{id}", str(id))

    url += f'api_token={api_token}'

    return get_all_(url)


def persons_get_activities(id, start=None, limit=None, done=None, exclude=None, api_token=None, company_domain='api'):
    """
    Função para listar as atividades associadas a uma pessoa no Pipedrive.

    Parâmetros:
    - id (str): ID da pessoa.
    - start (int, opcional): Início da paginação.
    - limit (int, opcional): Número de itens mostrados por página.
    - done (int, opcional): Filtrar atividades concluídas (1) ou não concluídas (0). Se omitido, ambas são buscadas.
    - exclude (str, opcional): String com IDs de atividades a serem excluídas do resultado, separadas por vírgula.
    - api_token (str): Token da API para autenticação. Necessário.
    - company_domain (str): Domínio da empresa no Pipedrive. Padrão é 'api'.

    Retorna:
    - dict: Um dicionário contendo as atividades associadas à pessoa.

    Exemplo de uso:
    --------------
    api_token = 'seu_api_token'  # Substitua pelo seu token da API do Pipedrive
    company_domain = 'sua_empresa'  # Substitua pelo domínio da sua empresa
    person_id = '1234'  # ID da pessoa

    # Chama a função para listar as atividades associadas à pessoa
    response = persons_get_activities(id=person_id, api_token=api_token, company_domain=company_domain)

    # Exibe as atividades da pessoa
    print(response)
    """
    api_token = check_api_token(api_token)

    url = 'https://{company_domain}.pipedrive.com/v1/persons/{id}/activities?'
    url = url.replace("{company_domain}", company_domain)
    url = url.replace("{id}", str(id))

    bodyList = {
        'start': 0 if start is None else start,
        'limit': 500 if limit is None else limit,
        'done': done,
        'exclude': exclude
    }

    bodyList = clear_list(bodyList)

    url += prepare_url_parameters_(bodyList)

    url += f'&api_token={api_token}'

    return get_all_(url)

def persons_get_deals(id, start=None, limit=None, status=None, sort=None, api_token=None, company_domain='api'):
    """
    Função para listar os negócios associados a uma pessoa no Pipedrive.

    Parâmetros:
    - id (str): ID da pessoa.
    - start (int, opcional): Início da paginação.
    - limit (int, opcional): Número de itens mostrados por página.
    - status (str, opcional): Filtro para buscar negócios com status específico. Domínios possíveis: ('open', 'won', 'lost', 'deleted', 'all_not_deleted').
    - sort (str, opcional): Nomes dos campos e modo de classificação separados por vírgula (campo_1 ASC, campo_2 DESC).
    - api_token (str): Token da API para autenticação. Necessário.
    - company_domain (str): Domínio da empresa no Pipedrive. Padrão é 'api'.

    Retorna:
    - dict: Um dicionário contendo os negócios associados à pessoa.

    Exemplo de uso:
    --------------
    api_token = 'seu_api_token'  # Substitua pelo seu token da API do Pipedrive
    company_domain = 'sua_empresa'  # Substitua pelo domínio da sua empresa
    person_id = '1234'  # ID da pessoa

    # Chama a função para listar os negócios associados à pessoa
    response = persons_get_deals(id=person_id, api_token=api_token, company_domain=company_domain)

    # Exibe os negócios da pessoa
    print(response)
    """
    api_token = check_api_token(api_token)

    url = 'https://{company_domain}.pipedrive.com/v1/persons/{id}/deals?'
    url = url.replace("{company_domain}", company_domain)
    url = url.replace("{id}", str(id))

    bodyList = {
        'start': 0 if start is None else start,
        'limit': 500 if limit is None else limit,
        'status': status,
        'sort': sort
    }

    bodyList = clear_list(bodyList)

    url += prepare_url_parameters_(bodyList)

    url += f'&api_token={api_token}'

    return get_all_(url)

def persons_get_files(id, start=None, limit=None, include_deleted_files=None, sort=None, api_token=None, company_domain='api'):
    """
    Função para listar os arquivos anexados a uma pessoa no Pipedrive.

    Parâmetros:
    - id (str): ID da pessoa.
    - start (int, opcional): Início da paginação.
    - limit (int, opcional): Número de itens mostrados por página.
    - include_deleted_files (int, opcional): Incluir arquivos excluídos. 0 = não, 1 = sim.
    - sort (str, opcional): Nomes dos campos e modo de classificação separados por vírgula (campo_1 ASC, campo_2 DESC). 
      Campos suportados: id, user_id, deal_id, person_id, org_id, product_id, add_time, update_time, file_name, file_type, file_size, comment.
    - api_token (str): Token da API para autenticação. Necessário.
    - company_domain (str): Domínio da empresa no Pipedrive. Padrão é 'api'.

    Retorna:
    - dict: Um dicionário contendo os arquivos anexados à pessoa.

    Exemplo de uso:
    --------------
    api_token = 'seu_api_token'  # Substitua pelo seu token da API do Pipedrive
    company_domain = 'sua_empresa'  # Substitua pelo domínio da sua empresa
    person_id = '1234'  # ID da pessoa

    # Chama a função para listar os arquivos anexados à pessoa
    response = persons_get_files(id=person_id, api_token=api_token, company_domain=company_domain)

    # Exibe os arquivos anexados
    print(response)
    """
    api_token = check_api_token(api_token)


    url = 'https://{company_domain}.pipedrive.com/v1/persons/{id}/files?'
    url = url.replace("{company_domain}", company_domain)
    url = url.replace("{id}", str(id))

    
    bodyList = {
        'start': 0 if start is None else start,
        'limit': 500 if limit is None else limit,
        'include_deleted_files': include_deleted_files,
        'sort': sort
    }

    
    bodyList = clear_list(bodyList)

    
    url += prepare_url_parameters_(bodyList)

    
    url += f'&api_token={api_token}'

    
    return get_all_(url)


def persons_get_flow(id, start=None, limit=None, api_token=None, company_domain='api'):
    """
    Função para listar atualizações sobre uma pessoa no Pipedrive.

    Parâmetros:
    - id (str): ID da pessoa.
    - start (int, opcional): Início da paginação.
    - limit (int, opcional): Número de itens mostrados por página.
    - api_token (str): Token da API para autenticação. Necessário.
    - company_domain (str): Domínio da empresa no Pipedrive. Padrão é 'api'.

    Retorna:
    - dict: Um dicionário contendo as atualizações sobre a pessoa.

    Exemplo de uso:
    --------------
    api_token = 'seu_api_token'  # Substitua pelo seu token da API do Pipedrive
    company_domain = 'sua_empresa'  # Substitua pelo domínio da sua empresa
    person_id = '1234'  # ID da pessoa

    # Chama a função para listar as atualizações sobre a pessoa
    response = persons_get_flow(id=person_id, api_token=api_token, company_domain=company_domain)

    # Exibe as atualizações sobre a pessoa
    print(response)
    """
    api_token = check_api_token(api_token)


    url = 'https://{company_domain}.pipedrive.com/v1/persons/{id}/flow?'
    url = url.replace("{company_domain}", company_domain)
    url = url.replace("{id}", str(id))

    
    bodyList = {
        'start': 0 if start is None else start,
        'limit': 500 if limit is None else limit
    }

    
    bodyList = clear_list(bodyList)

    
    url += prepare_url_parameters_(bodyList)

    
    url += f'&api_token={api_token}'

    
    return get_all_(url)

def persons_get_followers(id, api_token=None, company_domain='api'):
    """
    Função para listar os seguidores de uma pessoa no Pipedrive.

    Parâmetros:
    - id (str): ID da pessoa.
    - api_token (str): Token da API para autenticação. Necessário.
    - company_domain (str): Domínio da empresa no Pipedrive. Padrão é 'api'.

    Retorna:
    - dict: Um dicionário contendo a lista de seguidores da pessoa.

    Exemplo de uso:
    --------------
    api_token = 'seu_api_token'  # Substitua pelo seu token da API do Pipedrive
    company_domain = 'sua_empresa'  # Substitua pelo domínio da sua empresa
    person_id = '1234'  # ID da pessoa

    # Chama a função para listar os seguidores da pessoa
    response = persons_get_followers(id=person_id, api_token=api_token, company_domain=company_domain)

    # Exibe os seguidores da pessoa
    print(response)
    """

    api_token = check_api_token(api_token)


    url = 'https://{company_domain}.pipedrive.com/v1/persons/{id}/followers?'
    url = url.replace("{company_domain}", company_domain)
    url = url.replace("{id}", str(id))


    url += f'api_token={api_token}'


    return get_all_(url)



def persons_get_mailmessages(id, start=None, limit=None, api_token=None, company_domain='api'):
    """
    Função para listar as mensagens de e-mail associadas a uma pessoa no Pipedrive.

    Parâmetros:
    - id (str): ID da pessoa.
    - start (int, opcional): Início da paginação.
    - limit (int, opcional): Número de itens mostrados por página.
    - api_token (str): Token da API para autenticação. Necessário.
    - company_domain (str): Domínio da empresa no Pipedrive. Padrão é 'api'.

    Retorna:
    - dict: Um dicionário contendo as mensagens de e-mail associadas à pessoa.

    Exemplo de uso:
    --------------
    api_token = 'seu_api_token'  # Substitua pelo seu token da API do Pipedrive
    company_domain = 'sua_empresa'  # Substitua pelo domínio da sua empresa
    person_id = '1234'  # ID da pessoa

    # Chama a função para listar as mensagens de e-mail associadas à pessoa
    response = persons_get_mailmessages(id=person_id, api_token=api_token, company_domain=company_domain)

    # Exibe as mensagens de e-mail associadas
    print(response)
    """
    api_token = check_api_token(api_token)

    url = 'https://{company_domain}.pipedrive.com/v1/persons/{id}/mailMessages?'
    url = url.replace("{company_domain}", company_domain)
    url = url.replace("{id}", str(id))

    bodyList = {
        'start': 0 if start is None else start,
        'limit': 500 if limit is None else limit
    }

    bodyList = clear_list(bodyList)

    url += prepare_url_parameters_(bodyList)

    url += f'&api_token={api_token}'

    return get_all_(url)


def persons_get_permittedusers(id, access_level=None, api_token=None, company_domain='api'):
    """
    Função para listar os usuários permitidos de uma pessoa no Pipedrive.

    Parâmetros:
    - id (str): ID da pessoa.
    - access_level (int, opcional): Filtrar os resultados pelo nível de acesso permitido. Domínios: 1 = Leitura, 2 = Escrita, 3 = Leitura + Escrita.
    - api_token (str): Token da API para autenticação. Necessário.
    - company_domain (str): Domínio da empresa no Pipedrive. Padrão é 'api'.

    Retorna:
    - dict: Um dicionário contendo a lista de usuários permitidos.

    Exemplo de uso:
    --------------
    api_token = 'seu_api_token'  # Substitua pelo seu token da API do Pipedrive
    company_domain = 'sua_empresa'  # Substitua pelo domínio da sua empresa
    person_id = '1234'  # ID da pessoa

    # Chama a função para listar os usuários permitidos de uma pessoa
    response = persons_get_permittedusers(id=person_id, access_level=1, api_token=api_token, company_domain=company_domain)

    # Exibe os usuários permitidos
    print(response)
    """
    api_token = check_api_token(api_token)

    url = 'https://{company_domain}.pipedrive.com/v1/persons/{id}/permittedUsers?'
    url = url.replace("{company_domain}", company_domain)
    url = url.replace("{id}", str(id))

    bodyList = {
        'access_level': access_level
    }

    bodyList = clear_list(bodyList)

    url += prepare_url_parameters_(bodyList)
    url += f'&api_token={api_token}'

    return get_all_(url)

def persons_get_products(id, start=None, limit=None, api_token=None, company_domain='api'):
    """
    Lista produtos associados a uma pessoa no Pipedrive.

    Parâmetros:
    - id (str): ID da pessoa.
    - start (int, opcional): Paginação inicial.
    - limit (int, opcional): Quantidade de itens exibidos por página.
    - api_token (str): API token para autenticação. Verifique como obtê-lo em: https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference.
    - company_domain (str, opcional): Domínio da empresa. Verifique como obtê-lo em: https://pipedrive.readme.io/docs/how-to-get-the-company-domain.

    Retorna:
    - pd.DataFrame: DataFrame contendo os produtos associados à pessoa.
    """
    api_token = check_api_token(api_token)

    
    url = 'https://{company_domain}.pipedrive.com/v1/persons/{id}/products?'

     
    body_dict = {
        'id': id,
        'start': start if start is not None else 0,
        'limit': limit if limit is not None else 500
    }

    
    body_dict = clear_list(body_dict)

    
    url = f"https://{company_domain}.pipedrive.com/v1/persons/{id}/products?"
    url += prepare_url_parameters_(body_dict)
    url += f"&api_token={api_token}"

    
    return get_all_(url)

def persons_get_all(user_id=None, filter_id=None, first_char=None, start=None, limit=None, sort=None, api_token=None, company_domain='api'):
    """
    Função para obter todas as pessoas do Pipedrive.

    Parâmetros:
    - user_id (int, opcional): Se fornecido, somente as pessoas atribuídas ao usuário dado serão retornadas.
    - filter_id (int, opcional): ID do filtro a ser usado.
    - first_char (str, opcional): Se fornecido, apenas pessoas cujo nome começa com a letra especificada (não diferencia maiúsculas de minúsculas) serão retornadas.
    - start (int, opcional): Início da paginação.
    - limit (int, opcional): Quantidade de itens exibidos por página.
    - sort (str, opcional): Nomes dos campos e modo de ordenação separados por vírgula (ex: "field_name_1 ASC, field_name_2 DESC").
    - api_token (str): Token da API para validação. Consulte: https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference
    - company_domain (str): Domínio da empresa. Consulte: https://pipedrive.readme.io/docs/how-to-get-the-company-domain

    Retorna:
    - pd.DataFrame: DataFrame contendo as informações das pessoas.
    """

    api_token = check_api_token(api_token)

    
    url = 'https://{company_domain}.pipedrive.com/v1/persons?'

     
    body_dict = {
        'user_id': user_id,
        'filter_id': filter_id,
        'first_char': first_char,
        'start': start if start is not None else 0,
        'limit': limit if limit is not None else 500,
        'sort': sort
    }

    
    body_dict = clear_list(body_dict)

    
    url += prepare_url_parameters_(body_dict)
    url = url.replace('{company_domain}', company_domain)
    url += f"&api_token={api_token}"

    
    return get_all_(url)

def persons_update(id, name=None, owner_id=None, org_id=None, email=None, phone=None, visible_to=None, customList=None, api_token=None, company_domain='api', return_type='complete'):
    """
    Função para atualizar uma pessoa no Pipedrive.

    Parâmetros:
    - id (str): ID da pessoa.
    - name (str, opcional): Nome da pessoa.
    - owner_id (int, opcional): ID do usuário que será marcado como proprietário da pessoa.
    - org_id (int, opcional): ID da organização à qual essa pessoa pertence.
    - email (list, opcional): Endereços de email associados à pessoa.
    - phone (list, opcional): Números de telefone associados à pessoa.
    - visible_to (int, opcional): Visibilidade da pessoa (1 = Proprietário e seguidores; 3 = Toda a empresa).
    - customList (dict, opcional): Dicionário com campos personalizados.
    - api_token (str): Token da API para validação. Consulte: https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference.
    - company_domain (str): Domínio da empresa. Consulte: https://pipedrive.readme.io/docs/how-to-get-the-company-domain.
    - return_type (str, opcional): Tipo de retorno (padrão 'complete' ou 'boolean' para apenas verificar sucesso/erro).

    Retorna:
    - Objeto de resposta da requisição ou valor booleano indicando sucesso/erro.
    """

    api_token = check_api_token(api_token)

    
    url = f'https://{company_domain}.pipedrive.com/v1/persons/{id}?'

     
    body_dict = {
        'name': name,
        'owner_id': owner_id,
        'org_id': org_id,
        'email': email,
        'phone': phone,
        'visible_to': visible_to
    }

    
    if isinstance(customList, dict):
        body_dict.update(customList)

    
    body_dict = clear_list(body_dict)

    
    url += f"api_token={api_token}"

    
    if 'id' in body_dict:
        del body_dict['id']

    
    response = requests.put(url, json=body_dict)

    
    if return_type == 'boolean':
        return response.status_code in [200, 201]
    else:
        return response


def persons_update_merge(id, merge_with_id, api_token=None, company_domain='api', return_type='complete'):
    """
    Função para mesclar duas pessoas no Pipedrive.

    Parâmetros:
    - id (str): ID da pessoa que será mesclada.
    - merge_with_id (str): ID da pessoa com a qual a pessoa será mesclada.
    - api_token (str): Token da API para validação. Consulte: https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference.
    - company_domain (str): Domínio da empresa. Consulte: https://pipedrive.readme.io/docs/how-to-get-the-company-domain.
    - return_type (str, opcional): Tipo de retorno ('complete' para retornar toda a resposta, 'boolean' para verificar apenas sucesso/erro).

    Retorna:
    - Objeto de resposta da requisição ou valor booleano indicando sucesso/erro.
    """

    api_token = check_api_token(api_token)

    
    url = f'https://{company_domain}.pipedrive.com/v1/persons/{id}/merge?'

     
    body_dict = {
        'merge_with_id': merge_with_id
    }

    
    body_dict = clear_list(body_dict)

    
    url += f"api_token={api_token}"

    
    if 'id' in body_dict:
        del body_dict['id']

    
    response = requests.put(url, json=body_dict)

    
    if return_type == 'boolean':
        return response.status_code in [200, 201]
    else:
        return response

def pipelines_add(name=None, deal_probability=None, order_nr=None, active=None, api_token=None, company_domain='api', return_type='complete'):
    """
    Função para adicionar um novo pipeline no Pipedrive.

    Parâmetros:
    - name (str, opcional): Nome do pipeline.
    - deal_probability (int, opcional): Se a probabilidade de negócios está desativada ou ativada (0 ou 1).
    - order_nr (int, opcional): Define a ordem dos pipelines. O primeiro pipeline (order_nr=0) é o pipeline padrão.
    - active (int, opcional): Se o pipeline será tornado inativo (0) ou ativo (1).
    - api_token (str): Token da API para validação. Consulte: https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference.
    - company_domain (str): Domínio da empresa. Consulte: https://pipedrive.readme.io/docs/how-to-get-the-company-domain.
    - return_type (str, opcional): Tipo de retorno ('complete' para retornar toda a resposta, 'boolean' para verificar apenas sucesso/erro).

    Retorna:
    - Objeto de resposta da requisição ou valor booleano indicando sucesso/erro.
    """

    api_token = check_api_token(api_token)

    
    url = f'https://{company_domain}.pipedrive.com/v1/pipelines?'

     
    body_dict = {
        'name': name,
        'deal_probability': deal_probability,
        'order_nr': order_nr,
        'active': active
    }

    
    body_dict = clear_list(body_dict)

    
    url += f"api_token={api_token}"

    
    response = requests.post(url, json=body_dict)

    
    if return_type == 'boolean':
        return response.status_code in [200, 201]
    else:
        return response
    
def pipelines_delete(id, api_token=None, company_domain='api', return_type='complete'):
    """
    Função para deletar um pipeline no Pipedrive.

    Parâmetros:
    - id (str): ID do pipeline a ser deletado.
    - api_token (str): Token da API para validação. Consulte: https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference.
    - company_domain (str): Domínio da empresa. Consulte: https://pipedrive.readme.io/docs/how-to-get-the-company-domain.
    - return_type (str, opcional): Tipo de retorno ('complete' para retornar toda a resposta, 'boolean' para verificar apenas sucesso/erro).

    Retorna:
    - Objeto de resposta da requisição ou valor booleano indicando sucesso/erro.
    """

    api_token = check_api_token(api_token)

    
    url = f'https://{company_domain}.pipedrive.com/v1/pipelines/{id}?api_token={api_token}'

    
    response = requests.delete(url)

    
    if return_type == 'boolean':
        return response.status_code in [200, 201]
    else:
        return response

def pipelines_get(id, totals_convert_currency=None, api_token=None, company_domain='api'):
    """
    Função para obter um pipeline do Pipedrive.

    Parâmetros:
    - id (str): ID do pipeline a ser buscado.
    - totals_convert_currency (str, opcional): Código de moeda de 3 letras. Se fornecido, os totais são convertidos para essa moeda. Pode ser 'default_currency' para usar a moeda padrão do usuário.
    - api_token (str): Token da API para validação. Consulte: https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference.
    - company_domain (str): Domínio da empresa. Consulte: https://pipedrive.readme.io/docs/how-to-get-the-company-domain.

    Retorna:
    - pd.DataFrame: DataFrame contendo os dados do pipeline.
    """

    api_token = check_api_token(api_token)

    
    url = f'https://{company_domain}.pipedrive.com/v1/pipelines/{id}?'

     
    body_dict = {
        'totals_convert_currency': totals_convert_currency
    }

    
    body_dict = clear_list(body_dict)

    
    url += prepare_url_parameters_(body_dict)
    url += f"&api_token={api_token}"

    
    return get_all_(url)

def pipelines_get_conversion_statistics(id, start_date, end_date, user_id=None, api_token=None, company_domain='api'):
    """
    Função para obter as taxas de conversão de negócios em um pipeline no Pipedrive.

    Parâmetros:
    - id (str): ID do pipeline.
    - start_date (str): Início do período (formato: YYYY-MM-DD).
    - end_date (str): Fim do período (formato: YYYY-MM-DD).
    - user_id (int, opcional): ID do usuário cujas estatísticas de métricas do pipeline serão buscadas. Se omitido, o usuário autorizado será utilizado.
    - api_token (str): Token da API para validação. Consulte: https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference.
    - company_domain (str): Domínio da empresa. Consulte: https://pipedrive.readme.io/docs/how-to-get-the-company-domain.

    Retorna:
    - pd.DataFrame: DataFrame contendo as taxas de conversão de negócios no pipeline.
    """

    api_token = check_api_token(api_token)

    
    url = f'https://{company_domain}.pipedrive.com/v1/pipelines/{id}/conversion_statistics?'

     
    body_dict = {
        'start_date': start_date,
        'end_date': end_date,
        'user_id': user_id
    }

    
    body_dict = clear_list(body_dict)

    
    url += prepare_url_parameters_(body_dict)
    url += f"&api_token={api_token}"



    return get_all_(url)


def pipelines_get_deals(id, filter_id=None, user_id=None, everyone=None, stage_id=None, start=None, limit=None, get_summary=None, totals_convert_currency=None, api_token=None, company_domain='api'):
    """
    Função para obter negócios em um pipeline no Pipedrive.

    Parâmetros:
    - id (str): ID do pipeline a ser buscado.
    - filter_id (str, opcional): Se fornecido, apenas os negócios correspondentes ao filtro serão retornados.
    - user_id (str, opcional): Se fornecido, apenas os negócios do usuário especificado serão retornados. Se omitido, os negócios do usuário autorizado serão retornados.
    - everyone (int, opcional): Se fornecido, os negócios de todos os usuários serão retornados, ignorando filter_id e user_id (0 ou 1).
    - stage_id (str, opcional): Se fornecido, apenas negócios dentro do estágio especificado serão retornados.
    - start (int, opcional): Início da paginação.
    - limit (int, opcional): Quantidade de itens exibidos por página. O padrão é 500.
    - get_summary (int, opcional): Se fornecido, inclui o resumo do pipeline nos dados adicionais (0 ou 1).
    - totals_convert_currency (str, opcional): Código de moeda de 3 letras. Se fornecido, os totais convertidos são retornados no deals_summary.
    - api_token (str): Token da API para validação. Consulte: https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference.
    - company_domain (str): Domínio da empresa. Consulte: https://pipedrive.readme.io/docs/how-to-get-the-company-domain.

    Retorna:
    - pd.DataFrame: DataFrame contendo os negócios no pipeline.
    """

    api_token = check_api_token(api_token)

    
    url = f'https://{company_domain}.pipedrive.com/v1/pipelines/{id}/deals?'

     
    body_dict = {
        'filter_id': filter_id,
        'user_id': user_id,
        'everyone': everyone,
        'stage_id': stage_id,
        'start': start if start is not None else 0,
        'limit': limit if limit is not None else 500,
        'get_summary': get_summary,
        'totals_convert_currency': totals_convert_currency
    }

    
    body_dict = clear_list(body_dict)

    
    url += prepare_url_parameters_(body_dict)
    url += f"&api_token={api_token}"

    
    return get_all_(url)


def pipelines_get_movement_statistics(id, start_date, end_date, user_id=None, api_token=None, company_domain='api'):
    """
    Função para obter as movimentações de negócios em um pipeline no Pipedrive.

    Parâmetros:
    - id (str): ID do pipeline.
    - start_date (str): Início do período (formato: YYYY-MM-DD).
    - end_date (str): Fim do período (formato: YYYY-MM-DD).
    - user_id (str, opcional): ID do usuário cujas estatísticas de movimentação do pipeline serão buscadas. Se omitido, o usuário autorizado será utilizado.
    - api_token (str): Token da API para validação. Consulte: https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference.
    - company_domain (str): Domínio da empresa. Consulte: https://pipedrive.readme.io/docs/how-to-get-the-company-domain.

    Retorna:
    - pd.DataFrame: DataFrame contendo as estatísticas de movimentação dos negócios no pipeline.
    """

    api_token = check_api_token(api_token)

    
    url = f'https://{company_domain}.pipedrive.com/v1/pipelines/{id}/movement_statistics?'

     
    body_dict = {
        'start_date': start_date,
        'end_date': end_date,
        'user_id': user_id
    }

    
    body_dict = clear_list(body_dict)

    
    url += prepare_url_parameters_(body_dict)
    url += f"&api_token={api_token}"

    
    return get_all_(url)

def pipelines_get_all(api_token=None, company_domain='api'):
    """
    Função para obter todos os pipelines no Pipedrive.

    Parâmetros:
    - api_token (str): Token da API para validação. Consulte: https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference.
    - company_domain (str): Domínio da empresa. Consulte: https://pipedrive.readme.io/docs/how-to-get-the-company-domain.

    Retorna:
    - pd.DataFrame: DataFrame contendo todos os pipelines.
    """

    api_token = check_api_token(api_token)

    
    url = f'https://{company_domain}.pipedrive.com/v1/pipelines?api_token={api_token}'

    
    return get_all_(url)


def pipelines_update(id, name=None, deal_probability=None, order_nr=None, active=None, api_token=None, company_domain='api', return_type='complete'):
    """
    Função para editar um pipeline no Pipedrive.

    Parâmetros:
    - id (str): ID do pipeline a ser editado.
    - name (str, opcional): Nome do pipeline.
    - deal_probability (int, opcional): Se a probabilidade de negócio está ativada ou desativada (0 ou 1).
    - order_nr (int, opcional): Define a ordem dos pipelines. O primeiro pipeline (order_nr=0) é o pipeline padrão.
    - active (int, opcional): Se o pipeline será ativo (1) ou inativo (0).
    - api_token (str): Token da API para validação. Consulte: https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference.
    - company_domain (str): Domínio da empresa. Consulte: https://pipedrive.readme.io/docs/how-to-get-the-company-domain.
    - return_type (str, opcional): Tipo de retorno ('complete' para retornar toda a resposta, 'boolean' para verificar apenas sucesso/erro).

    Retorna:
    - Objeto de resposta da requisição ou valor booleano indicando sucesso/erro.
    """

    api_token = check_api_token(api_token)

    
    url = f'https://{company_domain}.pipedrive.com/v1/pipelines/{id}?api_token={api_token}'

     
    body_dict = {
        'name': name,
        'deal_probability': deal_probability,
        'order_nr': order_nr,
        'active': active
    }

    
    body_dict = clear_list(body_dict)

    
    response = requests.put(url, json=body_dict)

    
    if return_type == 'boolean':
        return response.status_code in [200, 201]
    else:
        return response


def productfields_add(name, field_type, options=None, api_token=None, company_domain='api', return_type='complete'):
    """
    Função para adicionar um novo campo de produto no Pipedrive.

    Parâmetros:
    - name (str): Nome do campo.
    - field_type (str): Tipo do campo. Pode ser um dos seguintes: varchar, varchar_auto, text, double, monetary, date, set, enum, user, org, people, phone, time, timerange, daterange.
    - options (list, opcional): Quando field_type for 'set' ou 'enum', opções possíveis devem ser fornecidas como uma lista (ex: ['red', 'blue', 'lilac']).
    - api_token (str): Token da API para validação. Consulte: https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference.
    - company_domain (str): Domínio da empresa. Consulte: https://pipedrive.readme.io/docs/how-to-get-the-company-domain.
    - return_type (str, opcional): Tipo de retorno ('complete' para retornar toda a resposta, 'boolean' para verificar apenas sucesso/erro).

    Retorna:
    - Objeto de resposta da requisição ou valor booleano indicando sucesso/erro.
    """

    api_token = check_api_token(api_token)

    
    url = f'https://{company_domain}.pipedrive.com/v1/productFields?api_token={api_token}'

     
    body_dict = {
        'name': name,
        'field_type': field_type,
        'options': options
    }

    
    body_dict = clear_list(body_dict)

    
    response = requests.post(url, json=body_dict)

    
    if return_type == 'boolean':
        return response.status_code in [200, 201]
    else:
        return response

def productfields_delete(id, api_token=None, company_domain='api', return_type='complete'):
    """
    Função para deletar um campo de produto no Pipedrive.

    Parâmetros:
    - id (str): ID do campo a ser deletado.
    - api_token (str): Token da API para validação. Consulte: https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference.
    - company_domain (str): Domínio da empresa. Consulte: https://pipedrive.readme.io/docs/how-to-get-the-company-domain.
    - return_type (str, opcional): Tipo de retorno ('complete' para retornar toda a resposta, 'boolean' para verificar apenas sucesso/erro).

    Retorna:
    - Objeto de resposta da requisição ou valor booleano indicando sucesso/erro.
    """

    api_token = check_api_token(api_token)

    
    url = f'https://{company_domain}.pipedrive.com/v1/productFields/{id}?api_token={api_token}'

    
    response = requests.delete(url)

    
    if return_type == 'boolean':
        return response.status_code in [200, 201]
    else:
        return response

def productfields_delete_multiple(ids, api_token=None, company_domain='api', return_type='complete'):
    """
    Função para deletar múltiplos campos de produto no Pipedrive.

    Parâmetros:
    - ids (str): IDs dos campos a serem deletados, separados por vírgula.
    - api_token (str): Token da API para validação. Consulte: https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference.
    - company_domain (str): Domínio da empresa. Consulte: https://pipedrive.readme.io/docs/how-to-get-the-company-domain.
    - return_type (str, opcional): Tipo de retorno ('complete' para retornar toda a resposta, 'boolean' para verificar apenas sucesso/erro).

    Retorna:
    - Objeto de resposta da requisição ou valor booleano indicando sucesso/erro.
    """

    api_token = check_api_token(api_token)

    
    url = f'https://{company_domain}.pipedrive.com/v1/productFields?api_token={api_token}'

    
    body_dict = {
        'ids': ids
    }

    response = requests.delete(url, json=body_dict)

    
    if return_type == 'boolean':
        return response.status_code in [200, 201]
    else:
        return response

def productfields_get(id, api_token=None, company_domain='api'):
    """
    Função para obter um campo de produto no Pipedrive.

    Parâmetros:
    - id (str): ID do campo a ser buscado.
    - api_token (str): Token da API para validação. Consulte: https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference.
    - company_domain (str): Domínio da empresa. Consulte: https://pipedrive.readme.io/docs/how-to-get-the-company-domain.

    Retorna:
    - pd.DataFrame: DataFrame contendo os detalhes do campo de produto.
    """

    api_token = check_api_token(api_token)

    
    url = f'https://{company_domain}.pipedrive.com/v1/productFields/{id}?api_token={api_token}'

    
    return get_all_(url)


def productfields_get_all(api_token=None, company_domain='api'):
    """
    Função para obter todos os campos de produto no Pipedrive.

    Parâmetros:
    - api_token (str): Token da API para validação. Consulte: https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference.
    - company_domain (str): Domínio da empresa. Consulte: https://pipedrive.readme.io/docs/how-to-get-the-company-domain.

    Retorna:
    - pd.DataFrame: DataFrame contendo todos os campos de produto.
    """

    api_token = check_api_token(api_token)

    
    url = f'https://{company_domain}.pipedrive.com/v1/productFields?api_token={api_token}'

    
    return get_all_(url)


def productfields_update(id, name, options=None, api_token=None, company_domain='api', return_type='complete'):
    """
    Função para atualizar um campo de produto no Pipedrive.

    Parâmetros:
    - id (str): ID do campo a ser atualizado.
    - name (str): Nome do campo.
    - options (list, opcional): Quando o field_type for 'set' ou 'enum', as opções possíveis devem ser fornecidas como uma lista de dicionários. Exemplo: [{'id': 123, 'label': 'Item Existente'}, {'label': 'Novo Item'}].
    - api_token (str): Token da API para validação. Consulte: https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference.
    - company_domain (str): Domínio da empresa. Consulte: https://pipedrive.readme.io/docs/how-to-get-the-company-domain.
    - return_type (str, opcional): Tipo de retorno ('complete' para retornar toda a resposta, 'boolean' para verificar apenas sucesso/erro).

    Retorna:
    - Objeto de resposta da requisição ou valor booleano indicando sucesso/erro.
    """

    api_token = check_api_token(api_token)

    
    url = f'https://{company_domain}.pipedrive.com/v1/productFields/{id}?api_token={api_token}'

     
    body_dict = {
        'name': name,
        'options': options
    }

    
    body_dict = clear_list(body_dict)

    
    response = requests.put(url, json=body_dict)

    
    if return_type == 'boolean':
        return response.status_code in [200, 201]
    else:
        return response

def products_add(name, code=None, unit=None, tax=None, active_flag=None, visible_to=None, owner_id=None, prices=None, customList=None, api_token=None, company_domain='api', return_type='complete'):
    """
    Função para adicionar um produto no Pipedrive.

    Parâmetros:
    - name (str): Nome do produto.
    - code (str, opcional): Código do produto.
    - unit (str, opcional): Unidade na qual o produto é vendido.
    - tax (float, opcional): Percentual de imposto.
    - active_flag (int, opcional): Se o produto será ativo (1) ou inativo (0).
    - visible_to (int, opcional): Visibilidade do produto (1 = Proprietário e seguidores; 3 = Toda a empresa).
    - owner_id (int, opcional): ID do usuário que será marcado como proprietário do produto.
    - prices (list, opcional): Lista de objetos contendo informações de preços. Exemplo: [{'currency': 'USD', 'price': 100.0, 'cost': 50.0, 'overhead_cost': 10.0}].
    - customList (dict, opcional): Dicionário contendo campos personalizados.
    - api_token (str): Token da API para validação. Consulte: https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference.
    - company_domain (str): Domínio da empresa. Consulte: https://pipedrive.readme.io/docs/how-to-get-the-company-domain.
    - return_type (str, opcional): Tipo de retorno ('complete' para retornar toda a resposta, 'boolean' para verificar apenas sucesso/erro).

    Retorna:
    - Objeto de resposta da requisição ou valor booleano indicando sucesso/erro.
    """

    api_token = check_api_token(api_token)

    
    url = f'https://{company_domain}.pipedrive.com/v1/products?api_token={api_token}'

     
    body_dict = {
        'name': name,
        'code': code,
        'unit': unit,
        'tax': tax,
        'active_flag': active_flag,
        'visible_to': visible_to,
        'owner_id': owner_id,
        'prices': prices
    }

    if isinstance(customList, dict):
        body_dict.update(customList)

    
    body_dict = clear_list(body_dict)

    
    response = requests.post(url, json=body_dict)

    
    if return_type == 'boolean':
        return response.status_code in [200, 201]
    else:
        return response


def products_add_followers(id, user_id, api_token=None, company_domain='api', return_type='complete'):
    """
    Função para adicionar um seguidor a um produto no Pipedrive.

    Parâmetros:
    - id (str): ID do produto.
    - user_id (str): ID do usuário a ser adicionado como seguidor.
    - api_token (str): Token da API para validação. Consulte: https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference.
    - company_domain (str): Domínio da empresa. Consulte: https://pipedrive.readme.io/docs/how-to-get-the-company-domain.
    - return_type (str, opcional): Tipo de retorno ('complete' para retornar toda a resposta, 'boolean' para verificar apenas sucesso/erro).

    Retorna:
    - Objeto de resposta da requisição ou valor booleano indicando sucesso/erro.
    """

    api_token = check_api_token(api_token)

    
    url = f'https://{company_domain}.pipedrive.com/v1/products/{id}/followers?api_token={api_token}'

     
    body_dict = {
        'user_id': user_id
    }

    
    body_dict = clear_list(body_dict)

    
    response = requests.post(url, json=body_dict)

    
    if return_type == 'boolean':
        return response.status_code in [200, 201]
    else:
        return response

def products_delete(id, api_token=None, company_domain='api', return_type='complete'):
    """
    Função para deletar um produto no Pipedrive.

    Parâmetros:
    - id (str): ID do produto a ser deletado.
    - api_token (str): Token da API para validação. Consulte: https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference.
    - company_domain (str): Domínio da empresa. Consulte: https://pipedrive.readme.io/docs/how-to-get-the-company-domain.
    - return_type (str, opcional): Tipo de retorno ('complete' para retornar toda a resposta, 'boolean' para verificar apenas sucesso/erro).

    Retorna:
    - Objeto de resposta da requisição ou valor booleano indicando sucesso/erro.
    """

    api_token = check_api_token(api_token)

    
    url = f'https://{company_domain}.pipedrive.com/v1/products/{id}?api_token={api_token}'

    
    response = requests.delete(url)

    
    if return_type == 'boolean':
        return response.status_code in [200, 201]
    else:
        return response

def products_delete_followers(id, follower_id, api_token=None, company_domain='api', return_type='complete'):
    """
    Função para remover um seguidor de um produto no Pipedrive.

    Parâmetros:
    - id (str): ID do produto.
    - follower_id (str): ID do seguidor a ser removido.
    - api_token (str): Token da API para validação. Consulte: https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference.
    - company_domain (str): Domínio da empresa. Consulte: https://pipedrive.readme.io/docs/how-to-get-the-company-domain.
    - return_type (str, opcional): Tipo de retorno ('complete' para retornar toda a resposta, 'boolean' para verificar apenas sucesso/erro).

    Retorna:
    - Objeto de resposta da requisição ou valor booleano indicando sucesso/erro.
    """

    api_token = check_api_token(api_token)

    
    url = f'https://{company_domain}.pipedrive.com/v1/products/{id}/followers/{follower_id}?api_token={api_token}'

    
    response = requests.delete(url)

    
    if return_type == 'boolean':
        return response.status_code in [200, 201]
    else:
        return response


def products_find(term, currency=None, start=None, limit=None, api_token=None, company_domain='api'):
    """
    Função para buscar produtos por nome no Pipedrive.

    Parâmetros:
    - term (str): Termo de busca, mínimo de 3 caracteres.
    - currency (str, opcional): Código da moeda em que os preços devem ser retornados. Se omitido, os preços serão retornados na moeda padrão do usuário.
    - start (int, opcional): Início da paginação.
    - limit (int, opcional): Quantidade de itens mostrados por página. O padrão é 500.
    - api_token (str): Token da API para validação. Consulte: https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference.
    - company_domain (str): Domínio da empresa. Consulte: https://pipedrive.readme.io/docs/how-to-get-the-company-domain.

    Retorna:
    - pd.DataFrame: DataFrame contendo os produtos encontrados.
    """

    api_token = check_api_token(api_token)

    
    url = f'https://{company_domain}.pipedrive.com/v1/products/find?api_token={api_token}'

     
    body_dict = {
        'term': term,
        'currency': currency,
        'start': start if start is not None else 0,
        'limit': limit if limit is not None else 500
    }

    
    body_dict = clear_list(body_dict)

    
    url += prepare_url_parameters_(body_dict)

    
    return get_all_(url)

def products_get(id, api_token=None, company_domain='api'):
    """
    Função para obter um produto específico no Pipedrive.

    Parâmetros:
    - id (str): ID do produto.
    - api_token (str): Token da API para validação. Consulte: https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference.
    - company_domain (str): Domínio da empresa. Consulte: https://pipedrive.readme.io/docs/how-to-get-the-company-domain.

    Retorna:
    - pd.DataFrame: DataFrame contendo os detalhes do produto.
    """

    api_token = check_api_token(api_token)

    
    url = f'https://{company_domain}.pipedrive.com/v1/products/{id}?api_token={api_token}'

    
    return get_all_(url)


def products_get_deals(id, start=None, limit=None, status=None, api_token=None, company_domain='api'):
    """
    Função para obter os negócios onde um produto está vinculado no Pipedrive.

    Parâmetros:
    - id (str): ID do produto.
    - start (int, opcional): Início da paginação.
    - limit (int, opcional): Quantidade de itens mostrados por página. O padrão é 500.
    - status (str, opcional): Status específico dos negócios para buscar. Pode ser (open, won, lost, deleted, all_not_deleted).
    - api_token (str): Token da API para validação. Consulte: https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference.
    - company_domain (str): Domínio da empresa. Consulte: https://pipedrive.readme.io/docs/how-to-get-the-company-domain.

    Retorna:
    - pd.DataFrame: DataFrame contendo os negócios associados ao produto.
    """

    api_token = check_api_token(api_token)

    
    url = f'https://{company_domain}.pipedrive.com/v1/products/{id}/deals?api_token={api_token}'

     
    body_dict = {
        'start': start if start is not None else 0,
        'limit': limit if limit is not None else 500,
        'status': status
    }

    
    body_dict = clear_list(body_dict)

    
    url += prepare_url_parameters_(body_dict)

    
    return get_all_(url)

def products_get_files(id, start=None, limit=None, include_deleted_files=None, sort=None, api_token=None, company_domain='api'):
    """
    Função para listar os arquivos anexados a um produto no Pipedrive.

    Parâmetros:
    - id (str): ID do produto.
    - start (int, opcional): Início da paginação.
    - limit (int, opcional): Quantidade de itens mostrados por página. O padrão é 500.
    - include_deleted_files (int, opcional): Se 1, a lista incluirá arquivos deletados, mas não será possível baixá-los.
    - sort (str, opcional): Campos e modo de ordenação separados por vírgula (ex: 'field_name_1 ASC, field_name_2 DESC').
    - api_token (str): Token da API para validação. Consulte: https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference.
    - company_domain (str): Domínio da empresa. Consulte: https://pipedrive.readme.io/docs/how-to-get-the-company-domain.

    Retorna:
    - pd.DataFrame: DataFrame contendo a lista de arquivos anexados ao produto.
    """

    api_token = check_api_token(api_token)

    
    url = f'https://{company_domain}.pipedrive.com/v1/products/{id}/files?api_token={api_token}'

     
    body_dict = {
        'start': start if start is not None else 0,
        'limit': limit if limit is not None else 500,
        'include_deleted_files': include_deleted_files,
        'sort': sort
    }

    
    body_dict = clear_list(body_dict)

    
    url += prepare_url_parameters_(body_dict)

    
    return get_all_(url)

def products_get_followers(id, api_token=None, company_domain='api'):
    """
    Função para listar os seguidores de um produto no Pipedrive.

    Parâmetros:
    - id (str): ID do produto.
    - api_token (str): Token da API para validação. Consulte: https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference.
    - company_domain (str): Domínio da empresa. Consulte: https://pipedrive.readme.io/docs/how-to-get-the-company-domain.

    Retorna:
    - pd.DataFrame: DataFrame contendo a lista de seguidores do produto.
    """

    api_token = check_api_token(api_token)

    
    url = f'https://{company_domain}.pipedrive.com/v1/products/{id}/followers?api_token={api_token}'

    
    return get_all_(url)

def products_get_permittedusers(id, access_level=None, api_token=None, company_domain='api'):
    """
    Função para listar os usuários permitidos de um produto no Pipedrive.

    Parâmetros:
    - id (str): ID do produto.
    - access_level (int, opcional): Nível de acesso permitido. 1 = Leitura, 2 = Escrita, 3 = Leitura + Escrita.
    - api_token (str): Token da API para validação. Consulte: https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference.
    - company_domain (str): Domínio da empresa. Consulte: https://pipedrive.readme.io/docs/how-to-get-the-company-domain.

    Retorna:
    - pd.DataFrame: DataFrame contendo a lista de usuários permitidos do produto.
    """

    api_token = check_api_token(api_token)

    
    url = f'https://{company_domain}.pipedrive.com/v1/products/{id}/permittedUsers?api_token={api_token}'

     
    body_dict = {
        'access_level': access_level
    }

    
    body_dict = clear_list(body_dict)

    
    url += prepare_url_parameters_(body_dict)

    
    return get_all_(url)


def products_get_all(user_id=None, filter_id=None, first_char=None, start=None, limit=None, api_token=None, company_domain='api'):
    """
    Função para obter todos os produtos no Pipedrive.

    Parâmetros:
    - user_id (str, opcional): Se fornecido, somente os produtos do usuário especificado serão retornados.
    - filter_id (str, opcional): ID do filtro a ser usado.
    - first_char (str, opcional): Se fornecido, apenas produtos cujo nome começa com a letra especificada serão retornados (não diferencia maiúsculas de minúsculas).
    - start (int, opcional): Início da paginação.
    - limit (int, opcional): Quantidade de itens mostrados por página. O padrão é 500.
    - api_token (str): Token da API para validação. Consulte: https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference.
    - company_domain (str): Domínio da empresa. Consulte: https://pipedrive.readme.io/docs/how-to-get-the-company-domain.

    Retorna:
    - pd.DataFrame: DataFrame contendo todos os produtos.
    """

    api_token = check_api_token(api_token)

    
    url = f'https://{company_domain}.pipedrive.com/v1/products?api_token={api_token}'

     
    body_dict = {
        'user_id': user_id,
        'filter_id': filter_id,
        'first_char': first_char,
        'start': start if start is not None else 0,
        'limit': limit if limit is not None else 500
    }

    
    body_dict = clear_list(body_dict)

    
    url += prepare_url_parameters_(body_dict)

    
    return get_all_(url)

def products_update(id, name=None, code=None, unit=None, tax=None, active_flag=None, visible_to=None, owner_id=None, prices=None, customList=None, api_token=None, company_domain='api', return_type='complete'):
    """
    Função para atualizar um produto no Pipedrive.

    Parâmetros:
    - id (str): ID do produto a ser atualizado.
    - name (str, opcional): Nome do produto.
    - code (str, opcional): Código do produto.
    - unit (str, opcional): Unidade na qual o produto é vendido.
    - tax (float, opcional): Percentual de imposto.
    - active_flag (int, opcional): Se o produto será ativo (1) ou inativo (0).
    - visible_to (int, opcional): Visibilidade do produto (1 = Proprietário e seguidores; 3 = Toda a empresa).
    - owner_id (int, opcional): ID do usuário que será marcado como proprietário do produto.
    - prices (list, opcional): Lista de objetos contendo informações de preços. Exemplo: [{'currency': 'USD', 'price': 100.0, 'cost': 50.0, 'overhead_cost': 10.0}].
    - customList (dict, opcional): Dicionário contendo campos personalizados.
    - api_token (str): Token da API para validação. Consulte: https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference.
    - company_domain (str): Domínio da empresa. Consulte: https://pipedrive.readme.io/docs/how-to-get-the-company-domain.
    - return_type (str, opcional): Tipo de retorno ('complete' para retornar toda a resposta, 'boolean' para verificar apenas sucesso/erro).

    Retorna:
    - Objeto de resposta da requisição ou valor booleano indicando sucesso/erro.
    """

    api_token = check_api_token(api_token)

    
    url = f'https://{company_domain}.pipedrive.com/v1/products/{id}?api_token={api_token}'

     
    body_dict = {
        'name': name,
        'code': code,
        'unit': unit,
        'tax': tax,
        'active_flag': active_flag,
        'visible_to': visible_to,
        'owner_id': owner_id,
        'prices': prices
    }

    if isinstance(customList, dict):
        body_dict.update(customList)

    
    body_dict = clear_list(body_dict)

    
    response = requests.put(url, json=body_dict)

    
    if return_type == 'boolean':
        return response.status_code in [200, 201]
    else:
        return response


def recents_get(since_timestamp, items=None, start=None, limit=None, api_token=None, company_domain='api'):
    """
    Função para obter registros recentes no Pipedrive.

    Parâmetros:
    - since_timestamp (str): Timestamp em UTC. Formato: YYYY-MM-DD HH:MM:SS.
    - items (list, opcional): Seleção múltipla de tipos de itens a incluir na consulta (ex: ['activity', 'deal', 'person']).
    - start (int, opcional): Início da paginação.
    - limit (int, opcional): Quantidade de itens mostrados por página. O padrão é 500.
    - api_token (str): Token da API para validação. Consulte: https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference.
    - company_domain (str): Domínio da empresa. Consulte: https://pipedrive.readme.io/docs/how-to-get-the-company-domain.

    Retorna:
    - pd.DataFrame: DataFrame contendo os registros recentes.
    """

    api_token = check_api_token(api_token)

    
    url = f'https://{company_domain}.pipedrive.com/v1/recents?api_token={api_token}'

     
    body_dict = {
        'since_timestamp': since_timestamp,
        'items': items,
        'start': start if start is not None else 0,
        'limit': limit if limit is not None else 500
    }

    
    body_dict = clear_list(body_dict)

    
    url += prepare_url_parameters_(body_dict)

    
    return get_all_(url)

def roles_add_assignments(id, user_id, api_token=None, company_domain='api', return_type='complete'):
    """
    Função para adicionar uma atribuição de função no Pipedrive.

    Parâmetros:
    - id (str): ID da função.
    - user_id (str): ID do usuário.
    - api_token (str): Token da API para validação. Consulte: https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference.
    - company_domain (str): Domínio da empresa. Consulte: https://pipedrive.readme.io/docs/how-to-get-the-company-domain.
    - return_type (str, opcional): Tipo de retorno ('complete' para retornar toda a resposta, 'boolean' para verificar apenas sucesso/erro).

    Retorna:
    - Objeto de resposta da requisição ou valor booleano indicando sucesso/erro.
    """

    api_token = check_api_token(api_token)

    
    url = f'https://{company_domain}.pipedrive.com/v1/roles/{id}/assignments?api_token={api_token}'

     
    body_dict = {
        'user_id': user_id
    }

    
    body_dict = clear_list(body_dict)

    
    response = requests.post(url, json=body_dict)

    
    if return_type == 'boolean':
        return response.status_code in [200, 201]
    else:
        return response


def roles_add_settings(id, value, api_token=None, company_domain='api', return_type='complete'):
    """
    Função para adicionar ou atualizar configurações de uma função no Pipedrive.

    Parâmetros:
    - id (str): ID da função. Exemplos: deal_default_visibility, org_default_visibility, person_default_visibility, product_default_visibility, deal_access_level, org_access_level, person_access_level, product_access_level.
    - value (int): Valores possíveis para default_visibility (0...1) e para access_level (1...7).
    - api_token (str): Token da API para validação. Consulte: https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference.
    - company_domain (str): Domínio da empresa. Consulte: https://pipedrive.readme.io/docs/how-to-get-the-company-domain.
    - return_type (str, opcional): Tipo de retorno ('complete' para retornar toda a resposta, 'boolean' para verificar apenas sucesso/erro).

    Retorna:
    - Objeto de resposta da requisição ou valor booleano indicando sucesso/erro.
    """

    api_token = check_api_token(api_token)

    
    url = f'https://{company_domain}.pipedrive.com/v1/roles/{id}/settings?api_token={api_token}'

     
    body_dict = {
        'value': value
    }

    
    body_dict = clear_list(body_dict)

    
    response = requests.post(url, json=body_dict)

    
    if return_type == 'boolean':
        return response.status_code in [200, 201]
    else:
        return response

def roles_delete(id, api_token=None, company_domain='api', return_type='complete'):
    """
    Função para deletar uma função no Pipedrive.

    Parâmetros:
    - id (str): ID da função a ser deletada.
    - api_token (str): Token da API para validação. Consulte: https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference.
    - company_domain (str): Domínio da empresa. Consulte: https://pipedrive.readme.io/docs/how-to-get-the-company-domain.
    - return_type (str, opcional): Tipo de retorno ('complete' para retornar toda a resposta, 'boolean' para verificar apenas sucesso/erro).

    Retorna:
    - Objeto de resposta da requisição ou valor booleano indicando sucesso/erro.
    """

    api_token = check_api_token(api_token)

    
    url = f'https://{company_domain}.pipedrive.com/v1/roles/{id}?api_token={api_token}'

    
    response = requests.delete(url)

    
    if return_type == 'boolean':
        return response.status_code in [200, 201]
    else:
        return response

def roles_delete_assignments(id, user_id, api_token=None, company_domain='api', return_type='complete'):
    """
    Função para deletar uma atribuição de função no Pipedrive.

    Parâmetros:
    - id (str): ID da função.
    - user_id (str): ID do usuário.
    - api_token (str): Token da API para validação. Consulte: https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference.
    - company_domain (str): Domínio da empresa. Consulte: https://pipedrive.readme.io/docs/how-to-get-the-company-domain.
    - return_type (str, opcional): Tipo de retorno ('complete' para retornar toda a resposta, 'boolean' para verificar apenas sucesso/erro).

    Retorna:
    - Objeto de resposta da requisição ou valor booleano indicando sucesso/erro.
    """

    api_token = check_api_token(api_token)

    
    url = f'https://{company_domain}.pipedrive.com/v1/roles/{id}/assignments?api_token={api_token}&user_id={user_id}'

    
    response = requests.delete(url)

    
    if return_type == 'boolean':
        return response.status_code in [200, 201]
    else:
        return response


def roles_get(id, api_token=None, company_domain='api'):
    """
    Função para obter uma função específica no Pipedrive.

    Parâmetros:
    - id (str): ID da função.
    - api_token (str): Token da API para validação. Consulte: https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference.
    - company_domain (str): Domínio da empresa. Consulte: https://pipedrive.readme.io/docs/how-to-get-the-company-domain.

    Retorna:
    - pd.DataFrame: DataFrame contendo os detalhes da função.
    """

    api_token = check_api_token(api_token)

    
    url = f'https://{company_domain}.pipedrive.com/v1/roles/{id}?api_token={api_token}'

    
    return get_all_(url)

def roles_get_assignments(id, start=None, limit=None, api_token=None, company_domain='api'):
    """
    Função para listar as atribuições de função no Pipedrive.

    Parâmetros:
    - id (str): ID da função.
    - start (int, opcional): Início da paginação.
    - limit (int, opcional): Quantidade de itens mostrados por página. O padrão é 500.
    - api_token (str): Token da API para validação. Consulte: https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference.
    - company_domain (str): Domínio da empresa. Consulte: https://pipedrive.readme.io/docs/how-to-get-the-company-domain.

    Retorna:
    - pd.DataFrame: DataFrame contendo a lista de atribuições de função.
    """

    api_token = check_api_token(api_token)

    
    url = f'https://{company_domain}.pipedrive.com/v1/roles/{id}/assignments?api_token={api_token}'

     
    body_dict = {
        'start': start if start is not None else 0,
        'limit': limit if limit is not None else 500
    }

    
    body_dict = clear_list(body_dict)

    
    url += prepare_url_parameters_(body_dict)

    
    return get_all_(url)

def roles_get_roles(id, start=None, limit=None, api_token=None, company_domain='api'):
    """
    Função para listar as sub-funções de uma função no Pipedrive.

    Parâmetros:
    - id (str): ID da função.
    - start (int, opcional): Início da paginação.
    - limit (int, opcional): Quantidade de itens mostrados por página. O padrão é 500.
    - api_token (str): Token da API para validação. Consulte: https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference.
    - company_domain (str): Domínio da empresa. Consulte: https://pipedrive.readme.io/docs/how-to-get-the-company-domain.

    Retorna:
    - pd.DataFrame: DataFrame contendo a lista de sub-funções.
    """

    api_token = check_api_token(api_token)

    
    url = f'https://{company_domain}.pipedrive.com/v1/roles/{id}/roles?api_token={api_token}'

     
    body_dict = {
        'start': start if start is not None else 0,
        'limit': limit if limit is not None else 500
    }

    
    body_dict = clear_list(body_dict)

    
    url += prepare_url_parameters_(body_dict)

    
    return get_all_(url)

def roles_get_settings(id, api_token=None, company_domain='api'):
    """
    Função para listar as configurações de uma função no Pipedrive.

    Parâmetros:
    - id (str): ID da função.
    - api_token (str): Token da API para validação. Consulte: https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference.
    - company_domain (str): Domínio da empresa. Consulte: https://pipedrive.readme.io/docs/how-to-get-the-company-domain.

    Retorna:
    - pd.DataFrame: DataFrame contendo as configurações da função.
    """

    api_token = check_api_token(api_token)

    
    url = f'https://{company_domain}.pipedrive.com/v1/roles/{id}/settings?api_token={api_token}'

    
    return get_all_(url)

def roles_get_all(start=None, limit=None, api_token=None, company_domain='api'):
    """
    Função para obter todas as funções no Pipedrive.

    Parâmetros:
    - start (int, opcional): Início da paginação.
    - limit (int, opcional): Quantidade de itens mostrados por página. O padrão é 500.
    - api_token (str): Token da API para validação. Consulte: https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference.
    - company_domain (str): Domínio da empresa. Consulte: https://pipedrive.readme.io/docs/how-to-get-the-company-domain.

    Retorna:
    - pd.DataFrame: DataFrame contendo todas as funções.
    """

    api_token = check_api_token(api_token)

    
    url = f'https://{company_domain}.pipedrive.com/v1/roles?api_token={api_token}'

     
    body_dict = {
        'start': start if start is not None else 0,
        'limit': limit if limit is not None else 500
    }

    
    body_dict = clear_list(body_dict)

    
    url += prepare_url_parameters_(body_dict)

    
    return get_all_(url)

def roles_update(id, api_token=None, company_domain='api', return_type='complete'):
    """
    Função para atualizar os detalhes de uma função no Pipedrive.

    Parâmetros:
    - id (str): ID da função.
    - api_token (str): Token da API para validação. Consulte: https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference.
    - company_domain (str): Domínio da empresa. Consulte: https://pipedrive.readme.io/docs/how-to-get-the-company-domain.
    - return_type (str, opcional): Tipo de retorno ('complete' para retornar toda a resposta, 'boolean' para verificar apenas sucesso/erro).

    Retorna:
    - Objeto de resposta da requisição ou valor booleano indicando sucesso/erro.
    """

    api_token = check_api_token(api_token)

    
    url = f'https://{company_domain}.pipedrive.com/v1/roles/{id}?api_token={api_token}'

     
    body_dict = {
        # Adicione os parâmetros que você deseja atualizar
    }

    
    response = requests.put(url, json=body_dict)

    
    if return_type == 'boolean':
        return response.status_code in [200, 201]
    else:
        return response

def searchresults_get(term, item_type=None, start=None, limit=None, exact_match=None, api_token=None, company_domain='api'):
    """
    Função para realizar uma pesquisa no Pipedrive.

    Parâmetros:
    - term (str): Termo de pesquisa, mínimo de 2 caracteres.
    - item_type (str, opcional): Tipo exato de item a ser pesquisado. Se omitido, todos os tipos de itens são pesquisados. Exemplos: 'deal', 'person', 'organization', 'product', 'file'.
    - start (int, opcional): Início da paginação.
    - limit (int, opcional): Quantidade de itens mostrados por página. O padrão é 500.
    - exact_match (int, opcional): Quando ativado, somente correspondências exatas completas contra o termo fornecido são retornadas (0 = desativado, 1 = ativado).
    - api_token (str): Token da API para validação. Consulte: https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference.
    - company_domain (str): Domínio da empresa. Consulte: https://pipedrive.readme.io/docs/how-to-get-the-company-domain.

    Retorna:
    - pd.DataFrame: DataFrame contendo os resultados da pesquisa.
    """

    api_token = check_api_token(api_token)

    
    url = f'https://{company_domain}.pipedrive.com/v1/searchResults?api_token={api_token}'

     
    body_dict = {
        'term': term,
        'item_type': item_type,
        'start': start if start is not None else 0,
        'limit': limit if limit is not None else 500,
        'exact_match': exact_match
    }

    
    body_dict = clear_list(body_dict)

    
    url += prepare_url_parameters_(body_dict)

    
    return get_all_(url)


def searchresults_get_field(term, field_type, field_key, exact_match=None, return_field_key=None, return_item_ids=None, start=None, limit=None, api_token=None, company_domain='api'):
    """
    Função para realizar uma pesquisa no Pipedrive usando um valor de campo específico.

    Parâmetros:
    - term (str): Termo de pesquisa, mínimo de 2 caracteres.
    - field_type (str): Tipo do campo para realizar a pesquisa. Exemplos: 'dealField', 'personField', 'organizationField', 'productField'.
    - field_key (str): Chave do campo a ser pesquisado. A chave pode ser obtida usando a lista de campos via API de campos.
    - exact_match (int, opcional): Quando ativado, somente correspondências exatas são retornadas (0 = desativado, 1 = ativado).
    - return_field_key (str, opcional): Nome do campo nos resultados de pesquisa. Se omitido, 'value' será utilizado.
    - return_item_ids (int, opcional): Se ativado, retorna os IDs dos itens correspondentes (0 = desativado, 1 = ativado).
    - start (int, opcional): Início da paginação.
    - limit (int, opcional): Quantidade de itens mostrados por página. O padrão é 500.
    - api_token (str): Token da API para validação. Consulte: https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference.
    - company_domain (str): Domínio da empresa. Consulte: https://pipedrive.readme.io/docs/how-to-get-the-company-domain.

    Retorna:
    - pd.DataFrame: DataFrame contendo os resultados da pesquisa.
    """

    api_token = check_api_token(api_token)

    
    url = f'https://{company_domain}.pipedrive.com/v1/searchResults/field?api_token={api_token}'

     
    body_dict = {
        'term': term,
        'exact_match': exact_match,
        'field_type': field_type,
        'field_key': field_key,
        'return_field_key': return_field_key,
        'return_item_ids': return_item_ids,
        'start': start if start is not None else 0,
        'limit': limit if limit is not None else 500
    }

    
    body_dict = clear_list(body_dict)

    
    url += prepare_url_parameters_(body_dict)

    
    return get_all_(url)

def stages_add(name, pipeline_id, deal_probability=None, rotten_flag=None, rotten_days=None, api_token=None, company_domain='api', return_type='complete'):
    """
    Função para adicionar uma nova etapa no Pipedrive.

    Parâmetros:
    - name (str): Nome da etapa.
    - pipeline_id (str): ID do pipeline ao qual a etapa será adicionada.
    - deal_probability (int, opcional): Percentual de probabilidade de sucesso do negócio. Usado quando valores ponderados são utilizados.
    - rotten_flag (int, opcional): Indica se negócios nessa etapa podem se tornar obsoletos (0 = não, 1 = sim).
    - rotten_days (int, opcional): Número de dias que os negócios não atualizados nesta etapa se tornam obsoletos. Aplica-se apenas se `rotten_flag` estiver definido.
    - api_token (str): Token da API para validação. Consulte: https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference.
    - company_domain (str): Domínio da empresa. Consulte: https://pipedrive.readme.io/docs/how-to-get-the-company-domain.
    - return_type (str, opcional): Tipo de retorno ('complete' para retornar toda a resposta, 'boolean' para verificar apenas sucesso/erro).

    Retorna:
    - Objeto de resposta da requisição ou valor booleano indicando sucesso/erro.
    """

    api_token = check_api_token(api_token)

    
    url = f'https://{company_domain}.pipedrive.com/v1/stages?api_token={api_token}'

     
    body_dict = {
        'name': name,
        'pipeline_id': pipeline_id,
        'deal_probability': deal_probability,
        'rotten_flag': rotten_flag,
        'rotten_days': rotten_days
    }

    
    body_dict = clear_list(body_dict)

    
    response = requests.post(url, json=body_dict)

    
    if return_type == 'boolean':
        return response.status_code in [200, 201]
    else:
        return response

def stages_delete(id, api_token=None, company_domain='api', return_type='complete'):
    """
    Função para deletar uma etapa no Pipedrive.

    Parâmetros:
    - id (str): ID da etapa a ser deletada.
    - api_token (str): Token da API para validação. Consulte: https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference.
    - company_domain (str): Domínio da empresa. Consulte: https://pipedrive.readme.io/docs/how-to-get-the-company-domain.
    - return_type (str, opcional): Tipo de retorno ('complete' para retornar toda a resposta, 'boolean' para verificar apenas sucesso/erro).

    Retorna:
    - Objeto de resposta da requisição ou valor booleano indicando sucesso/erro.
    """

    api_token = check_api_token(api_token)

    
    url = f'https://{company_domain}.pipedrive.com/v1/stages/{id}?api_token={api_token}'

    
    response = requests.delete(url)

    
    if return_type == 'boolean':
        return response.status_code in [200, 201]
    else:
        return response


def stages_delete_multiple(ids, api_token=None, company_domain='api', return_type='complete'):
    """
    Função para deletar várias etapas em massa no Pipedrive.

    Parâmetros:
    - ids (str): IDs das etapas a serem deletadas, separados por vírgulas.
    - api_token (str): Token da API para validação. Consulte: https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference.
    - company_domain (str): Domínio da empresa. Consulte: https://pipedrive.readme.io/docs/how-to-get-the-company-domain.
    - return_type (str, opcional): Tipo de retorno ('complete' para retornar toda a resposta, 'boolean' para verificar apenas sucesso/erro).

    Retorna:
    - Objeto de resposta da requisição ou valor booleano indicando sucesso/erro.
    """

    api_token = check_api_token(api_token)

    
    url = f'https://{company_domain}.pipedrive.com/v1/stages?api_token={api_token}'

    
    body_dict = {
        'ids': ids
    }

    response = requests.delete(url, json=body_dict)

    
    if return_type == 'boolean':
        return response.status_code in [200, 201]
    else:
        return response

def stages_get(id, api_token=None, company_domain='api'):
    """
    Função para obter uma etapa específica no Pipedrive.

    Parâmetros:
    - id (str): ID da etapa.
    - api_token (str): Token da API para validação. Consulte: https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference.
    - company_domain (str): Domínio da empresa. Consulte: https://pipedrive.readme.io/docs/how-to-get-the-company-domain.

    Retorna:
    - pd.DataFrame: DataFrame contendo os detalhes da etapa.
    """

    api_token = check_api_token(api_token)

    
    url = f'https://{company_domain}.pipedrive.com/v1/stages/{id}?api_token={api_token}'

    
    return get_all_(url)

def stages_get_deals(id, filter_id=None, user_id=None, everyone=None, start=None, limit=None, api_token=None, company_domain='api'):
    """
    Função para obter negócios em uma etapa específica no Pipedrive.

    Parâmetros:
    - id (str): ID da etapa.
    - filter_id (str, opcional): Se fornecido, apenas os negócios que correspondem ao filtro dado serão retornados.
    - user_id (str, opcional): Se fornecido, o filter_id não será considerado e apenas os negócios pertencentes ao usuário dado serão retornados.
    - everyone (int, opcional): Se fornecido, o filter_id e o user_id não serão considerados, em vez disso, os negócios pertencentes a todos serão retornados (0 = desativado, 1 = ativado).
    - start (int, opcional): Início da paginação.
    - limit (int, opcional): Quantidade de itens mostrados por página. O padrão é 500.
    - api_token (str): Token da API para validação. Consulte: https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference.
    - company_domain (str): Domínio da empresa. Consulte: https://pipedrive.readme.io/docs/how-to-get-the-company-domain.

    Retorna:
    - pd.DataFrame: DataFrame contendo os negócios na etapa.
    """

    api_token = check_api_token(api_token)

    
    url = f'https://{company_domain}.pipedrive.com/v1/stages/{id}/deals?api_token={api_token}'

     
    body_dict = {
        'filter_id': filter_id,
        'user_id': user_id,
        'everyone': everyone,
        'start': start if start is not None else 0,
        'limit': limit if limit is not None else 500
    }

    
    body_dict = clear_list(body_dict)

    
    url += prepare_url_parameters_(body_dict)

    
    return get_all_(url)

def stages_get_all(pipeline_id=None, api_token=None, company_domain='api'):
    """
    Função para obter todas as etapas no Pipedrive.

    Parâmetros:
    - pipeline_id (str, opcional): ID do pipeline para buscar as etapas. Se omitido, as etapas de todos os pipelines serão buscadas.
    - api_token (str): Token da API para validação. Consulte: https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference.
    - company_domain (str): Domínio da empresa. Consulte: https://pipedrive.readme.io/docs/how-to-get-the-company-domain.

    Retorna:
    - pd.DataFrame: DataFrame contendo todas as etapas.
    """

    api_token = check_api_token(api_token)

    
    url = f'https://{company_domain}.pipedrive.com/v1/stages?api_token={api_token}'

     
    params = {}
    if pipeline_id is not None:
        params['pipeline_id'] = pipeline_id

    
    return get_all_(url, params=params)


def stages_update(id, name=None, pipeline_id=None, order_nr=None, deal_probability=None, rotten_flag=None, rotten_days=None, api_token=None, company_domain='api', return_type='complete'):
    """
    Função para atualizar os detalhes de uma etapa no Pipedrive.

    Parâmetros:
    - id (str): ID da etapa a ser atualizada.
    - name (str, opcional): Nome da etapa.
    - pipeline_id (str, opcional): ID do pipeline ao qual essa etapa pertence.
    - order_nr (int, opcional): Número de ordem para esta etapa. Usado para ordenar as etapas no pipeline.
    - deal_probability (int, opcional): Percentual de probabilidade de sucesso do negócio.
    - rotten_flag (int, opcional): Indica se os negócios nesta etapa podem se tornar obsoletos (0 = não, 1 = sim).
    - rotten_days (int, opcional): Número de dias que os negócios não atualizados nesta etapa se tornam obsoletos. Aplica-se apenas se `rotten_flag` estiver definido.
    - api_token (str): Token da API para validação. Consulte: https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference.
    - company_domain (str): Domínio da empresa. Consulte: https://pipedrive.readme.io/docs/how-to-get-the-company-domain.
    - return_type (str, opcional): Tipo de retorno ('complete' para retornar toda a resposta, 'boolean' para verificar apenas sucesso/erro).

    Retorna:
    - Objeto de resposta da requisição ou valor booleano indicando sucesso/erro.
    """

    api_token = check_api_token(api_token)

    
    url = f'https://{company_domain}.pipedrive.com/v1/stages/{id}?api_token={api_token}'

     
    body_dict = {
        'name': name,
        'pipeline_id': pipeline_id,
        'order_nr': order_nr,
        'deal_probability': deal_probability,
        'rotten_flag': rotten_flag,
        'rotten_days': rotten_days
    }

    
    body_dict = clear_list(body_dict)

    
    response = requests.put(url, json=body_dict)

    
    if return_type == 'boolean':
        return response.status_code in [200, 201]
    else:
        return response

def userconnections_get_all(api_token=None, company_domain='api'):
    """
    Função para obter todas as conexões de usuários no Pipedrive.

    Parâmetros:
    - api_token (str): Token da API para validação. Consulte: https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference.
    - company_domain (str): Domínio da empresa. Consulte: https://pipedrive.readme.io/docs/how-to-get-the-company-domain.

    Retorna:
    - pd.DataFrame: DataFrame contendo todas as conexões de usuários.
    """

    api_token = check_api_token(api_token)

    
    url = f'https://{company_domain}.pipedrive.com/v1/userConnections?api_token={api_token}'

    
    return get_all_(url)

def users_add(name, email, active_flag, api_token=None, company_domain='api', return_type='complete'):
    """
    Função para adicionar um novo usuário no Pipedrive.

    Parâmetros:
    - name (str): Nome do usuário.
    - email (str): Email do usuário.
    - active_flag (int): Indica se o usuário está ativo ou não (0 = Não ativado, 1 = Ativado).
    - api_token (str): Token da API para validação. Consulte: https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference.
    - company_domain (str): Domínio da empresa. Consulte: https://pipedrive.readme.io/docs/how-to-get-the-company-domain.
    - return_type (str, opcional): Tipo de retorno ('complete' para retornar toda a resposta, 'boolean' para verificar apenas sucesso/erro).

    Retorna:
    - Objeto de resposta da requisição ou valor booleano indicando sucesso/erro.
    """

    api_token = check_api_token(api_token)

    
    url = f'https://{company_domain}.pipedrive.com/v1/users?api_token={api_token}'

     
    body_dict = {
        'name': name,
        'email': email,
        'active_flag': active_flag
    }

    
    body_dict = clear_list(body_dict)

    response = requests.post(url, json=body_dict)

    
    if return_type == 'boolean':
        return response.status_code in [200, 201]
    else:
        return response


def users_add_blacklisted_emails(id, address, api_token=None, company_domain='api', return_type='complete'):
    """
    Função para adicionar um endereço de e-mail à lista negra de um usuário no Pipedrive.

    Parâmetros:
    - id (str): ID do usuário.
    - address (str): Endereço de e-mail a ser colocado na lista negra (pode conter * para curingas, por exemplo, *@example.com ou john*@ex*.com).
    - api_token (str): Token da API para validação. Consulte: https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference.
    - company_domain (str): Domínio da empresa. Consulte: https://pipedrive.readme.io/docs/how-to-get-the-company-domain.
    - return_type (str, opcional): Tipo de retorno ('complete' para retornar toda a resposta, 'boolean' para verificar apenas sucesso/erro).

    Retorna:
    - Objeto de resposta da requisição ou valor booleano indicando sucesso/erro.
    """

    api_token = check_api_token(api_token)

    
    url = f'https://{company_domain}.pipedrive.com/v1/users/{id}/blacklistedEmails?api_token={api_token}'

     
    body_dict = {
        'address': address
    }

     
    response = requests.post(url, json=body_dict)

    
    if return_type == 'boolean':
        return response.status_code in [200, 201]
    else:
        return response

def users_add_role_assignments(id, role_id, api_token=None, company_domain='api', return_type='complete'):
    """
    Função para adicionar uma atribuição de função a um usuário no Pipedrive.

    Parâmetros:
    - id (str): ID do usuário.
    - role_id (str): ID da função a ser atribuída.
    - api_token (str): Token da API para validação. Consulte: https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference.
    - company_domain (str): Domínio da empresa. Consulte: https://pipedrive.readme.io/docs/how-to-get-the-company-domain.
    - return_type (str, opcional): Tipo de retorno ('complete' para retornar toda a resposta, 'boolean' para verificar apenas sucesso/erro).

    Retorna:
    - Objeto de resposta da requisição ou valor booleano indicando sucesso/erro.
    """

    api_token = check_api_token(api_token)

    
    url = f'https://{company_domain}.pipedrive.com/v1/users/{id}/roleAssignments?api_token={api_token}'

     
    body_dict = {
        'role_id': role_id
    }

    response = requests.post(url, json=body_dict)

    
    if return_type == 'boolean':
        return response.status_code in [200, 201]
    else:
        return response

def users_delete_role_assignments(id, role_id, api_token=None, company_domain='api', return_type='complete'):
    """
    Função para deletar uma atribuição de função de um usuário no Pipedrive.

    Parâmetros:
    - id (str): ID do usuário.
    - role_id (str): ID da função a ser removida.
    - api_token (str): Token da API para validação. Consulte: https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference.
    - company_domain (str): Domínio da empresa. Consulte: https://pipedrive.readme.io/docs/how-to-get-the-company-domain.
    - return_type (str, opcional): Tipo de retorno ('complete' para retornar toda a resposta, 'boolean' para verificar apenas sucesso/erro).

    Retorna:
    - Objeto de resposta da requisição ou valor booleano indicando sucesso/erro.
    """

    api_token = check_api_token(api_token)

    
    url = f'https://{company_domain}.pipedrive.com/v1/users/{id}/roleAssignments?api_token={api_token}'

    response = requests.delete(url)

    
    if return_type == 'boolean':
        return response.status_code in [200, 201]
    else:
        return response


def users_find(term, search_by_email=None, api_token=None, company_domain='api'):
    """
    Função para encontrar usuários pelo nome no Pipedrive.

    Parâmetros:
    - term (str): Termo de pesquisa para procurar.
    - search_by_email (int, opcional): Quando habilitado, o termo será comparado apenas com os endereços de e-mail dos usuários. Padrão: 0 (falso).
    - api_token (str): Token da API para validação. Consulte: https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference.
    - company_domain (str): Domínio da empresa. Consulte: https://pipedrive.readme.io/docs/how-to-get-the-company-domain.

    Retorna:
    - Objeto de resposta da requisição.
    """

    api_token = check_api_token(api_token)

    
    url = f'https://{company_domain}.pipedrive.com/v1/users/find?api_token={api_token}'

     
    body_dict = {
        'term': term,
        'search_by_email': search_by_email
    }

    
    body_dict = {k: v for k, v in body_dict.items() if v is not None}

    
    response = requests.get(url, params=body_dict)

    
    return response


def users_get(id, api_token=None, company_domain='api'):
    """
    Função para obter um usuário do Pipedrive.

    Parâmetros:
    - id (str): ID do usuário a ser buscado.
    - api_token (str): Token da API para validação. Consulte: https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference.
    - company_domain (str): Domínio da empresa. Consulte: https://pipedrive.readme.io/docs/how-to-get-the-company-domain.

    Retorna:
    - Objeto de resposta da requisição.
    """

    api_token = check_api_token(api_token)

    
    url = f'https://{company_domain}.pipedrive.com/v1/users/{id}?api_token={api_token}'

    
    response = requests.get(url)

    
    return response


def users_get_activities(id, due_date=None, activity_type=None, start=None, limit=None, done=None, api_token=None, company_domain='api'):
    """
    Função para listar e filtrar atividades atribuídas a um usuário específico no Pipedrive.

    Parâmetros:
    - id (str): ID do usuário.
    - due_date (str, opcional): Data de vencimento no formato YYYY-MM-DD ou um dos seguintes: all, overdue, today, tomorrow, this_week, next_week.
    - activity_type (str, opcional): Filtrar atividades com base na chave do tipo de atividade (exemplos: call, meeting).
    - start (int, opcional): Início da paginação.
    - limit (int, opcional): Itens mostrados por página.
    - done (int, opcional): Se busca atividades feitas (1) ou não feitas (0). Se omitido, ambas as atividades feitas e não feitas são buscadas. 
    - api_token (str): Token da API para validação. Consulte: https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference.
    - company_domain (str): Domínio da empresa. Consulte: https://pipedrive.readme.io/docs/how-to-get-the-company-domain.

    Retorna:
    - Objeto de resposta da requisição.
    """

    api_token = check_api_token(api_token)

    
    url = f'https://{company_domain}.pipedrive.com/v1/users/{id}/activities?api_token={api_token}'

    params = {
        'due_date': due_date,
        'type': activity_type,
        'start': start,
        'limit': limit,
        'done': done
    }

    
    params = {k: v for k, v in params.items() if v is not None}

    
    response = requests.get(url, params=params)

    
    return response


def users_get_blacklisted_emails(id, api_token=None, company_domain='api'):
    """
    Função para listar endereços de email bloqueados de um usuário no Pipedrive.

    Parâmetros:
    - id (str): ID do usuário.
    - api_token (str): Token da API para validação. Consulte: 
                       https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference.
    - company_domain (str): Domínio da empresa. Consulte: 
                            https://pipedrive.readme.io/docs/how-to-get-the-company-domain.

    Retorna:
    - Objeto de resposta da requisição.
    """

    api_token = check_api_token(api_token)

    
    url = f'https://{company_domain}.pipedrive.com/v1/users/{id}/blacklistedEmails?api_token={api_token}'

    
    response = requests.get(url)

    
    return response



def users_get_followers(id, api_token=None, company_domain='api'):
    """
    Função para listar seguidores de um usuário no Pipedrive.

    Parâmetros:
    - id (str): ID do usuário.
    - api_token (str): Token da API para validação. Consulte: 
                       https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference.
    - company_domain (str): Domínio da empresa. Consulte: 
                            https://pipedrive.readme.io/docs/how-to-get-the-company-domain.

    Retorna:
    - Objeto de resposta da requisição.
    """
    
    api_token = check_api_token(api_token)

    
    url = f'https://{company_domain}.pipedrive.com/v1/users/{id}/followers?api_token={api_token}'

    response = requests.get(url)

    
    return response

def users_get_permissions(user_id, api_token=None, company_domain='api'):
    """
    Função para listar permissões de um usuário no Pipedrive.

    Parâmetros:
    - user_id (str): ID do usuário.
    - api_token (str): Token da API para validação. Consulte: 
                       https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference.
    - company_domain (str): Domínio da empresa. Consulte: 
                            https://pipedrive.readme.io/docs/how-to-get-the-company-domain.

    Retorna:
    - Objeto de resposta da requisição.
    """
    
    api_token = check_api_token(api_token)

    
    url = f'https://{company_domain}.pipedrive.com/v1/users/{user_id}/permissions?api_token={api_token}'

    
    response = requests.get(url)

    
    return response

def users_get_role_assignments(user_id, start=None, limit=None, api_token=None, company_domain='api'):
    """
    Função para listar atribuições de função de um usuário no Pipedrive.

    Parâmetros:
    - user_id (str): ID do usuário.
    - start (int): Início da paginação.
    - limit (int): Itens mostrados por página.
    - api_token (str): Token da API para validação. Consulte: 
                       https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference.
    - company_domain (str): Domínio da empresa. Consulte: 
                            https://pipedrive.readme.io/docs/how-to-get-the-company-domain.

    Retorna:
    - Objeto de resposta da requisição.
    """
    
    api_token = check_api_token(api_token)

    
    url = f'https://{company_domain}.pipedrive.com/v1/users/{user_id}/roleAssignments?api_token={api_token}'

    
    params = {}
    if start is not None:
        params['start'] = start
    if limit is not None:
        params['limit'] = limit or 500  

    response = requests.get(url, params=params)

    
    return response


def users_get_role_settings(user_id, api_token=None, company_domain='api'):
    """
    Função para listar as configurações de função de um usuário no Pipedrive.

    Parâmetros:
    - user_id (str): ID do usuário.
    - api_token (str): Token da API para validação. Consulte: 
                       https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference.
    - company_domain (str): Domínio da empresa. Consulte: 
                            https://pipedrive.readme.io/docs/how-to-get-the-company-domain.

    Retorna:
    - Objeto de resposta da requisição.
    """
    
    api_token = check_api_token(api_token)

    
    url = f'https://{company_domain}.pipedrive.com/v1/users/{user_id}/roleSettings?api_token={api_token}'

    response = requests.get(url)

    
    return response

def users_get_all(api_token=None, company_domain='api'):
    """
    Função para obter todos os usuários do Pipedrive.

    Parâmetros:
    - api_token (str): Token da API para validação. Consulte: 
                       https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference.
    - company_domain (str): Domínio da empresa. Consulte: 
                            https://pipedrive.readme.io/docs/how-to-get-the-company-domain.

    Retorna:
    - Objeto de resposta da requisição.
    """
    
    api_token = check_api_token(api_token)


    url = f'https://{company_domain}.pipedrive.com/v1/users?api_token={api_token}'

    response = requests.get(url)

    return response


def users_me(api_token=None, company_domain='api'):
    """
    Função para obter os dados do usuário atual do Pipedrive.

    Parâmetros:
    - api_token (str): Token da API para validação. Consulte: 
                       https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference.
    - company_domain (str): Domínio da empresa. Consulte: 
                            https://pipedrive.readme.io/docs/how-to-get-the-company-domain.

    Retorna:
    - Objeto de resposta da requisição.
    """

    api_token = check_api_token(api_token)

    url = f'https://{company_domain}.pipedrive.com/v1/users/me?api_token={api_token}'

    response = requests.get(url)

    return response

def users_update(id, active_flag, api_token=None, company_domain='api', return_type='complete'):
    """
    Função para atualizar os detalhes do usuário no Pipedrive.

    Parâmetros:
    - id (int): ID do usuário a ser atualizado.
    - active_flag (int): Indica se o usuário está ativo (1) ou não (0).
    - api_token (str): Token da API para validação.
                       Consulte: https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference.
    - company_domain (str): Domínio da empresa.
                            Consulte: https://pipedrive.readme.io/docs/how-to-get-the-company-domain.
    - return_type (str): O retorno pode ser 'complete' (detalhes da resposta) ou 'boolean' (sucesso/falha).

    Retorna:
    - Objeto de resposta ou um valor booleano.
    """

    api_token = check_api_token(api_token)

    url = f'https://{company_domain}.pipedrive.com/v1/users/{id}?api_token={api_token}'

    body = {'active_flag': active_flag}

    response = requests.put(url, json=body)

    if return_type == 'boolean':
        return response.status_code in {200, 201}
    else:
        return response.json()  

def usersettings_get(api_token=None, company_domain='api'):
    """
    Função para listar as configurações do usuário autorizado no Pipedrive.

    Parâmetros:
    - api_token (str): Token da API para validação.
                       Consulte: https://pipedrive.readme.io/docs/how-to-find-the-api-token?utm_source=api_reference.
    - company_domain (str): Domínio da empresa.
                            Consulte: https://pipedrive.readme.io/docs/how-to-get-the-company-domain.

    Retorna:
    - Objeto de resposta com as configurações do usuário.
    """

    api_token = check_api_token(api_token)

    url = f'https://{company_domain}.pipedrive.com/v1/userSettings?api_token={api_token}'

    response = requests.get(url)

    return response.json()

def webhooks_add(subscription_url, event_action, event_object, user_id=None, http_auth_user=None, 
                 http_auth_password=None, api_token=None, company_domain='api', return_type='complete'):
    """
    Function to create a new webhook on Pipedrive.

    Parameters:
    - subscription_url (str): A full, valid, publicly accessible URL to send notifications to.
    - event_action (str): Type of action to receive notifications about (e.g., added, updated, merged, deleted, *).
    - event_object (str): Type of object to receive notifications about (e.g., activity, deal, note, organization, person, *).
    - user_id (int): ID of the user for authorization (optional).
    - http_auth_user (str): HTTP basic auth username of the subscription URL endpoint (if required).
    - http_auth_password (str): HTTP basic auth password of the subscription URL endpoint (if required).
    - api_token (str): Token to validate requests.
    - company_domain (str): The company domain to connect to Pipedrive.
    - return_type (str): The return type (default is 'complete', can also be 'boolean').

    Returns:
    - dict or bool: Response object if return_type is 'complete', True/False if return_type is 'boolean'.
    """

    api_token = check_api_token(api_token)


    url = f'https://{company_domain}.pipedrive.com/v1/webhooks?api_token={api_token}'


    payload = {
        'subscription_url': subscription_url,
        'event_action': event_action,
        'event_object': event_object,
        'user_id': user_id,
        'http_auth_user': http_auth_user,
        'http_auth_password': http_auth_password
    }
    
    payload = {k: v for k, v in payload.items() if v is not None}

    response = requests.post(url, json=payload)

 
    if return_type == 'boolean':
        return response.status_code in [200, 201]
    else:
        return response.json()

def webhooks_delete(id, api_token=None, company_domain='api', return_type='complete'):
    """
    Function to delete an existing webhook on Pipedrive.

    Parameters:
    - id (str): ID of the webhook to delete.
    - api_token (str): Token to validate requests.
    - company_domain (str): The company domain to connect to Pipedrive.
    - return_type (str): The return type (default is 'complete', can also be 'boolean').

    Returns:
    - dict or bool: Response object if return_type is 'complete', True/False if return_type is 'boolean'.
    """

 
    api_token = check_api_token(api_token)


    url = f'https://{company_domain}.pipedrive.com/v1/webhooks/{id}?api_token={api_token}'


    response = requests.delete(url)


    if return_type == 'boolean':
        return response.status_code in [200, 201]
    else:
        return response.json()


def webhooks_get_all(api_token=None, company_domain='api'):
    """
    Function to get all webhooks from Pipedrive.

    Parameters:
    - api_token (str): Token to validate requests.
    - company_domain (str): The company domain to connect to Pipedrive.

    Returns:
    - dict: Response object containing the list of webhooks.
    """


    api_token = check_api_token(api_token)

    url = f'https://{company_domain}.pipedrive.com/v1/webhooks?api_token={api_token}'

    response = requests.get(url)

    return response.json()
