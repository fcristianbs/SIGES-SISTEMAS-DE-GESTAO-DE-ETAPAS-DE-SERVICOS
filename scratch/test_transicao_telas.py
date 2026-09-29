import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.db import get_db_connection, buscar_servicos_db, tramitar_servico_db

print('--- TEST 1: Buscando tela de Medicao (status_in=1,3,6,11,12,13) ---')
med = buscar_servicos_db(status_in='1,3,6,11,12,13', limit=10)
print('Total na Medicao:', med['total'])
st_med = set(s['st'] for s in med['data'])
print('Status presentes na amostra da Medicao:', st_med)
assert 2 not in st_med, 'Erro: Status 2 nao deveria estar na tela de Medicao!'
assert 4 not in st_med, 'Erro: Status 4 nao deveria estar na tela de Medicao!'

print('--- TEST 2: Buscando tela de Pendencias (status_in=2,4,6,7) ---')
pen = buscar_servicos_db(status_in='2,4,6,7', limit=10)
print('Total em Pendencias:', pen['total'])
st_pen = set(s['st'] for s in pen['data'])
print('Status presentes na amostra de Pendencias:', st_pen)

print('--- TEST 3: Validando Ordenacao por Mais Recente Transmitido ---')
if med['data']:
    sid = med['data'][0]['id']
    st_orig = med['data'][0]['st']
    print(f"Tramitando {sid} (status original: {st_orig}) para Status 2 (Pendencias)...")
    res = tramitar_servico_db(sid, 2, 'Teste Script', 'teste@cosampa.com.br')
    print('Resultado tramitacao:', res['status'])
    
    # 1. Agora busca Pendencias de novo
    pen_after = buscar_servicos_db(status_in='2,4,6,7', limit=5)
    primeiro_pen = pen_after['data'][0]['id']
    print(f"Primeiro item em Pendencias apos tramitacao: {primeiro_pen}")
    assert primeiro_pen == sid, f"Esperava que {sid} fosse o primeiro item em Pendencias, mas foi {primeiro_pen}"
    print("SUCESSO: A ordem transmitida caiu no topo (posicao 1) de Pendencias!")
    
    # 2. E verifica se sumiu de Medicao
    med_after = buscar_servicos_db(status_in='1,3,6,11,12,13', limit=10)
    ids_med = [s['id'] for s in med_after['data']]
    assert sid not in ids_med, f"Erro: {sid} ainda aparece na Medicao apos virar pendencia!"
    print("SUCESSO: A ordem transmitida sumiu da tela de Medicao!")
    
    # 3. Agora retorna de Pendencia para Medicao (status 1) simulando RN-04
    print(f"Retornando {sid} de volta para Status 1 (Medicao)...")
    res_retorno = tramitar_servico_db(sid, 1, 'Teste Script', 'teste@cosampa.com.br')
    med_final = buscar_servicos_db(status_in='1,3,6,11,12,13', limit=5)
    primeiro_med = med_final['data'][0]['id']
    print(f"Primeiro item na Medicao apos retorno: {primeiro_med}")
    assert primeiro_med == sid, f"Esperava que {sid} fosse o primeiro da Medicao, mas foi {primeiro_med}"
    print("SUCESSO: Ao retornar para Medicao, a ordem caiu no topo (posicao 1) da Medicao!")
