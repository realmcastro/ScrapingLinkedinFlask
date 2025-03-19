# LinkedIn Job Scraper with Python || 2.0

Uma aplicação web simples para buscar vagas no LinkedIn com filtros avançados, integração de exportação em CSV/JSON e interface gráfica construída com Flask. Ideal para quem busca vagas de forma eficiente e personalizada.

## 🚀 Funcionalidades

- 🔍 **Busca Avançada**: Use operadores booleanos (AND/OR) para combinações de palavras-chave.
- 🗂️ **Filtros de Vagas**: Filtre por tipo de emprego (tempo integral, contrato, etc.).
- 📍 **Filtro de Localização**: Escolha entre presencial, remoto ou híbrido.
- 📅 **Filtro de Data**: Filtre vagas por intervalo de tempo (últimas 24h, 7 dias, 30 dias).
- ⚡ **Exportação de Dados**: Exporte os resultados para **CSV** ou **JSON**.
- 🌐 **Interface Intuitiva**: Interface gráfica para busca e visualização de vagas.
- 📊 **Log e Status**: Acompanhe o progresso da busca em tempo real.

## 🛠️ Tecnologias

- Python
- Flask
- Requests
- HTML/CSS com Bootstrap

## 📦 Instalação

1. Clone o repositório:
```
git clone git@github.com:realmcastro/ScrapingLinkedinFlask.git
cd ScrapingLinkedinFlask
```
Instale as dependências:
```
pip install -r requirements.txt
```
Inicie o servidor Flask:
```
python app.py
```

Acesse a aplicação no navegador:
```
http://127.0.0.1:5000
```
🔧 Como Usar

🖥️ Interface Gráfica

- Filtros disponíveis:<br>
- Palavras-chave (ex.: React AND (Jr OR Junior)).<br>
- Localização (ex.: "Brazil").<br>
- Data máxima (ex.: "31/12/2023").<br>

Tipo de emprego:

- Tempo integral (F), Meio período (P), Contrato (C), Temporário (T).
- Local de trabalho: Presencial, Remoto.
- Distância e limite de vagas.

Exportação:
- Após realizar a busca, você pode exportar os resultados em CSV ou JSON.

📜 Exportação

CSV: Exporta os resultados em uma planilha para análises offline.<br>
JSON: Ideal para integração com outras aplicações ou APIs.

📁 Estrutura do Projeto
linkedin-job-scraper/
├── scraper.py        # Lógica principal do scraper<br>
├── app.py            # Arquivo principal do servidor Flask<br>
├── templates/        # Arquivos HTML para renderização<br>
│   ├── index.html    # Página inicial com filtros e busca<br>
│   ├── results.html  # Página de resultados<br>
├── static/           # Arquivos CSS/JS<br>
├── requirements.txt  # Dependências do projeto<br>
└── README.md         # Documentação do projeto

⚠️ Notas Importantes
- Limitações: O LinkedIn pode bloquear o acesso ao scraper após diversas requisições em curto período. Use com moderação.
- Compatibilidade: Testado com Python 3.x.


🖼️ Pré-visualização

- Tela de Busca<br>
- LinkedIn Job Scraper

🔧 Principais Elementos

- Filtros de Busca: Permite definir palavras-chave, tipo de emprego, localização, data máxima e outros critérios.<br>
- Status e Log: Feedback em tempo real sobre o progresso da busca.<br>
- Exportação: Botões para salvar os resultados em CSV ou JSON.

📝 Licença
Este projeto está sob a licença MIT. Consulte o arquivo LICENSE para mais detalhes.

Preview:
![alt text](image.png)
