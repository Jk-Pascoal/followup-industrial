import streamlit as st
import pandas as pd
import datetime
import io

# Configuração da página
st.set_page_config(page_title="Follow-up Industrial Enterprise", layout="wide", page_icon="🏭")

# --- GERENCIAMENTO DE ESTADO (OBSERVAÇÕES) ---
if 'obs_dict' not in st.session_state:
    st.session_state['obs_dict'] = {}

# --- CABEÇALHO DO DASHBOARD ---
st.markdown("<h1 style='text-align: center; padding-top: 0;'>🏭 Sistema de Follow-up Industrial</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #888888; margin-top: -20px;'>Biorrefinaria - Versão Enterprise</h3>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Planejamento, interações com fornecedores e monitoramento de ruptura operacional.</p>", unsafe_allow_html=True)

# --- UPLOADER E CARGA DE DADOS ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2775/2775994.png", width=100) # Ícone de Caminhão
    st.header("📁 Carga de Dados (ERP)")
    arquivo_upload = st.file_uploader("Formato: CSV ou Excel", type=["csv", "xlsx"])

def processar_dados(df):
    df_copy = df.copy()
    
    # Padronização de Colunas de Data
    if 'Prazo_Acordado' in df_copy.columns:
        df_copy['Prazo_Acordado'] = pd.to_datetime(df_copy['Prazo_Acordado'], errors='coerce').dt.date
    if 'Data_Emissao' in df_copy.columns:
        df_copy['Data_Emissao'] = pd.to_datetime(df_copy['Data_Emissao'], errors='coerce').dt.date
        
    # --- MOTOR DE DATA SCIENCE BÁSICO: ALERTA DE RUPTURA ---
    if 'Prazo_Acordado' in df_copy.columns and 'Status_Followup' in df_copy.columns:
        hoje = datetime.date.today()
        
        def calcular_ruptura(row):
            if pd.isnull(row['Prazo_Acordado']):
                return False
            # Verifica dias faltantes
            dias_restantes = (row['Prazo_Acordado'] - hoje).days
            # Regra: Faltam 2 dias ou menos E não está isolado biologicamente/logísticamente (Em Trânsito)
            if dias_restantes <= 2 and row['Status_Followup'] not in ['Em Trânsito', 'Concluído', 'Recebido']:
                return True
            return False
            
        df_copy['Risco_Ruptura'] = df_copy.apply(calcular_ruptura, axis=1)
    
    # --- INCORPORAR ANOTAÇÕES DE HISTÓRICO ---
    # Usamos o dicionário de estado para persistir as anotações mesmo ao filtrar
    if 'Pedido' in df_copy.columns:
        df_copy['Anotação_Interação'] = df_copy['Pedido'].map(lambda x: st.session_state['obs_dict'].get(str(x), ""))
        
    return df_copy

df = None
if arquivo_upload is not None:
    try:
        if arquivo_upload.name.endswith('.csv'):
            df_bruto = pd.read_csv(arquivo_upload)
        else:
            df_bruto = pd.read_excel(arquivo_upload)
        df = processar_dados(df_bruto)
        st.sidebar.success("✅ Arquivo carregado com sucesso!")
    except Exception as e:
        st.sidebar.error(f"Erro ao ler arquivo: {e}")
else:
    try:
        df_bruto = pd.read_csv("base_pedidos.csv")
        df = processar_dados(df_bruto)
        st.sidebar.info("👀 Exibindo dados da Demonstração.")
    except FileNotFoundError:
        df = None

if df is None:
    st.info("👈 Por favor, utilize o menu lateral para inserir a planilha do seu ERP (.csv ou .xlsx).")
    st.stop()


# --- FILTROS DE PESQUISA ---
with st.sidebar:
    st.markdown("---")
    st.header("🔍 Filtros")
    fornecedores = st.multiselect("Filtrar Fornecedor", options=df["Fornecedor"].dropna().unique() if "Fornecedor" in df.columns else [])
    status = st.multiselect("Filtrar Status", options=df["Status_Followup"].dropna().unique() if "Status_Followup" in df.columns else [])
    somente_rupturas = st.checkbox("🚨 Apenas Risco de Ruptura")

