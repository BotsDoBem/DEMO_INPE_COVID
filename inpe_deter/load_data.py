import requests


def deter():
    url = 'http://terrabrasilis.dpi.inpe.br/homologation/file-delivery/download/deter-amz/daily'
    r = requests.get(url)
    return r.json()


#####Acessando dados

def setting_dados_deter():
    deter_dados = deter()
    estados, municipios, ucs, causas = [], [], [], []
    for i, row in enumerate(deter_dados["features"]):
        # if deter_dados["features"][i]["properties"]["h"] == 'MT':
        #     deter_dados["features"][i]["properties"]["h"] = 'Mato Grosso(MT)'
        # elif deter_dados["features"][i]["properties"]["h"] == 'RR':
        #     deter_dados["features"][i]["properties"]["h"] = 'Roraima(RR)'
        # elif deter_dados["features"][i]["properties"]["h"] == 'RO':
        #     deter_dados["features"][i]["properties"]["h"] = 'Rondônia(RO)'
        # elif deter_dados["features"][i]["properties"]["h"] == 'PA':
        #     deter_dados["features"][i]["properties"]["h"] = 'Pará(PA)'
        # elif deter_dados["features"][i]["properties"]["h"] == 'MA':
        #     deter_dados["features"][i]["properties"]["h"] = 'Maranhão(MA)'
        # elif deter_dados["features"][i]["properties"]["h"] == 'AM':
        #     deter_dados["features"][i]["properties"]["h"] = 'Amazonas(AM)'
        # elif deter_dados["features"][i]["properties"]["h"] == 'AC':
        #     deter_dados["features"][i]["properties"]["h"] = 'Acre(AC)'
        # elif deter_dados["features"][i]["properties"]["h"] == 'AP':
        #     deter_dados["features"][i]["properties"]["h"] = 'Amapá(AP)'
        # elif deter_dados["features"][i]["properties"]["h"] == 'MT':
        #     deter_dados["features"][i]["properties"]["h"] = 'Mato Grosso(MT)'
        # elif deter_dados["features"][i]["properties"]["h"] == 'TO':
        #     deter_dados["features"][i]["properties"]["h"] = 'Tocantins(TO)'
        estados.append(row['properties']['h'])
        municipios.append(row['properties']['i'])
        ucs.append(row['properties']['j'])
        causas.append(row["properties"]["c"])
    estados = set(estados)
    municipios = set(municipios)
    ucs = set(ucs)
    causas = set(causas)

    for i in range(len(deter_dados["features"])):
        deter_dados["features"][i]["properties"]["g"] = deter_dados["features"][i]["properties"]["g"].split('-')

    return deter_dados, estados, municipios, ucs, causas

def dado_variacao_percentual_por_mes(ano, mes1, mes2, dados):
    dados_por_data1 = []
    dados_por_data2 = []

    total_por_data1 = {}
    total_por_data2 = {}

    for i in range(len((dados["features"]))):
        if ((dados["features"][i]["properties"]["g"])[0] == ano) \
                and ((dados["features"][i]["properties"]["g"])[1] == mes1):
            dados_por_data1.append(round(dados["features"][i]["properties"]["e"], 2))

    total_por_data1[mes1, ano] = round(sum(dados_por_data1), 2)

    for i in range(len(dados["features"])):
        if ((dados["features"][i]["properties"]["g"])[0] == ano) \
                and ((dados["features"][i]["properties"]["g"])[1] == mes2):
            dados_por_data2.append(round(dados["features"][i]["properties"]["e"], 2))

    total_por_data2[mes2, ano] = round(sum(dados_por_data2), 2)

    try:
        variacao = round((total_por_data2[(mes2, ano)] - total_por_data1[(mes1, ano)]) / total_por_data1[(mes1, ano)], 2)
    except:
        variacao = 0

    return variacao

def dado_variacao_percentual_por_ano(ano, mes, dados):
    area = list(dado_total_por_data(ano, mes, dados).values())[0]


    prev_ano = str(int(ano)-1)
    prev_area = list(dado_total_por_data(prev_ano, mes, dados).values())[0]

    try:
        variation = (area - prev_area) / prev_area
    except:
        variation = 0
    return variation

