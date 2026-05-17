# CardioIA — Fase 3: IoT, Edge, Cloud e Visualização de Dados

> FIAP — 2° Ano — Fase 3 (2026)

---

## Integrante

| Nome | RM |
|------|----|
| Diogo Zequini | 565535 |

---

## Continuidade das fases anteriores

Esta entrega é a terceira etapa do CardioIA. As duas anteriores estão aqui:

- **Fase 1 — Busca de Dados:** levantei e curei os três tipos de dados cardiológicos (numéricos do Cleveland, textuais das diretrizes da SBC e visuais de ECG da LUDB), com governança, tratamento de ausentes e análise de viés.
- **Fase 2 — Diagnóstico Automatizado com IA:** pipeline NLP de sintomas, classificador TF-IDF de risco (alto/baixo), MLP para diagnóstico visual de ECG, portal React com autenticação e dashboard, e XAI (SHAP/LIME) para tabular e visão.

Na Fase 3 eu transformo o CardioIA em um sistema **conectado e contínuo**: o que antes era análise sob demanda (uma frase, um exame) agora vira monitoramento em tempo real, com ESP32 capturando sinais vitais, envio MQTT para nuvem, dashboard ao vivo e alerta automático por e-mail.

```text
Fase 1: dados preparados
Fase 2: diagnóstico assistido por IA
Fase 3: monitoramento contínuo conectado (esta entrega)
```

---

## O que foi pedido vs. o que entreguei

### Parte 1 — Edge Computing (ESP32 + sensores + resiliência offline)

| Requisito | Entrega | Arquivo |
|-----------|---------|---------|
| No mínimo 2 sensores, sendo um deles DHT22 | DHT22 (temperatura + umidade) + botão simulando batimentos (BPM por contagem de pressões/min) | `wokwi/diagram.json`, `wokwi/sketch.ino` |
| Simulação de conectividade Wi-Fi via variável booleana | Flag de conexão alternada no loop, com publicação só quando "online" | `wokwi/sketch.ino` |
| Resiliência offline com estratégia de armazenamento limitado | Buffer circular em memória dimensionado para minutos de coleta offline; ao reconectar, faz flush e limpa | `wokwi/sketch.ino` |
| SPIFFS (opcional, dispensado em simulador) | Optei pelo Monitor Serial + buffer em RAM, conforme o próprio enunciado autoriza. Em ESP32 físico, o mesmo conceito migra para SPIFFS ou microSD sem mudar a lógica | — |
| Código C++ comentado | Comentários explicando ciclo de leitura, gatilhos de alerta, fluxo offline/online e payload MQTT | `wokwi/sketch.ino` |
| Relatório (≥1 página) | Fluxo de funcionamento e lógica de resiliência | `docs/relatorio_parte1_edge.md` |

### Parte 2 — Transmissão para nuvem e visualização (Fog/Cloud)

| Requisito | Entrega | Arquivo |
|-----------|---------|---------|
| Envio MQTT do ESP32 para broker em nuvem | HiveMQ Cloud (TLS 8883), tópicos `cardioia/patients/{id}/vitals`, `.../alerts` e `cardioia/system/status` | `wokwi/sketch.ino` |
| Dashboard Node-RED em tempo real | Flow com input MQTT, function de normalização, gráfico de linha (BPM), gauges (temperatura, umidade, buffer offline) e indicador textual de alerta | `node-red/flows_cardioia.json` |
| Gráfico de um sinal vital escolhido | BPM gerado por botão (cada pressão = 1 batimento na janela) | `node-red/flows_cardioia.json` |
| Gauge de outro parâmetro relevante | Temperatura e umidade (vindas do DHT22) | `node-red/flows_cardioia.json` |
| Alerta visual quando passar do limite | Indicador muda de cor e texto quando BPM > 120, temperatura > 38 °C ou ausência de movimento; combinação de fatores marca risco alto | `wokwi/sketch.ino`, `node-red/flows_cardioia.json` |
| Relatório (≥2 páginas) sobre fluxo MQTT e dashboard | Arquitetura, payload, QoS, regras de alerta, segurança e ligação com a Fase 2 | `docs/relatorio_parte2_mqtt_dashboard.md` |

### Ir Além 1 — Comunicação automatizada com REST e e-mail

| Requisito | Entrega | Arquivo |
|-----------|---------|---------|
| API REST em Python para enviar/receber dados | FastAPI com endpoints de ingestão de leituras e consulta | `api-rest/app.py` |
| Cliente REST que envia leituras | Cliente em Python que publica leituras simuladas e dispara cenário de risco com `--simulate-risk` | `api-rest/client.py` |
| Lógica de verificação de risco (taquicardia, febre, ausência de movimento) | Regras isoladas em módulo próprio, replicando os mesmos limiares do ESP32 e do Node-RED | `api-rest/risk.py` |
| Disparo de e-mail automatizado em caso de alerta | Módulo SMTP que envia e-mail com o motivo do alerta e a leitura associada (credenciais via `.env`) | `api-rest/emailer.py` |
| Relatório curto (1–2 páginas) | Fluxo HTTP + lógica de risco + automação de e-mail | `docs/relatorio_ir_alem_1_rest_email.md` |

### Ir Além 2 — IA em séries temporais de saúde

