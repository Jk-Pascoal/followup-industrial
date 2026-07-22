# Follow-up Industrial

Dashboard em **Streamlit** para acompanhamento operacional de pedidos industriais, atrasos, criticidade, interações com fornecedores e risco de ruptura.

O projeto traduz uma rotina comum de suprimentos em uma aplicação analítica simples: recebe uma base exportada do ERP, aplica regras de negócio, oferece filtros e prioriza os pedidos que exigem ação.

---

## Problema de negócio

Equipes de suprimentos frequentemente acompanham centenas de pedidos em planilhas dispersas. Sem uma visão consolidada, atrasos e itens críticos podem ser percebidos tarde demais.

A aplicação centraliza perguntas operacionais como:

- Quantos pedidos estão atrasados?
- Quais itens possuem criticidade alta ou crítica?
- Quais entregas estão próximas do prazo sem conclusão?
- Qual fornecedor ou status concentra os maiores riscos?
- Quais pedidos devem entrar primeiro no relatório de cobrança?

---

## Funcionalidades implementadas

- upload de arquivos `.csv` e `.xlsx`;
- base demonstrativa carregada automaticamente;
- conversão e tratamento das datas de emissão e prazo;
- filtros por fornecedor e status;
- filtro exclusivo para risco de ruptura;
- indicadores de pedidos, atrasos, criticidade e ruptura;
- tabela editável para registrar interações;
- exportação em Excel dos pedidos atrasados ou em risco;
- geração assistida de texto para acompanhamento de fornecedores.

---

## Regra de risco de ruptura

O alerta atual é **determinístico e interpretável**. Um pedido é marcado como risco quando:

1. faltam dois dias ou menos para o prazo acordado; e
2. o status não está entre `Em Trânsito`, `Concluído` ou `Recebido`.

```text
Risco de ruptura =
    prazo restante <= 2 dias
    E status ainda não indica trânsito ou conclusão
```

Essa regra funciona como um mecanismo de priorização operacional. Ela não é apresentada como modelo preditivo de Machine Learning.

---

## Indicadores

| Indicador | Definição |
|---|---|
| Total de pedidos | Quantidade de registros após aplicação dos filtros |
| Atrasados | Pedidos com `Status_Followup = Atrasado` |
| Alta criticidade | Itens classificados como `Alta` ou `Crítica` |
| Risco de ruptura | Pedidos que atendem à regra de prazo e status |

---

## Tecnologias

- Python
- Streamlit
- Pandas
- OpenPyXL
- XlsxWriter

---

## Estrutura

```text
followup-industrial/
├── app.py
├── base_pedidos.csv
├── requirements.txt
└── README.md
```

---

## Como executar

```bash
git clone https://github.com/Jk-Pascoal/followup-industrial.git
cd followup-industrial

python -m venv .venv
```

Ativação no Windows:

```powershell
.venv\Scripts\activate
```

Instalação e execução:

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## Formato esperado dos dados

A aplicação utiliza, quando disponíveis, as seguintes colunas:

| Coluna | Uso |
|---|---|
| `Pedido` | Identificação do pedido e vínculo com anotações |
| `Fornecedor` | Filtro e acompanhamento do parceiro |
| `Data_Emissao` | Data de origem do pedido |
| `Prazo_Acordado` | Cálculo de proximidade do prazo |
| `Status_Followup` | Situação operacional |
| `Criticidade` | Priorização do item |

A base `base_pedidos.csv` permite testar a aplicação sem utilizar informações corporativas.

---

## Limitações atuais

- as anotações ficam no `session_state` e são mantidas somente durante a sessão ativa;
- não há integração direta com ERP ou banco de dados;
- o risco de ruptura é calculado por regra de negócio, sem estimação probabilística;
- autenticação e controle de acesso ainda não foram implementados.

Essas limitações delimitam o estágio atual do protótipo e orientam sua evolução.

---

## Próximas evoluções

- persistência em SQLite ou PostgreSQL;
- histórico temporal das interações com fornecedores;
- SLA por categoria e fornecedor;
- score probabilístico de atraso;
- autenticação e perfis de acesso;
- testes automatizados para as regras de negócio.

---

## Autor

**Jakson Pascoal** — [GitHub](https://github.com/Jk-Pascoal)