##################
# DADOS POR ESTADO#
##################

def dados_estado(estado, dados):
    dados_estados = []
    for i in range(len(dados["features"])):
        if dados["features"][i]["properties"]["h"] == estado:
            dados_estados.append(round(dados["features"][i]["properties"]["e"], 2))

    total_dados_estados = round(sum(dados_estados), 2)
    return total_dados_estados


def set_total_estados(dados):
    estados = []
    total_estado = {}
    for i in range(len((dados["features"]))):
        estados.append(dados["features"][i]["properties"]["h"])

    estados = set(estados)
    for estado in set(estados):
        total_estado[estado] = dados_estado(estado, dados)

    return total_estado


def dado_por_estado(dados):
    total_estado = set_total_estados(dados)
    dados_por_estado = sorted(total_estado.items(), key=lambda x: x[1], reverse=True)

    return dados_por_estado


# total_por_estado = dado_por_estado(dados)


def soma_estados(dados):
    total_estado = set_total_estados(dados)
    soma_dados_estados = round(sum(total_estado.values()), 2)
    return soma_dados_estados


def dado_estados_por_data(ano, mes, estados, dados):
    total_por_estado_data = {}

    for estado in estados:
        for i in range(len((dados["features"]))):
            if ((dados["features"][i]["properties"]["g"])[0] == ano) \
                    and ((dados["features"][i]["properties"]["g"])[1] == mes) \
                    and (dados["features"][i]["properties"]["h"] == estado):
                if estado not in total_por_estado_data:
                    total_por_estado_data[estado] = 0
                total_por_estado_data[estado] += dados["features"][i]["properties"]["e"]

    return total_por_estado_data


# testando
# dados_MT_2019_05 = dado_estado_data(2019, 5, 'Mato Grosso(MT)',dados)
# dados_PA_2019_05 = dado_estado_data('2019', '05', 'Pará(PA)')
# dados_AM_2019_05 = dado_estado_data('2019', '05', 'Amazonas(AM)')


def dado_total_por_data(ano, mes, dados):
    dados_por_data = []
    total_por_data = {}

    for i in range(len((dados["features"]))):

        if ((dados["features"][i]["properties"]["g"])[0] == ano) \
                and ((dados["features"][i]["properties"]["g"])[1] == mes):
            dados_por_data.append(round(dados["features"][i]["properties"]["e"], 2))

    total_por_data[mes, ano] = round(sum(dados_por_data), 2)

    return total_por_data


# # testando
# dados_2019_09 = dado_total_por_data(2019, 9, dados)
# dados_2019_06 = dado_total_por_data('2019', '06')


##########################
##PERCENTUAIS POR ESTADO##
##########################

def perc_estados(dados):
    estados = []
    soma_dados_estados = soma_estados(dados)
    porcent_estado = {}
    
    for i in range(len((dados["features"]))):
        estados.append(dados["features"][i]["properties"]["h"])
    estados = set(estados)
    for estado in estados:
        porcent_estado[estado] = round((dados_estado(estado, dados) / soma_dados_estados), 3)

    percentual_por_estado_decresc = sorted(porcent_estado.items(), key=lambda x: x[1], reverse=True)

    return percentual_por_estado_decresc


##################
# DADOS POR municipio#
##################

def dados_municipio(municipio, dados):
    dados_municipios = []
    for i in range(len(dados["features"])):
        if dados["features"][i]["properties"]["i"] == municipio:
            dados_municipios.append(round(dados["features"][i]["properties"]["e"], 2))

    total_dados_municipios = round(sum(dados_municipios), 2)
    return total_dados_municipios


def set_total_municipios(dados):
    municipios = []
    total_municipio = {}
    
    for i in range(len((dados["features"]))):
        municipios.append(dados["features"][i]["properties"]["i"])

    municipios = set(municipios)
    for municipio in set(municipios):
        total_municipio[municipio] = dados_municipio(municipio, dados)

    return total_municipio


def dado_por_municipio(dados):
    total_municipio = set_total_municipios(dados)
    dados_por_municipio = sorted(total_municipio.items(), key=lambda x: x[1], reverse=True)

    return dados_por_municipio