# Aplicação de Filtros
df_filtrado = df.copy()

if fornecedores and "Fornecedor" in df_filtrado.columns:
    df_filtrado = df_filtrado[df_filtrado["Fornecedor"].isin(fornecedores)]
if status and "Status_Followup" in df_filtrado.columns:
    df_filtrado = df_filtrado[df_filtrado["Status_Followup"].isin(status)]
if somente_rupturas and "Risco_Ruptura" in df_filtrado.columns:
    df_filtrado = df_filtrado[df_filtrado["Risco_Ruptura"] == True]

# --- BLOCO PRINCIPAL (DASHBOARD) ---
with st.container():
    st.markdown("### 📊 Visão Executiva")
    col1, col2, col3, col4 = st.columns(4)

    total_pedidos = len(df_filtrado)
    qtd_atrasados = len(df_filtrado[df_filtrado["Status_Followup"] == "Atrasado"]) if "Status_Followup" in df_filtrado.columns else 0
    itens_criticos = len(df_filtrado[df_filtrado["Criticidade"].isin(["Crítica", "Alta"])]) if "Criticidade" in df_filtrado.columns else 0
    rupturas_alerta = len(df_filtrado[df_filtrado["Risco_Ruptura"] == True]) if "Risco_Ruptura" in df_filtrado.columns else 0

    with col1:
        st.metric("📦 Total de Pedidos", total_pedidos)
    with col2:
        st.metric("⏳ Atrasados", qtd_atrasados, delta=f"{qtd_atrasados} ofensor(es)" if qtd_atrasados > 0 else "OK", delta_color="inverse")
    with col3:
        st.metric("🔥 Alta Criticidade", itens_criticos)
    with col4:
        st.metric("🚨 Risco de Ruptura", rupturas_alerta, delta="CRÍTICO" if rupturas_alerta > 0 else "Normal", delta_color="inverse")


st.markdown("---")


