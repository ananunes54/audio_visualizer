import numpy as np
import matplotlib.pyplot as plt
import struct

# --- Parâmetros da Onda (ESSENCIAIS para arquivo binário bruto) ---
TAXA_AMOSTRAGEM = 44100  # Hz (Você DEVE saber isso sobre seu arquivo)
BITS_POR_AMOSTRA = 16    # 16 bits (Você DEVE saber isso sobre seu arquivo)
NUM_CANAIS_ESPERADO = 1  # Assumindo mono. Se for estéreo e intercalado, precisará de tratamento.

# --- Função para ler dados de um arquivo binário bruto (.dat, .bin, .raw) ---
def ler_dados_binario_bruto(nome_arquivo, dtype_esperado=np.int16):
    """
    Lê dados de um arquivo binário bruto.
    Assume que o arquivo contém APENAS amostras no formato especificado (dtype_esperado).
    """
    print(f"Lendo arquivo binário como {dtype_esperado}...")
    try:
        with open(nome_arquivo, 'rb') as f:
            dados_bytes = f.read()
        
        sinal = np.frombuffer(dados_bytes, dtype=dtype_esperado)
        
        # Tratamento de canais (se necessário, descomente e ajuste)
        # if NUM_CANAIS_ESPERADO == 2 and len(sinal) > 0:
        #     print("Assumindo dados estéreo intercalados, pegando o primeiro canal (esquerdo).")
        #     sinal = sinal[::2]
        # elif NUM_CANAIS_ESPERADO > 1 and len(sinal) > 0:
        #     print(f"Assumindo {NUM_CANAIS_ESPERADO} canais intercalados, pegando o primeiro.")
        #     sinal = sinal[::NUM_CANAIS_ESPERADO]

        return sinal, TAXA_AMOSTRAGEM
    except FileNotFoundError:
        print(f"Erro: Arquivo '{nome_arquivo}' não encontrado.")
        return None, None
    except Exception as e:
        print(f"Erro ao ler o arquivo binário bruto '{nome_arquivo}': {e}")
        return None, None

# --- Função para plotar a onda (MODIFICADA) ---
def plotar_onda(sinal_completo, taxa_amostragem, titulo="Onda Sonora", amostras_para_plotar=44100):
    """
    Plota uma porção especificada do sinal de áudio no domínio do tempo.
    Por padrão, plota 'amostras_para_plotar' (44100 amostras = 1 segundo).
    """
    if sinal_completo is None or len(sinal_completo) == 0:
        print("Sinal de entrada vazio ou nulo. Nada para plotar.")
        return

    # Seleciona a porção do sinal para plotar
    if len(sinal_completo) >= amostras_para_plotar:
        sinal_plot = sinal_completo[:amostras_para_plotar]
        print(f"Plotando as primeiras {amostras_para_plotar} amostras ({amostras_para_plotar/taxa_amostragem:.2f} segundos).")
    else:
        sinal_plot = sinal_completo # Plota tudo o que tem
        print(f"Sinal tem menos de {amostras_para_plotar} amostras ({len(sinal_completo)} amostras). "
              f"Plotando todas as amostras disponíveis ({len(sinal_completo)/taxa_amostragem:.2f} segundos).")

    if len(sinal_plot) == 0:
        print("Nenhuma amostra selecionada para plotar.")
        return

    duracao_plotada = len(sinal_plot) / taxa_amostragem
    tempo = np.linspace(0, duracao_plotada, len(sinal_plot), endpoint=False)
    
    plt.figure(figsize=(12, 5))
    plt.plot(tempo, sinal_plot)
    
    titulo_final = f"{titulo} - Primeiras {len(sinal_plot)} amostras ({duracao_plotada:.2f}s)"
    plt.title(titulo_final)
    plt.xlabel("Tempo (s)")
    plt.ylabel("Amplitude")
    plt.grid(True)
    
    max_abs_val = np.max(np.abs(sinal_plot)) if len(sinal_plot) > 0 else 2**(BITS_POR_AMOSTRA -1) -1
    if max_abs_val == 0: 
        max_abs_val = 2**(BITS_POR_AMOSTRA -1) -1
    plt.ylim(-max_abs_val * 1.1, max_abs_val * 1.1)
    
    plt.show()

# --- Principal ---
if __name__ == "__main__":
    # 1. Crie um arquivo binário de exemplo (opcional)
    #    Criado com 1.5s para garantir que haja amostras suficientes para o plot de 1s.
    nome_arquivo_exemplo = "stream_data.bin"
    
    # 2. Especifique o nome do arquivo binário bruto que você quer ler
    arquivo_para_ler = nome_arquivo_exemplo
    # arquivo_para_ler = "SEU_ARQUIVO_BINARIO_AQUI.bin" # <--- COLOQUE O NOME DO SEU ARQUIVO AQUI

    # 3. Especifique a endianness dos dados no seu arquivo binário
    dtype_dados_no_arquivo = np.int16  # Assumindo nativo, geralmente little-endian
    # dtype_dados_no_arquivo = '<i2'    # Forçar little-endian
    # dtype_dados_no_arquivo = '>i2'    # Forçar big-endian

    print(f"\nTentando ler o arquivo binário bruto: {arquivo_para_ler}")
    sinal_audio_completo, sr = ler_dados_binario_bruto(arquivo_para_ler, dtype_esperado=dtype_dados_no_arquivo)
    
    if sinal_audio_completo is not None:
        print(f"Lidas {len(sinal_audio_completo)} amostras no total.")
        print(f"Assumindo taxa de amostragem de {sr} Hz e {BITS_POR_AMOSTRA}-bits por amostra.")
        
        # Plotar as primeiras 44100 amostras (1 segundo)
        plotar_onda(sinal_audio_completo, sr, 
                    titulo=f"Onda Sonora de '{arquivo_para_ler}'", 
                    amostras_para_plotar=44100)
    else:
        print("Não foi possível ler os dados do arquivo.")
