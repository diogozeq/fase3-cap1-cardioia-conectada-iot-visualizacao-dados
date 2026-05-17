# Relatorio Parte 1 - Edge Computing e Resiliencia Offline

## Contexto

A Fase 3 do CardioIA continua o trabalho iniciado na Fase 1, em que foram levantados dados cardiologicos numericos, textuais e visuais com preocupacao de origem, governanca, vies e LGPD. Na Fase 3, esses principios saem da camada de preparacao de dados e entram em um fluxo de monitoramento continuo com IoT.

O objetivo desta parte e simular um dispositivo vestivel com ESP32 no Wokwi, capaz de capturar sinais vitais, processar leituras localmente e manter funcionamento mesmo em perda temporaria de conexao.

## Sensores simulados

O projeto usa dois sensores principais:

- DHT22: sensor obrigatorio para temperatura e umidade.
- Botao/pushbutton: usado para simular pulsos cardiacos e estimar BPM.

Tambem foi incluido um switch de movimento para enriquecer o monitoramento. Esse dado permite simular ausencia de movimento, importante em pacientes cardiologicos acompanhados remotamente.

## Fluxo local

O ESP32 executa o seguinte ciclo:

1. Le temperatura e umidade pelo DHT22.
2. Conta acionamentos do botao para estimar BPM.
3. Le o status de movimento.
4. Classifica risco localmente.
5. Gera um payload JSON com dados do paciente.
6. Se houver conexao, publica via MQTT.
7. Se nao houver conexao, guarda a leitura no buffer Edge.

## Resiliencia offline

O enunciado cita SPIFFS, mas tambem informa que no Wokwi esse recurso e volatil. Por isso, a implementacao usa um buffer circular em memoria com limite de 240 amostras (aproximadamente 20 minutos de coleta com intervalo de 5 segundos). O limite foi calibrado para caber confortavelmente na DRAM do ESP32 e cobrir cenarios realistas de queda de conectividade em ambiente domiciliar. Essa escolha preserva o comportamento esperado de Edge Computing no simulador: o dispositivo continua coletando dados mesmo offline e sincroniza o backlog quando volta a ficar online.

Quando o limite e atingido, a leitura mais antiga e descartada. Essa politica foi escolhida porque, em monitoramento cardiologico, as leituras mais recentes tendem a ser mais relevantes para decisao imediata. Em um ESP32 fisico, a mesma estrategia pode ser persistida em SPIFFS ou microSD.

## Relacao com a Fase 1

A Fase 1 ja havia documentado variaveis clinicas relevantes, como frequencia cardiaca, pressao, risco cardiovascular, qualidade dos dados e vies. A Fase 3 usa esse repertorio para justificar o monitoramento de BPM, temperatura e movimento, mantendo a preocupacao com transparencia e responsabilidade no uso de dados de saude.