# --- TABELA INTERATIVA COM EDITOR ---
with st.container():
    col_tb, col_exp = st.columns([0.8, 0.2])
    with col_tb:
        st.subheader("📝 Tabela Dinâmica e Histórico de Follow-up")
        st.markdown("Células da coluna **Anotação_Interação** podem ser editadas diretamente abaixo.")
    
    with col_exp:
        # GERAR RELATÓRIO EXCEL IN-MEMORY
        if not df_filtrado.empty:
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                # Vamos exportar os atrasados e com risco de ruptura
                df_export = df_filtrado[(df_filtrado.get("Status_Followup") == "Atrasado") | (df_filtrado.get("Risco_Ruptura") == True)]
                if df_export.empty:
                    df_export = df_filtrado # fallback se não tiver nada crítico, exporta o visível
                df_export.to_excel(writer, index=False, sheet_name='Criticos_e_Atrasos')
            
            xldados = output.getvalue()
            
            st.download_button(
                label="📥 Baixar Relatório Críticos (Excel)",
                data=xldados,
                file_name="Followup_Criticos.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    # Configuração de Colunas Especiais Visuais
    def highlight_rows(row):
        try:
            if row.get('Risco_Ruptura') == True:
                return ['background-color: rgba(255, 0, 0, 0.25); color: white; font-weight: bold'] * len(row)
            elif row.get('Status_Followup') == 'Atrasado':
                return ['background-color: rgba(255, 100, 100, 0.1); color: #ff4b4b'] * len(row)
            return [''] * len(row)
        except:
            return [''] * len(row)

    # st.data_editor detecta edições feitas pelo usuário
    if "Pedido" in df_filtrado.columns:
        df_display = df_filtrado.copy()
        
        # Mapeando colunas para o editor de forma amigável
        col_config = {
            "Anotação_Interação": st.column_config.TextColumn(
                "💬 Anotação Interação",
                help="Clique duas vezes na célula para digitar um comentário.",
                required=False
            ),
            "Risco_Ruptura": st.column_config.CheckboxColumn("🚨 Ruptura?", disabled=True)
        }
        
        # Criamos o editor desabilitando as colunas que não devem ser alteradas (tudo menos Anotação)
        disabled_cols = [c for c in df_display.columns if c != "Anotação_Interação"]
        
        edited_df = st.data_editor(
            df_display.style.apply(highlight_rows, axis=1),
            use_container_width=True,
            hide_index=True,
            column_config=col_config,
            disabled=disabled_cols,
            key="dados_edicao"
        )
        
        # Lógica para salvar as anotações alteradas de volta no Session State
        # O Streamlit reconduz a execução sempre que uma célula é alterada.
        if "dados_edicao" in st.session_state and "edited_rows" in st.session_state["dados_edicao"]:
            alteracoes = st.session_state["dados_edicao"]["edited_rows"]
            for idx, cols_mudados in alteracoes.items():
                if "Anotação_Interação" in cols_mudados:
                    mudanca_texto = cols_mudados["Anotação_Interação"]
                    pedido_alterado = df_display.iloc[idx]["Pedido"]
                    st.session_state['obs_dict'][str(pedido_alterado)] = mudanca_texto
    else:
        st.dataframe(df_filtrado, use_container_width=True, hide_index=True)


st.markdown("---")

# --- ASSISTENTE DE COBRANÇA ---
st.subheader("✉️ Assistente de Cobrança Inteligente")

with st.container():
    if total_pedidos > 0 and "Pedido" in df_filtrado.columns:
        pedido_selecionado = st.selectbox("Selecione o Número do Pedido:", options=df_filtrado["Pedido"].tolist())
        
        info = df_filtrado[df_filtrado["Pedido"] == pedido_selecionado].iloc[0]
        
        fornecedor_nome = info.get('Fornecedor', '[Fornecedor]')
        material_nome = info.get('Material', '[Material]')
        status_atual = info.get('Status_Followup', 'N/A')
        criticidade_ped = info.get('Criticidade', 'Normal')
        ruptura_alerta = info.get('Risco_Ruptura', False)
        
        try:
            if pd.notna(info.get('Prazo_Acordado')):
                prazo_formatado = info['Prazo_Acordado'].strftime('%d/%m/%Y')
            else:
                prazo_formatado = "[Indefinido]"
        except:
            prazo_formatado = str(info.get('Prazo_Acordado', '[Indefinido]'))
        
        anotacao = st.session_state['obs_dict'].get(str(pedido_selecionado), "")
        
        # Gerador
        if status_atual == 'Atrasado' or ruptura_alerta:
            msg = f"URGENTE: Olá equipe da {fornecedor_nome}.\n\nReferente ao Pedido {pedido_selecionado} ({material_nome}). O prazo de {prazo_formatado} cruzou nossa margem de segurança operacional.\n"
            if anotacao:
                msg += f"Observação anterior nossa: '{anotacao}'.\n"
            msg += f"Peço um status atualizado de carregamento AGORA para evitarmos impacto na Biorrefinaria.\n\nObrigado."
        else:
            msg = f"Olá equipe da {fornecedor_nome}.\n\nAcompanhamento do Pedido {pedido_selecionado} ({material_nome}). Prazo programado: {prazo_formatado}. Status consta como: '{status_atual}'. "
            if anotacao:
                msg += f"Alinhamentos: {anotacao}. "
            msg += "\nPodem nos dar um 'ok' de que segue o ritmo?\n\nObrigado!"
        
        st.text_area("Mensagem pronta para enviar:", value=msg, height=180)
    else:
        st.warning("Nenhum pedido atende aos filtros para cobrança.")

# --- RODAPÉ ---
st.markdown("<br><hr><div style='text-align: center; color: #888888; font-size: 14px;'>© 2026 @jkpascoalds - Sistema de Follow-up Industrial | Versão Enterprise</div>", unsafe_allow_html=True)