def soma_municipios(dados):
    total_municipio = set_total_municipios(dados)
    soma_dados_municipios = round(sum(total_municipio.values()), 2)
    return soma_dados_municipios


def dado_municipios_por_data(ano, mes, municipios, dados):
    total_por_municipio_data = {}

    for municipio in municipios:
        for i in range(len((dados["features"]))):
            if ((dados["features"][i]["properties"]["g"])[0] == ano) \
                    and ((dados["features"][i]["properties"]["g"])[1] == mes) \
                    and (dados["features"][i]["properties"]["i"] == municipio):
                estado = dados["features"][i]["properties"]["h"]
                if (estado, municipio) not in total_por_municipio_data:
                    total_por_municipio_data[(estado, municipio)] = 0
                total_por_municipio_data[(estado, municipio)] += dados["features"][i]["properties"]["e"]

    return total_por_municipio_data


# testando
# dados_brasnorte_2019_05 = dado_municipio_data(2019, 5, 'Brasnorte', dados)


##########################
##PERCENTUAIS POR municipio##
##########################

def perc_municipios(dados):
    municipios = []
    soma_dados_municipios = soma_municipios(dados)
    porcent_municipio = {}
    
    for i in range(len((dados["features"]))):
        municipios.append(dados["features"][i]["properties"]["i"])
    municipios = set(municipios)
    for municipio in municipios:
        porcent_municipio[municipio] = round((dados_municipio(municipio, dados) / soma_dados_municipios), 3)

    percentual_por_municipio_decresc = sorted(porcent_municipio.items(), key=lambda x: x[1], reverse=True)

    return percentual_por_municipio_decresc


##################
# DADOS POR UC#
##################

def dados_UC(UC, dados):
    dados_UCs = []
    for i in range(len(dados["features"])):
        if dados["features"][i]["properties"]["j"] == UC:
            dados_UCs.append(round(dados["features"][i]["properties"]["f"], 2))

    total_dados_UCs = round(sum(dados_UCs), 2)
    return total_dados_UCs


def set_total_UCs(dados):
    UCs = []
    total_UC = {}
    for i in range(len((dados["features"]))):
        UCs.append(dados["features"][i]["properties"]["j"])
        i += 1
    UCs = set(UCs)
    for UC in set(UCs):
        total_UC[UC] = dados_UC(UC, dados)

    return total_UC


def dado_por_UC(dados):
    total_UC = set_total_UCs(dados)
    dados_por_UC = sorted(total_UC.items(), key=lambda x: x[1], reverse=True)

    return dados_por_UC


# total_por_UC = dado_por_UC(dados)


def soma_UCs(dados):
    total_UC = set_total_UCs(dados)
    soma_dados_UCs = round(sum(total_UC.values()), 2)
    return soma_dados_UCs


def dado_UCs_por_data(ano, mes, UCs, dados):
    total_por_UC_data = {}

    for UC in UCs:
        for i in range(len((dados["features"]))):

            if ((dados["features"][i]["properties"]["g"])[0] == ano) \
                    and ((dados["features"][i]["properties"]["g"])[1] == mes) \
                    and (dados["features"][i]["properties"]["j"] == UC):

                if UC not in total_por_UC_data:
                    total_por_UC_data[UC] = 0
                total_por_UC_data[UC] += dados["features"][i]["properties"]["f"]

    return total_por_UC_data


# teste

# dado_UC_data(2019, 5, 'FLORESTA NACIONAL DO JAMANXIM', dados)
##########################
##PERCENTUAIS POR UC##
##########################

def perc_UCs(dados):
    UCs = []
    soma_dados_UCs = soma_UCs(dados)
    porcent_UC = {}

    for i in range(len(dados["features"])):
        if dados["features"][i]["properties"]["j"] != None:
            UCs.append(dados["features"][i]["properties"]["j"])
    UCs = set(UCs)
    for UC in UCs:
        porcent_UC[UC] = round((dados_UC(UC, dados) / soma_dados_UCs), 4)

    percentual_por_UC_decresc = sorted(porcent_UC.items(), key=lambda x: x[1], reverse=True)

    return percentual_por_UC_decresc



##########################
## POR DATA POR uc##
##########################

