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

Na Fase 3 eu transformo o CardioIA em um sistema **conectado e contínuo**: o que antes era análise sob demanda (uma frase, um exame) agora vira monitoramento em tempo real, com ESP32 capturando sinais vitais, envio MQTT para nuvem e dashboard ao vivo com alerta automático.

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
| No mínimo 2 sensores, sendo um deles DHT22 | DHT22 (temperatura + umidade) + botão simulando batimentos (BPM por contagem de pressões/min) + switch de movimento | `wokwi/diagram.json`, `wokwi/sketch.ino` |
| Simulação de conectividade Wi-Fi via variável booleana | Switch físico no diagrama alterna online/offline em tempo real para testar resiliência | `wokwi/sketch.ino` |
| Resiliência offline com estratégia de armazenamento limitado | Buffer circular em memória de 2.000 amostras (cerca de 2h45 de coleta a cada 5 s); ao reconectar, faz flush completo e limpa | `wokwi/sketch.ino` |
| SPIFFS (opcional, dispensado em simulador) | O próprio enunciado autoriza usar Monitor Serial + buffer em RAM, já que o SPIFFS é volátil em Wokwi. Em ESP32 físico, a mesma lógica migra para SPIFFS ou microSD sem mudar a estrutura | — |
| Código C++ comentado | Comentários explicando ciclo de leitura, gatilhos de alerta, fluxo offline/online e payload MQTT | `wokwi/sketch.ino` |
| Relatório (≥1 página) | Fluxo de funcionamento e lógica de resiliência | `docs/relatorio_parte1_edge.md` |

### Parte 2 — Transmissão para nuvem e visualização (Fog/Cloud)

| Requisito | Entrega | Arquivo |
|-----------|---------|---------|
| Envio MQTT do ESP32 para broker em nuvem | Broker público `broker.hivemq.com:1883`, sem necessidade de credenciais — funciona direto do Wokwi | `wokwi/sketch.ino` |
| Tópicos padronizados | `cardioia/patients/{id}/vitals`, `cardioia/patients/{id}/alerts`, `cardioia/system/status` | `wokwi/sketch.ino` |
| Dashboard Node-RED em tempo real | Flow com input MQTT, function de normalização, gráfico de linha (BPM), gauges (temperatura, umidade, buffer offline) e indicador textual de alerta | `node-red/flows_cardioia.json` |
| Gráfico de um sinal vital escolhido | BPM gerado por botão (cada pressão = 1 batimento na janela) | `node-red/flows_cardioia.json` |
| Gauge de outro parâmetro relevante | Temperatura e umidade (vindas do DHT22) | `node-red/flows_cardioia.json` |
| Alerta visual quando passar do limite | Indicador muda de cor/texto quando BPM > 120, temperatura > 38 °C ou ausência de movimento; combinação de fatores marca risco alto | `wokwi/sketch.ino`, `node-red/flows_cardioia.json` |
| Relatório (≥2 páginas) sobre fluxo MQTT e dashboard | Arquitetura, payload, QoS, regras de alerta, segurança e ligação com a Fase 2 | `docs/relatorio_parte2_mqtt_dashboard.md` |

> Sobre as evidências do dashboard: a demanda permite "prints **ou** export do dashboard Node-RED". O export está em `node-red/flows_cardioia.json` e pode ser importado direto no Node-RED para validação.

---

## Arquitetura

```text
                          Switch WiFi (online/offline)
                                    │
ESP32 (Wokwi) ──MQTT 1883──► broker.hivemq.com ──MQTT──► Node-RED Dashboard
        │
        └─ Buffer circular offline (2000 amostras)
```

---

## Estrutura do repositório

```text
.
├── docs/
│   ├── relatorio_parte1_edge.md
│   ├── relatorio_parte2_mqtt_dashboard.md
│   └── evidencias/
│
├── node-red/
│   └── flows_cardioia.json   # flow + dashboard
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
2. Rodar a simulação — o broker público já está configurado, não precisa preencher nada.
3. Apertar o botão simula batimentos. O switch de Wi-Fi alterna online/offline para mostrar a resiliência (offline acumula no buffer; online faz flush).

### Node-RED

1. Abrir o Node-RED e instalar `node-red-dashboard` se ainda não tiver.
2. Importar `node-red/flows_cardioia.json`.
3. O nó MQTT já está apontando para o broker público. Deploy → abrir `/ui`.

---

## Tópicos MQTT

- `cardioia/patients/cardioia-paciente-001/vitals` — leitura completa (BPM, temperatura, umidade, movimento, risco)
- `cardioia/patients/cardioia-paciente-001/alerts` — eventos de risco
- `cardioia/system/status` — status do dispositivo (retain ligado)

Identificação do paciente é pseudônimo, não usa nome nem documento — alinhado com a discussão de LGPD que abri na Fase 1.

---

## Links públicos para correção

- Repositório GitHub: https://github.com/diogozeq/fase3-cap1-cardioia-conectada-iot-visualizacao-dados
- Projeto Wokwi: https://wokwi.com/projects/464290026879197185

---

## Observação sobre o SPIFFS

O enunciado avisa que o SPIFFS é volátil em simuladores Wokwi/PlatformIO e que o item não conta na avaliação. Implementei a resiliência offline com buffer circular em memória, que é o que faz sentido em ambiente de simulação. Em hardware físico, a mesma lógica de buffer + flush ao reconectar pode ser persistida em SPIFFS ou cartão microSD sem mudança estrutural — o que muda é só a camada de armazenamento.

---

## Licença

<img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1"><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1">

Creative Commons Attribution 4.0 International — [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
