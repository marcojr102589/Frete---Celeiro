import streamlit as st
import pandas as pd
import googlemaps
import os

# Configuração da API do Google Maps (substitua pela sua chave real)
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY") or "SUA_CHAVE_AQUI"
gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)

# Dados simulados de transportadoras
transportadoras = [
    {"nome": "TransSoja", "custo_por_km": 4.20, "custo_por_ton": 210},
    {"nome": "AgroFretes", "custo_por_km": 3.90, "custo_por_ton": 200},
    {"nome": "ViaRural", "custo_por_km": 4.50, "custo_por_ton": 215},
    {"nome": "CoopLog", "custo_por_km": 4.00, "custo_por_ton": 205},
]

# Função para calcular distância usando Google Maps
def calcular_distancia_google_maps(origem, destino):
    try:
        result = gmaps.distance_matrix(origem, destino, mode='driving', region='br')
        distancia_metros = result['rows'][0]['elements'][0]['distance']['value']
        return distancia_metros / 1000  # converter para km
    except Exception as e:
        st.error(f"Erro ao calcular distância: {e}")
        return None

# Cálculo dos custos
def calcular_custos(origem, destino, peso_ton):
    distancia = calcular_distancia_google_maps(origem, destino)
    if not distancia:
        return []
    resultados = []

    for t in transportadoras:
        custo_km = t["custo_por_km"] * distancia
        custo_ton = t["custo_por_ton"] * peso_ton
        total = custo_km + custo_ton

        resultados.append({
            "Transportadora": t["nome"],
            "Distância (km)": round(distancia, 2),
            "Custo por km (R$/km)": t["custo_por_km"],
            "Custo por ton (R$/ton)": t["custo_por_ton"],
            "Custo Total Estimado (R$)": round(total, 2)
        })

    return sorted(resultados, key=lambda x: x["Custo Total Estimado (R$)"])

# Streamlit app
st.set_page_config(page_title="Cotador de Frete - Celeiro Sementes", layout="centered")
st.title("🚛 Cotador de Frete - Celeiro Sementes")

st.markdown("Informe abaixo os dados da rota de transporte de sementes em Big Bag:")

col1, col2 = st.columns(2)
with col1:
    origem = st.text_input("Origem", value="Luziânia, GO")
with col2:
    destino = st.text_input("Destino", value="Rio Verde, GO")

peso = st.number_input("Peso total transportado (em toneladas)", min_value=1.0, value=10.0, step=1.0)

if st.button("Calcular Frete"):
    resultados = calcular_custos(origem, destino, peso)
    if resultados:
        st.success(f"Melhor opção: {resultados[0]['Transportadora']} por R$ {resultados[0]['Custo Total Estimado (R$)']:.2f}")
        st.markdown("### Detalhamento das Transportadoras")
        st.dataframe(pd.DataFrame(resultados))
    else:
        st.warning("Não foi possível calcular a rota. Verifique os endereços informados e a chave da API.")