def dado_UC_data(ano, mes, UC, dados):

    dados_UC_por_data = []
    total_por_UC_data = {}

    for i in range(len((dados["features"]))):
        if ((dados["features"][i]["properties"]["g"])[0] == ano) \
                and ((dados["features"][i]["properties"]["g"])[1] == mes) \
                and (dados["features"][i]["properties"]["j"] == UC):
            dados_UC_por_data.append(round(dados["features"][i]["properties"]["f"], 2))
            
    total_por_UC_data[UC, mes, ano] = round(sum(dados_UC_por_data), 2)

    return total_por_UC_data


# testando

# dados_JAMANXIM = dado_UC_data(2019, 5, 'FLORESTA NACIONAL DO JAMANXIM',dados)


##################
# DADOS POR classe_desm#
##################

def dados_classe_desm(classe_desm, dados):

    dados_classe_desm = []
    for i in range(len(dados["features"])):
        if dados["features"][i]["properties"]["c"] == classe_desm:
            dados_classe_desm.append(round(dados["features"][i]["properties"]["e"], 2))

    total_dados_classe_desm = round(sum(dados_classe_desm), 2)
    return total_dados_classe_desm


def set_total_classe_desm(dados):

    classe_desm = []
    total_classe_desm = {}
    
    for i in range(len((dados["features"]))):
        classe_desm.append(dados["features"][i]["properties"]["c"])
        
    classe_desm = set(classe_desm)
    for classe_desm in set(classe_desm):
        total_classe_desm[classe_desm] = dados_classe_desm(classe_desm,dados)

    return total_classe_desm


def dado_por_classe_desm(dados):
    total_classe_desm = set_total_classe_desm(dados)
    dados_por_classe_desm = sorted(total_classe_desm.items(), key=lambda x: x[1], reverse=True)

    return dados_por_classe_desm


# total_por_classe_desm = dado_por_classe_desm()


def soma_classe_desm(dados):
    total_classe_desm = set_total_classe_desm(dados)
    soma_dados_classe_desm = round(sum(total_classe_desm.values()), 2)
    return soma_dados_classe_desm


def dado_classe_desm_data(ano, mes, classe_desm, dados):

    dados_classe_desm_por_data = []
    total_por_classe_desm_data = {}

    for i in range(len(dados["features"])):

        if ((dados["features"][i]["properties"]["g"])[0] == ano) \
                and ((dados["features"][i]["properties"]["g"])[1] == mes) \
                and (dados["features"][i]["properties"]["c"] == classe_desm):
            dados_classe_desm_por_data.append(round(dados["features"][i]["properties"]["e"], 2))
            
    total_por_classe_desm_data[classe_desm, mes, ano] = round(sum(dados_classe_desm_por_data), 2)

    return total_por_classe_desm_data

# dado_classe_desm_data(2019, 5, 'DESMATAMENTO_CR', dados)
##########################
##PERCENTUAIS POR classe_desm##
##########################

def perc_classe_desm(dados):
    classe_desms = []
    soma_dados_classe_desm = soma_classe_desm(dados)
    porcent_classe_desm = {}
    
    for i in range(len((dados["features"]))):
        classe_desms.append(dados["features"][i]["properties"]["c"])

    classe_desms = set(classe_desms)
    for classe_desm in classe_desms:
        porcent_classe_desm[classe_desm] = round((dados_classe_desm(classe_desm, dados) / soma_dados_classe_desm), 2)

    percentual_por_classe_desm_decresc = sorted(porcent_classe_desm.items(), key=lambda x: x[1], reverse=True)

    return percentual_por_classe_desm_decresc


##########################
## POR DATA POR classe_desm##
##########################

def dado_causas_por_data(ano, mes, causas, dados):
    total_por_causa = {}

    for causa in causas:
        for i in range(len((dados["features"]))):
            if ((dados["features"][i]["properties"]["g"])[0] == ano) \
                    and ((dados["features"][i]["properties"]["g"])[1] == mes) \
                    and (dados["features"][i]["properties"]["c"] == causa):
                if causa not in total_por_causa:
                    total_por_causa[causa] = 0
                total_por_causa[causa] += dados["features"][i]["properties"]["e"]

    return total_por_causa
