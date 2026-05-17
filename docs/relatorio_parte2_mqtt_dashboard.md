# Relatorio Parte 2 - MQTT, Fog/Cloud e Dashboard Node-RED

## Visao geral

A segunda parte da Fase 3 integra o dispositivo ESP32 ao ambiente de nuvem usando MQTT e apresenta os dados em um dashboard Node-RED. Essa etapa representa a camada Fog/Cloud do CardioIA, conectando captura local, transmissao de dados e visualizacao em tempo real. O resultado e um pipeline ponta a ponta no qual cada batimento simulado no Wokwi e refletido em poucos segundos em graficos, gauges e indicadores de alerta acessiveis a equipe clinica.

O desenho da arquitetura privilegia tres pontos: (i) padronizar o payload para que qualquer consumidor (Node-RED, API REST, notebook de IA) consiga interpretar o mesmo formato; (ii) usar um broker gerenciado para reduzir custo operacional na simulacao academica; (iii) manter o Edge responsavel pelas regras criticas de alerta, de modo que o Node-RED atue como camada de visualizacao e nao como unico ponto de decisao.

## Arquitetura de comunicacao

```text
ESP32 (Wokwi) --TLS/MQTT--> HiveMQ Cloud --MQTT--> Node-RED Dashboard
                                              \--> API REST Python --> E-mail
```

O ESP32 publica em tres topicos. O Node-RED se inscreve nos topicos de vitals e alerts e mantem o status de conexao em um gauge dedicado. A API REST consome eventos pontuais via HTTP, complementando o canal MQTT quando ha necessidade de integracao sincrona com sistemas externos.

## Comunicacao MQTT

O broker definido para a entrega e o HiveMQ Cloud, escolhido por oferecer plano free para simulacao, suporte a TLS na porta 8883 e autenticacao por usuario e senha. O ESP32 publica mensagens JSON em topicos padronizados:

- `cardioia/patients/cardioia-paciente-001/vitals`
- `cardioia/patients/cardioia-paciente-001/alerts`
- `cardioia/system/status`

O payload de vitals inclui identificador do paciente, timestamp em milissegundos, temperatura, umidade, BPM, movimento, status de conexao, nivel de risco e motivo do alerta. O payload de alerts e mais enxuto e carrega tipo do alerta, severidade e leitura associada. O topico de system/status carrega RSSI, uso de memoria livre e tamanho atual do buffer offline, permitindo monitorar o dispositivo.

O formato JSON foi escolhido por ser legivel, facil de processar no Node-RED via function nodes e compativel com APIs REST e bases SQL/NoSQL futuras. QoS 1 e usado para vitals e alerts, garantindo pelo menos uma entrega; retain e habilitado em system/status para que um novo subscriber receba imediatamente o ultimo estado do dispositivo.

## Configuracao do dashboard

O dashboard principal da Fase 3 e o Node-RED, conforme solicitado no enunciado. O flow exportado esta em `node-red/flows_cardioia.json` e possui:

- MQTT input para leituras de sinais vitais.
- Function node para normalizar o payload e separar metricas.
- Grafico de linha para BPM em tempo real.
- Gauge de temperatura.
- Gauge de umidade.
- Indicador textual de alerta com mudanca de cor.
- Gauge de buffer offline, evidenciando a resiliencia do Edge.

Para reproduzir, basta importar o JSON no Node-RED, instalar `node-red-dashboard`, configurar credenciais do HiveMQ Cloud no node MQTT broker e acessar `/ui`. Os mesmos dados ficam disponiveis para uma eventual integracao Grafana Cloud usando MQTT Source ou ponte via InfluxDB.

## Regras de alerta

As regras de alerta replicam, em fluxo continuo, a logica de triagem criada na Fase 2:

- BPM acima de 120: possivel taquicardia.
- Temperatura acima de 38 C: possivel febre.
- Ausencia de movimento por janela definida: sinal de atencao para sincope ou queda.
- Combinacao de dois ou mais fatores: risco alto, com destaque visual no dashboard.

Os limiares foram escolhidos com base em referencia clinica simples e podem ser ajustados via variaveis no sketch ou via context do Node-RED, sem necessidade de redeploy do ESP32.

## Seguranca e boas praticas

Mesmo em ambiente academico, a entrega ja considera praticas que se aplicam a IoT medica real:

- TLS obrigatorio no MQTT, evitando trafego de sinais vitais em texto claro.
- Credenciais fora do codigo final via variaveis no `.env` da API e placeholders no sketch.
- Identificacao por `patient_id` pseudonimo no topico, alinhada a LGPD (sem nome ou documento).
- Logs de status de conexao para auditoria, em consonancia com a governanca discutida na Fase 1.

## Relacao com a Fase 1 e a Fase 2

Na Fase 1, o CardioIA estabeleceu o vocabulario clinico e a governanca dos dados cardiologicos. Na Fase 2, a equipe classificava frases de sintomas e risco clinico usando NLP. Na Fase 3, a mesma ideia e aplicada em fluxo continuo: em vez de classificar texto informado pelo paciente, o sistema classifica leituras de sensores em tempo real. Assim, o alerta do Node-RED representa a continuidade operacional da triagem inteligente feita anteriormente, agora alimentada por IoT em vez de entrada manual.
