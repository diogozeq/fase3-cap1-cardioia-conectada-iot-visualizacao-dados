# Relatorio Ir Alem 2 - IA em Series Temporais de Saude

## Objetivo

O Ir Alem 2 aplica IA para analisar series temporais de sinais vitais. A proposta compara um classificador tradicional, Logistic Regression, com um modelo neuromorfico simples baseado em LIF, avaliando vantagens e limitacoes para uso em monitoramento continuo.

## Dados

O notebook gera series simuladas de BPM, temperatura e movimento. Cada janela representa um periodo de observacao do paciente. Sao criados cenarios normais e cenarios de risco com taquicardia, febre e ausencia de movimento.

Essa escolha e coerente com a Fase 3 porque os dados simulados seguem o mesmo formato dos sinais vitais coletados no ESP32. Tambem aproveita a experiencia da Fase 2 com classificacao e metricas.

## Modelo tradicional

A Logistic Regression usa features estatisticas por janela:

- media do BPM;
- desvio padrao do BPM;
- BPM maximo;
- temperatura media;
- temperatura maxima;
- proporcao de movimento;
- tendencia de BPM.

Esse modelo e simples, interpretavel e barato para executar.

## Modelo neuromorfico LIF

O modelo LIF simula acumulacao de potencial ao longo do tempo. Leituras mais intensas de BPM e temperatura aumentam o potencial; quando o limiar e ultrapassado, ocorre um spike. A contagem de spikes por janela e usada para classificar risco.

## Comparacao

A comparacao considera acuracia, precision, recall, F1 e matriz de confusao. A Logistic Regression tende a ser mais direta para bases pequenas e tabulares. O LIF e interessante para Edge Computing porque processa sinais sequenciais de forma incremental, mas depende de calibracao cuidadosa de limiares.

## Continuidade das fases

A Fase 1 forneceu a base de governanca e relevancia clinica dos dados. A Fase 2 introduziu classificadores e avaliacao. A Fase 3 aplica esses conceitos em sinais vitais continuos, fechando o ciclo do CardioIA como sistema conectado.
