# Motor de Liquidações e Arbitragem DeFi — Base + Solana

Sistema que vigia protocolos de empréstimo na **Base** (Morpho Blue, Aave v3, Moonwell) e na **Solana** (Kamino,
Jupiter Lend), encontra posições liquidáveis, monta a transação completa com **flash loan**, **simula na rede real
com os custos reais** e só então decide enviar. Roda 24/7 em duas VMs gratuitas da Oracle Cloud e manda cada
resultado e cada erro para o Telegram.

Este repositório é um **portfólio**: arquitetura, resultados medidos e uma ferramenta de análise aberta. O código
de execução (assinatura/envio) é privado.

## O que faz
- **Descoberta:** API oficial da Morpho + leitura on-chain (~51 mil posições na Base); varredura de 135 mil+
  obrigações no Kamino; 109 cofres do Jupiter Lend lidos pela própria simulação de liquidação do protocolo.
- **Motor pré-armado:** posições perto da liquidação têm o plano pronto; um vigia dispara quando o oráculo muda.
- **Execução atômica:** flash loan (Morpho, taxa 0) → liquidação → venda do colateral (Uniswap V3, Aerodrome,
  KyberSwap, resgate ERC-4626; Jupiter/Meteora na Solana) → devolução, tudo numa única transação; lucro em USDC.
- **Segurança:** simulação exata antes de todo envio; trava de lucro dentro do contrato (custo de rede + US$ 0,02);
  limite de reverts em 24 h.
- **Autodiagnóstico:** quando uma simulação reverte, o robô lê a rede naquele bloco e diz o porquê (ex.: "já
  liquidada por 0x… no bloco N, oráculo atualizado pelo SVR da Chainlink no mesmo bloco").
- **Observabilidade:** resumo de hora em hora e todo erro com prova no Telegram; ferramentas de linha de comando
  que mostram evidências (radar, funil do motor, simulações aprovadas/reprovadas com motivo).

## Ferramenta aberta: estatísticas de liquidação na Base
`python3 tools/base_liquidation_stats.py 24`. Só biblioteca padrão, RPC pública, só leitura. Responde: **quem ganha
as liquidações na Base e quanto custa?** Resultado real (13 h, 07/11/2026): leilões SVR com 99 liquidações e
~US$ 85 mil de bônus; disputa das sobras com 94 liquidações e 30 tentativas revertidas que queimaram 0,65 ETH de gás.

## Situação, com honestidade
- O motor funciona de ponta a ponta em simulação com posições reais (ex.: 12 de 14 posições grandes com dívida em
  WETH e 8 de 8 posições cbXRP passam a transação completa no preço de liquidação).
- **Ainda sem lucro realizado.** O motivo medido é a estrutura do mercado (leilões SVR e disputa no mesmo bloco),
  documentada pela ferramenta acima.

Detalhes: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) · [docs/CASE_STUDY.md](docs/CASE_STUDY.md)
