"""
GENERADOR DE DATASETS REALISTAS PARA ENTRENAMIENTO SQL/ANALYTICS
================================================================

Características clave:
- Distribuciones realistas (no uniformes)
- Outliers intencionales
- Relaciones FK consistentes
- Complejidad temporal y de segmentación
- Métricas de negocio calculables
"""
# Librerías necesarias
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

# Seed para reproducibilidad
np.random.seed(42)
random.seed(42)

# Crear carpeta de salida
os.makedirs('datasets', exist_ok=True)

print("Generando datasets realistas...")

# ============================================================================
# CUSTOMERS.CSV
# ============================================================================
print("\n[1/4] Generando customers.csv...")

NUM_CUSTOMERS = 5000

# Distribución realista de fechas de signup (crecimiento exponencial)
start_date = datetime(2020, 1, 1)
end_date = datetime(2024, 12, 31)
days_range = (end_date - start_date).days

# Pesos exponenciales: más signups recientes
weights = np.exp(np.linspace(0, 3, days_range))
weights = weights / weights.sum()

signup_days = np.random.choice(days_range, size=NUM_CUSTOMERS, p=weights)
signup_dates = [start_date + timedelta(days=int(d)) for d in signup_days]

# Países con distribución realista (concentración en top 3)
countries = ['USA', 'UK', 'Canada', 'Germany', 'France', 'Spain', 'Australia', 'Mexico', 'Brazil', 'Japan']
country_weights = [0.35, 0.20, 0.15, 0.08, 0.07, 0.05, 0.04, 0.03, 0.02, 0.01]
customer_countries = random.choices(countries, weights=country_weights, k=NUM_CUSTOMERS)

# Segmentación realista: pirámide (muchos low, pocos high)
segment_choices = ['low', 'medium', 'high']
segment_weights = [0.60, 0.30, 0.10]
customer_segments = random.choices(segment_choices, weights=segment_weights, k=NUM_CUSTOMERS)

# Canales de adquisición
channels = ['organic', 'ads', 'referral', 'email', 'social']
channel_weights = [0.35, 0.30, 0.20, 0.10, 0.05]
acquisition_channels = random.choices(channels, weights=channel_weights, k=NUM_CUSTOMERS)

# Churn realista: ~15% inactivos, más probable en low segment
is_active = []
for seg in customer_segments:
    if seg == 'low':
        is_active.append(random.random() > 0.25)  # 25% churn
    elif seg == 'medium':
        is_active.append(random.random() > 0.12)  # 12% churn
    else:  # high
        is_active.append(random.random() > 0.05)  # 5% churn

customers_df = pd.DataFrame({
    'customer_id': range(1, NUM_CUSTOMERS + 1),
    'signup_date': signup_dates,
    'country': customer_countries,
    'customer_segment': customer_segments,
    'acquisition_channel': acquisition_channels,
    'is_active': is_active
})

customers_df.to_csv('datasets/customers.csv', index=False)
print(f"✓ {len(customers_df):,} customers generados")

# ============================================================================
# PRODUCTS.CSV
# ============================================================================
print("\n[2/4] Generando products.csv...")

NUM_PRODUCTS = 100

# Categorías con distribución realista
categories = ['Electronics', 'Clothing', 'Home & Garden', 'Sports', 'Books', 'Toys', 'Beauty', 'Food']
category_weights = [0.25, 0.20, 0.15, 0.12, 0.10, 0.08, 0.06, 0.04]
product_categories = random.choices(categories, weights=category_weights, k=NUM_PRODUCTS)

# Precios con distribución log-normal (realista para retail)
prices = np.random.lognormal(mean=3.5, sigma=0.8, size=NUM_PRODUCTS)
prices = np.clip(prices, 5, 500)  # Entre $5 y $500

# Costos: 40-70% del precio (margen variable realista)
margin_pcts = np.random.uniform(0.30, 0.60, NUM_PRODUCTS)
costs = prices * (1 - margin_pcts)

products_df = pd.DataFrame({
    'product_id': range(1, NUM_PRODUCTS + 1),
    'category': product_categories,
    'price': np.round(prices, 2),
    'cost': np.round(costs, 2)
})

products_df.to_csv('datasets/products.csv', index=False)
print(f"✓ {len(products_df):,} productos generados")

# ============================================================================
# ORDERS.CSV
# ============================================================================
print("\n[3/4] Generando orders.csv...")

NUM_ORDERS = 50000

# Distribución de órdenes por cliente: power law (pocos compran mucho)
# Clientes activos tienen más probabilidad de ordenar
active_customers = customers_df[customers_df['is_active']]['customer_id'].tolist()
inactive_customers = customers_df[~customers_df['is_active']]['customer_id'].tolist()

# 90% de órdenes de clientes activos
num_orders_active = int(NUM_ORDERS * 0.90)
num_orders_inactive = NUM_ORDERS - num_orders_active

# Distribución power law: algunos clientes ordenan mucho
order_customers = []

# Activos: repetición con pesos exponenciales
for _ in range(num_orders_active):
    customer = random.choice(active_customers)
    order_customers.append(customer)

# Inactivos: solo 1-2 órdenes históricas
for _ in range(num_orders_inactive):
    customer = random.choice(inactive_customers)
    order_customers.append(customer)

random.shuffle(order_customers)

