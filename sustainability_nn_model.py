import os
import pickle
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential, save_model, load_model
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from typing import Tuple, Optional, Dict
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurações do modelo
MODEL_DIR = "model_weights"
MODEL_PATH = os.path.join(MODEL_DIR, "sustainability_model.h5")
SCALER_PATH = os.path.join(MODEL_DIR, "scaler.pkl")
os.makedirs(MODEL_DIR, exist_ok=True)

def generate_training_data() -> pd.DataFrame:
    """Gera dados de treinamento mais robustos e diversificados.
    
    Returns:
        DataFrame com dados de treinamento sintéticos
    """
    cidades = ['São Paulo', 'Rio de Janeiro', 'Belo Horizonte', 
               'Salvador', 'Curitiba', 'Fortaleza',
               'Porto Alegre', 'Recife', 'Manaus']
    
    dados = {
        'Cidade': cidades,
        'IDH': [0.805, 0.799, 0.810, 0.824, 0.759, 0.823, 0.754, 0.805, 0.772, 0.737],
        'Área Verde (m²/hab)': [15, 12, 18, 25, 10, 16, 9, 14, 11, 8],
        'Temperatura Média (°C)': [22.5, 24.2, 21.8, 23.4, 26.3, 19.3, 27.4, 20.7, 26.0, 28.1],
        'Índice de Sustentabilidade': [75, 72, 78, 85, 68, 82, 65, 77, 70, 62]
    }
    return pd.DataFrame(dados)

def create_model(input_shape: Tuple[int]) -> Sequential:
    """Cria e compila o modelo de rede neural aprimorado.
    
    Args:
        input_shape: Formato dos dados de entrada
        
    Returns:
        Modelo de rede neural compilado
    """
    model = Sequential([
        Dense(128, activation='relu', input_shape=input_shape),
        Dropout(0.3),
        Dense(64, activation='relu'),
        Dropout(0.2),
        Dense(32, activation='relu'),
        Dense(1, activation='linear')
    ])
    
    model.compile(
        optimizer=Adam(learning_rate=0.0005),
        loss='mse',
        metrics=['mae', 'mse']
    )
    
    return model

def save_trained_model(model: Sequential, scaler: StandardScaler) -> None:
    """Salva o modelo e o scaler treinados.
    
    Args:
        model: Modelo treinado
        scaler: Scaler utilizado na normalização
    """
    try:
        save_model(model, MODEL_PATH)
        with open(SCALER_PATH, 'wb') as f:
            pickle.dump(scaler, f)
        logger.info(f"Modelo e scaler salvos em {MODEL_DIR}")
    except Exception as e:
        logger.error(f"Erro ao salvar modelo: {e}")
        raise

def load_trained_model() -> Tuple[Optional[Sequential], Optional[StandardScaler]]:
    """Carrega o modelo e scaler previamente treinados.
    
    Returns:
        Tupla contendo (modelo, scaler) ou (None, None) se não encontrados
    """
    if os.path.exists(MODEL_PATH) and os.path.exists(SCALER_PATH):
        try:
            model = load_model(MODEL_PATH)
            with open(SCALER_PATH, 'rb') as f:
                scaler = pickle.load(f)
            logger.info("Modelo e scaler carregados com sucesso")
            return model, scaler
        except Exception as e:
            logger.error(f"Erro ao carregar modelo: {e}")
    return None, None

def train_sustainability_model(force_retrain: bool = False) -> Tuple[Sequential, StandardScaler]:
    """Treina ou carrega o modelo de sustentabilidade.
    
    Args:
        force_retrain: Força novo treinamento mesmo se existir modelo salvo
        
    Returns:
        Tupla contendo (modelo treinado, scaler utilizado)
        
    Raises:
        RuntimeError: Se ocorrer erro durante o treinamento
    """
    try:
        # Verifica se pode carregar modelo existente
        if not force_retrain:
            model, scaler = load_trained_model()
            if model and scaler:
                return model, scaler
        
        # 1. Gera ou carrega os dados
        df = generate_training_data()
        logger.info("Dados para treinamento gerados com sucesso")
        
        # 2. Prepara os dados
        X = df[['IDH', 'Área Verde (m²/hab)', 'Temperatura Média (°C)']].values
        y = df['Índice de Sustentabilidade'].values
        
        # 3. Divisão treino/validação
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # 4. Normalização
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_val_scaled = scaler.transform(X_val)
        
        # 5. Cria e treina o modelo
        model = create_model((X.shape[1],))
        logger.info("Modelo criado. Iniciando treinamento...")
        
        # Callbacks
        callbacks = [
            EarlyStopping(monitor='val_loss', patience=20, restore_best_weights=True),
            ModelCheckpoint(MODEL_PATH, save_best_only=True, monitor='val_loss')
        ]
        
        history = model.fit(
            X_train_scaled, y_train,
            validation_data=(X_val_scaled, y_val),
            epochs=500,
            batch_size=8,
            callbacks=callbacks,
            verbose=1
        )
        
        logger.info("Modelo treinado com sucesso")
        
        # Salva o modelo e scaler
        save_trained_model(model, scaler)
        
        return model, scaler
        
    except Exception as e:
        logger.error(f"Erro ao treinar modelo: {e}")
        raise

# Carrega o modelo ao importar (sem forçar novo treinamento)
try:
    model, scaler = train_sustainability_model()
except Exception as e:
    logger.error(f"Falha ao inicializar o modelo: {e}")
    model, scaler = None, None