| Requisito | Entrega | Arquivo |
|-----------|---------|---------|
| Notebook Python comentado | Geração de séries simuladas de BPM/temperatura/movimento, janelamento, features estatísticas, treino e avaliação | `notebooks/analise_series_temporais_cardioia.ipynb` |
| Classificador tradicional | Logistic Regression sobre features estatísticas por janela | `notebooks/analise_series_temporais_cardioia.py` |
| Rede neuromórfica simples (LIF/FHN) | Modelo LIF (Leaky Integrate-and-Fire) com contagem de spikes por janela | `notebooks/analise_series_temporais_cardioia.py` |
| Relatório comparativo (2 páginas) | Vantagens e limitações de cada modelo, acurácia, precisão, recall, F1 e leitura crítica | `docs/relatorio_ir_alem_2_ia_series_temporais.md` |
| Vídeo de até 4 min (YouTube não listado) | **Não entreguei o vídeo desta fase** (decisão minha, ciente da perda de pontos só neste opcional) | — |

> Observação: na Fase 2 eu fiz o vídeo (link no README da Fase 2). Nesta Fase 3 optei por não gravar.

---

## Arquitetura

```text
ESP32 (Wokwi) ──TLS/MQTT──► HiveMQ Cloud ──MQTT──► Node-RED Dashboard
        │                                    │
        │                                    └──► API REST (FastAPI) ──► E-mail (SMTP)
        │
        └─ Buffer circular offline (resiliência Edge)

                         Notebook IA séries temporais (Logistic Regression vs LIF)
```

---

## Estrutura do repositório

```text
.
├── api-rest/
│   ├── app.py                # FastAPI (ingestão/consulta de leituras)
│   ├── client.py             # cliente REST de teste
│   ├── risk.py               # regras de taquicardia / febre / ausência de movimento
│   ├── emailer.py            # disparo SMTP de alerta
│   └── requirements.txt
│
├── docs/
│   ├── relatorio_parte1_edge.md
│   ├── relatorio_parte2_mqtt_dashboard.md
│   ├── relatorio_ir_alem_1_rest_email.md
│   ├── relatorio_ir_alem_2_ia_series_temporais.md
│   └── evidencias/           # prints da execução
│
├── node-red/
│   └── flows_cardioia.json   # flow + dashboard
│
├── notebooks/
│   ├── analise_series_temporais_cardioia.ipynb
│   ├── analise_series_temporais_cardioia.py
│   └── requirements.txt
│
└── wokwi/
    ├── diagram.json
    ├── libraries.txt
    └── sketch.ino
```

---

## Como executar

### ESP32 (Wokwi)

1. Abrir o projeto no Wokwi com `wokwi/diagram.json` + `wokwi/sketch.ino`.
2. No `sketch.ino`, substituir as credenciais do broker:

```cpp
const char* MQTT_SERVER   = "SEU_CLUSTER.s1.eu.hivemq.cloud";
const int   MQTT_PORT     = 8883;
const char* MQTT_USER     = "SEU_USUARIO";
const char* MQTT_PASSWORD = "SUA_SENHA";
```

3. Rodar a simulação. Pressionar o botão simula batimentos; o DHT22 varia temperatura e umidade.

### Node-RED

1. Abrir o Node-RED e instalar `node-red-dashboard` se ainda não tiver.
2. Importar `node-red/flows_cardioia.json`.
3. Configurar o nó MQTT broker com as mesmas credenciais do HiveMQ Cloud.
4. Acessar `/ui` para ver o dashboard.

### API REST + e-mail

```bash
cd api-rest
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env   # preencher SMTP_*, EMAIL_TO
uvicorn app:app --reload
```

Testar com cenário de risco:

```bash
python client.py --simulate-risk
```

### Notebook de IA

```bash
cd notebooks
pip install -r requirements.txt
python analise_series_temporais_cardioia.py
```

O `.ipynb` é a versão comentada para apresentação; o `.py` permite rodar tudo rapidamente.

---

## Tópicos MQTT

- `cardioia/patients/cardioia-paciente-001/vitals` — leitura completa (BPM, temperatura, umidade, movimento, risco)
- `cardioia/patients/cardioia-paciente-001/alerts` — eventos de risco
- `cardioia/system/status` — RSSI, memória livre, tamanho do buffer offline (retain ligado)

QoS 1 para vitals/alerts. Identificação do paciente é pseudônimo, não usa nome nem documento — alinhado com a discussão de LGPD que abri na Fase 1.

---

## Links públicos para correção

- Repositório GitHub: https://github.com/diogozeq/fase3-cap1-cardioia-conectada-iot-visualizacao-dados
- Projeto Wokwi: *inserir link aqui*

---

## Observação sobre o SPIFFS

O enunciado avisa que o SPIFFS é volátil nos simuladores Wokwi/PlatformIO e que o item não conta na avaliação. Implementei a resiliência offline com buffer circular em memória, que é o que faz sentido em ambiente de simulação. Em hardware físico, a mesma lógica de buffer + flush ao reconectar pode ser persistida em SPIFFS ou em cartão microSD sem mudança estrutural — o que muda é só a camada de armazenamento.

---

## Licença

<img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1"><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1">

Creative Commons Attribution 4.0 International — [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
