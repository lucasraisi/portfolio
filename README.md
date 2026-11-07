# Lucas Raisi — Portfolio

Python / Node.js developer focused on **DeFi automation, on-chain data and applied AI**.
Systems Analysis and Development student (Anhembi Morumbi). AI trainer and model evaluator since 2023 (Appen / Outlier.ai).
I build systems that run 24/7, measure everything and report to Telegram.

*Português abaixo.*

## Featured project

### [DeFi Liquidation & Arbitrage Engine — Base + Solana](defi-liquidation-engine/)
A 24/7 system that monitors ~186,000 lending positions (Morpho Blue, Aave v3, Moonwell on Base; Kamino and Jupiter
Lend on Solana), builds flash-loan liquidations, **simulates them against the live chain with real network costs**,
and reports every result and error to Telegram, with on-chain self-diagnosis.
Includes an open-source tool that measures the Base liquidation market (Chainlink SVR auctions vs public races).
`Python` `Node.js` `Solidity` `web3.py` `@solana/web3.js` `Kamino SDK` `Jupiter Lend SDK` `systemd` `Telegram Bot API`

### Algorithmic trading platform: "tbot" (private code)
Python platform for crypto (Bybit, Binance and OKX via ccxt) with integrations for Alpaca (US), Interactive Brokers
(London/Europe) and MetaTrader 5 (B3, Brazil). A 24/7 data collector (1-minute candles, funding, open interest,
order book every 10 s) with retention rules and a daily automatic publication of summaries to GitHub; look-ahead-free
backtesting with costs, walk-forward and Monte Carlo; a risk engine that vetoes any order outside limits (size, daily
loss, drawdown, pace) with a kill switch; paper, testnet and live modes (live is locked behind a time-limited,
confirmed release); Telegram commands. About 3,000 lines and 106 automated tests. Runs in paper mode: no real money yet.
`Python` `ccxt` `pandas` `NumPy` `pytest` `Alpaca` `Interactive Brokers` `MetaTrader 5` `Telegram Bot API`

## AI & Machine Learning

| Project | What it does | Stack |
|---|---|---|
| [STRIDE threat analysis with AI](https://github.com/lucasraisi/Desafio-Analise-Stride-Usando-IA-DIO) | API that reads an architecture diagram and produces a STRIDE threat model with generative AI | Python, FastAPI, Azure OpenAI |
| [AI agent that writes unit tests](https://github.com/lucasraisi/construindo_agente_ia) | Takes Python code and generates pytest unit tests automatically | Python, LLM agent, pytest |
| [Image-based recommendation](https://github.com/lucasraisi/Recomendacao_Por_Imagens) | Recommends look-alike products (VGG16 features + cosine similarity, 4 categories) | TensorFlow/Keras, scikit-learn |
| [Face recognition from scratch](https://github.com/lucasraisi/Reconhecimento_Facial_Do_Zero) | Detection (OpenCV DNN) + recognition with MobileNetV2 transfer learning: **82.9% test accuracy** on LFW | TensorFlow, OpenCV |
| [YOLO custom dataset](https://github.com/lucasraisi/Rede_Yolo) | YOLOv4-tiny trained on a filtered dataset (people, bicycles), mAP@0.50 31%, with a data-quality post-mortem | Darknet, CUDA, OpenCV |
| [Voice virtual assistant](https://github.com/lucasraisi/Assistente_Virtual) | Speech-to-text, text-to-speech and voice commands | Python, NLP |
| [Ice-cream sales forecast](https://github.com/lucasraisi/dio-microsoft-previsao-sorvetes) | Regression model predicting sales from temperature | Azure Machine Learning |
| [Transfer learning](https://github.com/lucasraisi/Transfer-Learning-DIO) · [Confusion matrix metrics](https://github.com/lucasraisi/Confusion_Matrix) · [Dimensionality reduction](https://github.com/lucasraisi/Reducao-de-Dimensionalidade-DIO) | Core ML exercises | Python |

## What I can build for you
- Telegram bots that watch wallets, prices or DeFi positions and alert you before something goes wrong.
- On-chain data reports and dashboards (who wins liquidations, protocol volumes, whale wallets).
- Python automations with APIs (exchanges, spreadsheets, Telegram, public data).
- AI integrations: LLM agents and APIs (FastAPI + OpenAI/Azure OpenAI).

## Contact
GitHub: [@lucasraisi](https://github.com/lucasraisi) · LinkedIn: *add link* · E-mail: *add e-mail*

---

## Português
Desenvolvedor Python/Node.js focado em **automação DeFi, dados on-chain e IA aplicada**. Estudante de Análise e Desenvolvimento de
Sistemas (Anhembi Morumbi) e avaliador de modelos de IA desde 2023 (Appen / Outlier.ai). **Projeto principal:** [motor de liquidações e arbitragem DeFi (Base + Solana)](defi-liquidation-engine/README.pt-BR.md),
um sistema 24/7 que monitora ~186 mil posições de empréstimo, simula liquidações com flash loan na rede real e reporta
tudo no Telegram. **Plataforma de trading algorítmico "tbot" (código privado):** cripto (Bybit, Binance, OKX) e
integrações com Alpaca, Interactive Brokers e MetaTrader 5 (B3); coletor de dados 24/7, backtest com walk-forward e Monte
Carlo, motor de risco com kill switch e 106 testes automatizados, em modo papel. **IA/ML:** análise de ameaças STRIDE com FastAPI e Azure OpenAI, agente que gera testes unitários,
recomendação por imagem, reconhecimento facial, YOLO, assistente de voz e previsão de vendas no Azure ML.
**Serviços:** bots de alerta no Telegram, relatórios de dados on-chain, automações em Python e integrações com IA.
