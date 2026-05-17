# Relatorio Ir Alem 1 - REST, Risco e E-mail Automatizado

## Objetivo

O Ir Alem 1 implementa uma API REST em Python para receber sinais vitais, consultar leituras recentes, listar alertas e disparar e-mails automaticos em caso de risco. Essa camada simula a integracao do monitoramento IoT com sistemas de automacao hospitalar.

## API REST

A API foi implementada com FastAPI em `api-rest/app.py`. Os endpoints principais sao:

- `POST /vitals`: recebe sinais vitais.
- `GET /vitals/latest`: retorna a ultima leitura.
- `GET /alerts`: lista alertas.
- `POST /simulate`: gera leitura critica de teste.

O cliente `api-rest/client.py` permite enviar leituras normais ou simulacoes de risco.

## Logica de risco

A classificacao esta em `api-rest/risk.py`. Ela reaproveita conceitualmente a triagem da Fase 2: sinais sao analisados e transformados em uma classificacao simples de risco. As regras consideram taquicardia, bradicardia, febre e ausencia de movimento.

## E-mail

O envio usa SMTP real em `api-rest/emailer.py`. As credenciais ficam no `.env`, seguindo boas praticas de seguranca. Em caso de alerta, a API monta uma mensagem com paciente, sinais vitais, nivel de risco e motivo.

Esse fluxo demonstra uma automacao de resposta: o sistema nao apenas exibe dados, mas tambem aciona comunicacao ativa quando detecta risco.