# Fechas de órdenes: después del signup del cliente, distribución temporal realista
order_dates = []
for cust_id in order_customers:
    signup = customers_df[customers_df['customer_id'] == cust_id]['signup_date'].iloc[0]
    
    # Orden entre signup y hoy, con mayor densidad reciente
    days_since_signup = (end_date - signup).days
    if days_since_signup > 0:
        # Distribución exponencial: más órdenes recientes
        days_offset = int(np.random.exponential(days_since_signup / 3))
        days_offset = min(days_offset, days_since_signup)
        order_date = signup + timedelta(days=days_offset)
    else:
        order_date = signup
    
    order_dates.append(order_date)

# Montos: distribución realista con outliers
# La mayoría de órdenes: $20-$200
# Algunos outliers: hasta $5000
base_amounts = np.random.lognormal(mean=4.0, sigma=0.7, size=NUM_ORDERS)
base_amounts = np.clip(base_amounts, 10, 300)

# Añadir outliers (2% de órdenes grandes)
num_outliers = int(NUM_ORDERS * 0.02)
outlier_indices = np.random.choice(NUM_ORDERS, size=num_outliers, replace=False)
base_amounts[outlier_indices] = np.random.uniform(500, 5000, size=num_outliers)

order_amounts = np.round(base_amounts, 2)

# Payment methods
payment_methods = ['credit_card', 'debit_card', 'paypal', 'bank_transfer', 'crypto']
payment_weights = [0.50, 0.25, 0.15, 0.08, 0.02]
order_payments = random.choices(payment_methods, weights=payment_weights, k=NUM_ORDERS)

# Status: mayormente completed, algunos canceled/refunded
status_choices = ['completed', 'canceled', 'refunded']
status_weights = [0.88, 0.08, 0.04]
order_statuses = random.choices(status_choices, weights=status_weights, k=NUM_ORDERS)

orders_df = pd.DataFrame({
    'order_id': range(1, NUM_ORDERS + 1),
    'customer_id': order_customers,
    'order_date': order_dates,
    'order_amount': order_amounts,
    'payment_method': order_payments,
    'order_status': order_statuses
})

# Ordenar por fecha para realismo
orders_df = orders_df.sort_values('order_date').reset_index(drop=True)
orders_df['order_id'] = range(1, NUM_ORDERS + 1)

orders_df.to_csv('datasets/orders.csv', index=False)
print(f"✓ {len(orders_df):,} órdenes generadas")

# ============================================================================
# ORDER_ITEMS.CSV
# ============================================================================
print("\n[4/4] Generando order_items.csv...")

order_items = []

for order_id in orders_df['order_id']:
    # Número de items por orden: distribución realista
    # La mayoría: 1-3 items, algunos hasta 10
    num_items = np.random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 
                                  p=[0.40, 0.25, 0.15, 0.08, 0.05, 0.03, 0.02, 0.01, 0.005, 0.005])
    
    # Seleccionar productos únicos para esta orden
    order_products = random.sample(range(1, NUM_PRODUCTS + 1), min(num_items, NUM_PRODUCTS))
    
    for product_id in order_products:
        # Cantidad: mayormente 1, a veces más
        quantity = np.random.choice([1, 2, 3, 4, 5], p=[0.70, 0.15, 0.08, 0.05, 0.02])
        
        order_items.append({
            'order_id': order_id,
            'product_id': product_id,
            'quantity': quantity
        })

order_items_df = pd.DataFrame(order_items)
order_items_df.to_csv('datasets/order_items.csv', index=False)
print(f"✓ {len(order_items_df):,} items de orden generados")

# ============================================================================
# RESUMEN Y VALIDACIÓN
# ============================================================================
print("\n" + "="*70)
print("DATASETS GENERADOS EXITOSAMENTE")
print("="*70)

print(f"\nESTADÍSTICAS:")
print(f"  • customers.csv      : {len(customers_df):,} registros")
print(f"  • products.csv       : {len(products_df):,} registros")
print(f"  • orders.csv         : {len(orders_df):,} registros")
print(f"  • order_items.csv    : {len(order_items_df):,} registros")

print(f"\nVALIDACIONES:")
print(f"  • Rango de fechas    : {customers_df['signup_date'].min()} - {orders_df['order_date'].max()}")
print(f"  • Clientes activos   : {customers_df['is_active'].sum():,} ({customers_df['is_active'].mean()*100:.1f}%)")
print(f"  • Órdenes completed  : {(orders_df['order_status']=='completed').sum():,} ({(orders_df['order_status']=='completed').mean()*100:.1f}%)")
print(f"  • Promedio items/orden: {len(order_items_df)/len(orders_df):.2f}")

print(f"\nMÉTRICAS DE NEGOCIO DISPONIBLES:")
print(f"  • Revenue total      : ${orders_df[orders_df['order_status']=='completed']['order_amount'].sum():,.2f}")
print(f"  • AOV (completed)    : ${orders_df[orders_df['order_status']=='completed']['order_amount'].mean():,.2f}")
print(f"  • Top país           : {customers_df['country'].value_counts().index[0]} ({customers_df['country'].value_counts().iloc[0]:,} customers)")

print(f"\nTodos los archivos guardados en ./datasets/")
print("\nREADY FOR SQL ANALYTICS!")