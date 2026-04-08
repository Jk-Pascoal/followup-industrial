# 🏭 Sistema de Follow-up Industrial - Biorrefinaria Enterprise

Dashboard interativo e profissional desenvolvido em Python (Streamlit) para o gerenciamento de follow-up industrial. Focado no planejamento, interação com fornecedores e monitoramento de riscos de ruptura operacional em supply chain.

## 🚀 Funcionalidades

- **Visão Executiva**: Dashboard com métricas críticas (pedidos totais, itens em atraso, alta criticidade e risco de ruptura ininente).
- **Carga de Dados Dinâmica**: Integração simples com dados do ERP via upload de arquivos `.csv` ou `.xlsx`. Possui base de demonstração para testes.
- **Motor de Alertas (Ruptura)**: Cálculo automático de "Risco de Ruptura" baseado em prazos de entrega e na logística de suprimentos.
- **Tabela Interativa e Persistência de Dados**: Tabela com marcação visual de urgências e possibilidade de inserir e consultar histórico de interações com fornecedores diretamente pela interface.
- **Exportação de Dados**: Geração on-the-fly e download de relatórios Excel contemplando apenas os itens críticos e em atraso.
- **Assistente de Cobrança Inteligente**: Formulador semi-automático de textos e e-mails para cobrança e acompanhamento de parceiros e fornecedores, aproveitando contexto do atraso e anotações informadas.

## 🛠️ Tecnologias Utilizadas

- **[Python](https://www.python.org/)**
- **[Streamlit](https://streamlit.io/)**: Construção da interface do usuário e dashboard.
- **[Pandas](https://pandas.pydata.org/)**: Motor de análise e tratamento dos dados.
- **Biliotecas de Excel** (`openpyxl`, `xlsxwriter`): Leitura e exportação de relatórios.

## 📦 Como Instalar e Rodar Localmente

1. Clone o repositório:
   ```bash
   git clone https://github.com/SEU_USUARIO/followup-industrial.git
   cd followup-industrial
   ```

2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

3. Execute a aplicação na sua máquina:
   ```bash
   streamlit run app.py
   ```

## 📄 Estrutura do Projeto

- `app.py`: O núcleo da aplicação Streamlit (Front-end e Back-end).
- `requirements.txt`: Lista de pacotes necessários.
- `base_pedidos.csv`: Arquivo de demonstração usado se nenhum dado for inserido.

## 👨‍💻 Autor

**@jkpascoalds**
© 2026 Sistema de Follow-up Industrial | Versão Enterprise
