"""
GENERADOR DE DATASETS REALISTAS PARA ENTRENAMIENTO SQL/ANALYTICS
================================================================

Características clave:
- Distribuciones realistas (no uniformes)
- Outliers intencionales
- Relaciones FK consistentes
- Complejidad temporal y de segmentación
- Métricas de negocio calculables

Modularizado para poder importarse desde un proyecto principal:
    from generate_sales_data import generate_customers, generate_products, \
        generate_orders, generate_order_items, main
"""

import os
import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd


# ============================================================================
# CONFIGURACIÓN POR DEFECTO
# ============================================================================

DEFAULT_SEED = 42
DEFAULT_NUM_CUSTOMERS = 10000
DEFAULT_NUM_PRODUCTS = 500
DEFAULT_NUM_ORDERS = 200000
DEFAULT_START_DATE = datetime(2020, 1, 1)
DEFAULT_END_DATE = datetime(2024, 12, 31)
DEFAULT_OUTPUT_DIR = "datasets"


def set_seed(seed=DEFAULT_SEED):
    """Fija la semilla de numpy y random para reproducibilidad."""
    np.random.seed(seed)
    random.seed(seed)


# ============================================================================
# MODELO DE CRECIMIENTO DINÁMICO (para signups y, si se quiere, otras series)
# ============================================================================

def _logistic_trend(t, days_range, steepness=6.0, midpoint_frac=0.55):
    """
    Curva-S (crecimiento logístico) en vez de exponencial puro.
    Un negocio real no crece exponencialmente para siempre: arranca lento,
    acelera, y luego se satura. steepness controla qué tan brusca es la
    aceleración; midpoint_frac controla en qué punto del rango temporal
    ocurre el punto de inflexión.
    """
    midpoint = days_range * midpoint_frac
    k = steepness / days_range
    return 1.0 / (1.0 + np.exp(-k * (t - midpoint)))


def _seasonal_wave(t, period, amplitude, phase=0):
    """Componente sinusoidal simple (estacionalidad anual, semanal, etc.)."""
    return amplitude * np.sin(2 * np.pi * (t + phase) / period)


def _campaign_spikes(days_range, num_campaigns=10, amplitude=1.4, decay_days=12):
    """
    Simula ráfagas de campañas de marketing: en días aleatorios, un pico
    de señal que decae exponencialmente en los días siguientes. Rompe
    cualquier patrón suave y predecible.
    """
    spikes = np.zeros(days_range)
    campaign_days = np.random.choice(days_range, size=min(num_campaigns, days_range), replace=False)
    for day in campaign_days:
        for offset in range(decay_days):
            idx = day + offset
            if idx >= days_range:
                break
            spikes[idx] += amplitude * np.exp(-offset / (decay_days / 3))
    return spikes


def generate_growth_weights(days_range,
                             steepness=6.0,
                             midpoint_frac=0.55,
                             yearly_amplitude=0.25,
                             weekly_amplitude=0.10,
                             num_campaigns=10,
                             noise_sigma=0.15):
    """
    Combina varias señales en un solo vector de pesos por día:
    - Tendencia logística (crecimiento realista con saturación)
    - Estacionalidad anual (temporadas altas/bajas, ej. fin de año)
    - Estacionalidad semanal (días con más/menos actividad)
    - Picos de campañas de marketing en fechas aleatorias
    - Ruido multiplicativo log-normal (evita que se vea "de manual")

    Es intencionalmente simple (todo son funciones cerradas, sin estado),
    pero al combinarse ya no genera una curva monótona y predecible.
    """
    t = np.arange(days_range)

    trend = _logistic_trend(t, days_range, steepness, midpoint_frac)
    yearly = _seasonal_wave(t, period=365, amplitude=yearly_amplitude)
    weekly = _seasonal_wave(t, period=7, amplitude=weekly_amplitude, phase=2)
    spikes = _campaign_spikes(days_range, num_campaigns=num_campaigns)
    noise = np.random.lognormal(mean=0.0, sigma=noise_sigma, size=days_range)

    raw_weights = trend * (1 + yearly + weekly + spikes) * noise
    raw_weights = np.clip(raw_weights, a_min=1e-6, a_max=None)  # evitar pesos negativos/cero

    return raw_weights / raw_weights.sum()


# ============================================================================
# 1. CUSTOMERS
# ============================================================================

def generate_customers(num_customers=DEFAULT_NUM_CUSTOMERS,
                        start_date=DEFAULT_START_DATE,
                        end_date=DEFAULT_END_DATE):
    """
    Genera el DataFrame de clientes con:
    - Fechas de signup con un modelo de crecimiento dinámico (curva-S +
      estacionalidad + campañas + ruido), no un exponencial puro
    - Países con distribución concentrada en top 3
    - Segmentación en pirámide (low/medium/high)
    - Canales de adquisición
    - Churn dependiente del segmento
    """
    days_range = (end_date - start_date).days

    weights = generate_growth_weights(days_range)

    signup_days = np.random.choice(days_range, size=num_customers, p=weights)
    signup_dates = [start_date + timedelta(days=int(d)) for d in signup_days]

    # Países con distribución realista (concentración en top 3)
    countries = ['USA', 'UK', 'Canada', 'Germany', 'France', 'Spain',
                 'Australia', 'Mexico', 'Brazil', 'Japan']
    country_weights = [0.35, 0.20, 0.15, 0.08, 0.07, 0.05, 0.04, 0.03, 0.02, 0.01]
    customer_countries = random.choices(countries, weights=country_weights, k=num_customers)

    # Segmentación realista: pirámide (muchos low, pocos high)
    segment_choices = ['low', 'medium', 'high']
    segment_weights = [0.60, 0.30, 0.10]
    customer_segments = random.choices(segment_choices, weights=segment_weights, k=num_customers)

    # Canales de adquisición
    channels = ['organic', 'ads', 'referral', 'email', 'social']
    channel_weights = [0.35, 0.30, 0.20, 0.10, 0.05]
    acquisition_channels = random.choices(channels, weights=channel_weights, k=num_customers)

    # Churn realista: más probable en low segment
    churn_thresholds = {'low': 0.25, 'medium': 0.12, 'high': 0.05}
    is_active = [random.random() > churn_thresholds[seg] for seg in customer_segments]

    customers_df = pd.DataFrame({
        'customer_id': range(1, num_customers + 1),
        'signup_date': signup_dates,
        'country': customer_countries,
        'customer_segment': customer_segments,
        'acquisition_channel': acquisition_channels,
        'is_active': is_active
    })

    return customers_df


# ============================================================================
# 2. PRODUCTS
# ============================================================================

def generate_products(num_products=DEFAULT_NUM_PRODUCTS):
    """
    Genera el DataFrame de productos con:
    - Categorías con distribución realista
    - Precios log-normales (típico en retail)
    - Costos como % variable del precio (margen 30-60%)
    """
    categories = ['Electronics', 'Clothing', 'Home & Garden', 'Sports',
                  'Books', 'Toys', 'Beauty', 'Food']
    category_weights = [0.25, 0.20, 0.15, 0.12, 0.10, 0.08, 0.06, 0.04]
    product_categories = random.choices(categories, weights=category_weights, k=num_products)

    # Precios con distribución log-normal
    prices = np.random.lognormal(mean=3.5, sigma=0.8, size=num_products)
    prices = np.clip(prices, 5, 500)

    # Costos: margen variable realista
    margin_pcts = np.random.uniform(0.30, 0.60, num_products)
    costs = prices * (1 - margin_pcts)

    products_df = pd.DataFrame({
        'product_id': range(1, num_products + 1),
        'category': product_categories,
        'price': np.round(prices, 2),
        'cost': np.round(costs, 2)
    })

    return products_df


# ============================================================================
# 3. ORDERS
# ============================================================================

def _assign_order_customers(customers_df, num_orders, active_ratio=0.90):
    """Asigna clientes a órdenes: 90% activos, 10% inactivos (power law simple)."""
    active_customers = customers_df.loc[customers_df['is_active'], 'customer_id'].tolist()
    inactive_customers = customers_df.loc[~customers_df['is_active'], 'customer_id'].tolist()

    num_orders_active = int(num_orders * active_ratio)
    num_orders_inactive = num_orders - num_orders_active

    order_customers = (
        random.choices(active_customers, k=num_orders_active) +
        random.choices(inactive_customers, k=num_orders_inactive)
    )
    random.shuffle(order_customers)
    return order_customers


def _assign_order_dates(order_customers, customers_df, end_date):
    """Genera fechas de orden posteriores al signup, con densidad exponencial reciente."""
    # Indexar signup_date por customer_id una sola vez (evita O(n^2))
    signup_lookup = customers_df.set_index('customer_id')['signup_date']

    order_dates = []
    for cust_id in order_customers:
        signup = signup_lookup.loc[cust_id]
        days_since_signup = (end_date - signup).days

        if days_since_signup > 0:
            days_offset = int(np.random.exponential(days_since_signup / 3))
            days_offset = min(days_offset, days_since_signup)
            order_date = signup + timedelta(days=days_offset)
        else:
            order_date = signup

        order_dates.append(order_date)

    return order_dates


def _generate_order_amounts(num_orders, outlier_pct=0.02):
    """Montos con distribución log-normal + outliers intencionales (2% por defecto)."""
    base_amounts = np.random.lognormal(mean=4.0, sigma=0.7, size=num_orders)
    base_amounts = np.clip(base_amounts, 10, 300)

    num_outliers = int(num_orders * outlier_pct)
    outlier_indices = np.random.choice(num_orders, size=num_outliers, replace=False)
    base_amounts[outlier_indices] = np.random.uniform(500, 5000, size=num_outliers)

    return np.round(base_amounts, 2)


def generate_orders(customers_df,
                     num_orders=DEFAULT_NUM_ORDERS,
                     end_date=DEFAULT_END_DATE):
    """
    Genera el DataFrame de órdenes con:
    - Asignación de clientes ponderada por actividad
    - Fechas posteriores al signup con densidad reciente
    - Montos realistas con outliers
    - Métodos de pago y status con distribución de negocio típica
    """
    order_customers = _assign_order_customers(customers_df, num_orders)
    order_dates = _assign_order_dates(order_customers, customers_df, end_date)
    order_amounts = _generate_order_amounts(num_orders)

    payment_methods = ['credit_card', 'debit_card', 'paypal', 'bank_transfer', 'crypto']
    payment_weights = [0.50, 0.25, 0.15, 0.08, 0.02]
    order_payments = random.choices(payment_methods, weights=payment_weights, k=num_orders)

    status_choices = ['completed', 'canceled', 'refunded']
    status_weights = [0.88, 0.08, 0.04]
    order_statuses = random.choices(status_choices, weights=status_weights, k=num_orders)

    orders_df = pd.DataFrame({
        'order_id': range(1, num_orders + 1),
        'customer_id': order_customers,
        'order_date': order_dates,
        'order_amount': order_amounts,
        'payment_method': order_payments,
        'order_status': order_statuses
    })

    # Ordenar por fecha para realismo y reasignar IDs secuenciales
    orders_df = orders_df.sort_values('order_date').reset_index(drop=True)
    orders_df['order_id'] = range(1, num_orders + 1)

    return orders_df


# ============================================================================
# 4. ORDER ITEMS
# ============================================================================

def generate_order_items(orders_df, num_products=DEFAULT_NUM_PRODUCTS):
    """
    Genera el DataFrame de items por orden:
    - Número de items por orden (mayoría 1-3, cola larga hasta 10)
    - Productos únicos por orden
    - Cantidad por item (mayoría 1)
    """
    num_items_choices = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    num_items_weights = [0.40, 0.25, 0.15, 0.08, 0.05, 0.03, 0.02, 0.01, 0.005, 0.005]

    quantity_choices = [1, 2, 3, 4, 5]
    quantity_weights = [0.70, 0.15, 0.08, 0.05, 0.02]

    order_items = []

    for order_id in orders_df['order_id']:
        num_items = np.random.choice(num_items_choices, p=num_items_weights)
        order_products = random.sample(range(1, num_products + 1), min(num_items, num_products))

        for product_id in order_products:
            quantity = np.random.choice(quantity_choices, p=quantity_weights)
            order_items.append({
                'order_id': order_id,
                'product_id': product_id,
                'quantity': quantity
            })

    return pd.DataFrame(order_items)


# ============================================================================
# PERSISTENCIA
# ============================================================================

def save_datasets(datasets: dict, output_dir=DEFAULT_OUTPUT_DIR):
    """
    Guarda cada DataFrame del diccionario como CSV en output_dir.
    datasets: {'customers': df, 'products': df, 'orders': df, 'order_items': df}
    """
    os.makedirs(output_dir, exist_ok=True)
    for name, df in datasets.items():
        path = os.path.join(output_dir, f"{name}.csv")
        df.to_csv(path, index=False)
        print(f"✓ {len(df):,} registros -> {path}")


# ============================================================================
# RESUMEN Y VALIDACIÓN
# ============================================================================

def print_summary(customers_df, products_df, orders_df, order_items_df):
    """Imprime estadísticas de validación y métricas de negocio clave."""
    print("\n" + "=" * 70)
    print("DATASETS GENERADOS EXITOSAMENTE")
    print("=" * 70)

    print("\nESTADÍSTICAS:")
    print(f"  • customers      : {len(customers_df):,} registros")
    print(f"  • products       : {len(products_df):,} registros")
    print(f"  • orders         : {len(orders_df):,} registros")
    print(f"  • order_items    : {len(order_items_df):,} registros")

    print("\nVALIDACIONES:")
    print(f"  • Rango de fechas     : {customers_df['signup_date'].min()} - {orders_df['order_date'].max()}")
    print(f"  • Clientes activos    : {customers_df['is_active'].sum():,} "
          f"({customers_df['is_active'].mean() * 100:.1f}%)")
    completed_mask = orders_df['order_status'] == 'completed'
    print(f"  • Órdenes completed   : {completed_mask.sum():,} ({completed_mask.mean() * 100:.1f}%)")
    print(f"  • Promedio items/orden: {len(order_items_df) / len(orders_df):.2f}")

    print("\nMÉTRICAS DE NEGOCIO DISPONIBLES:")
    completed_orders = orders_df[completed_mask]
    print(f"  • Revenue total  : ${completed_orders['order_amount'].sum():,.2f}")
    print(f"  • AOV (completed): ${completed_orders['order_amount'].mean():,.2f}")
    top_country = customers_df['country'].value_counts()
    print(f"  • Top país       : {top_country.index[0]} ({top_country.iloc[0]:,} customers)")


# ============================================================================
# ORQUESTADOR PRINCIPAL
# ============================================================================

def generate_data(output_dir=DEFAULT_OUTPUT_DIR,
         num_customers=DEFAULT_NUM_CUSTOMERS,
         num_products=DEFAULT_NUM_PRODUCTS,
         num_orders=DEFAULT_NUM_ORDERS,
         start_date=DEFAULT_START_DATE,
         end_date=DEFAULT_END_DATE,
         seed=DEFAULT_SEED):
    """
    Genera y guarda los 4 datasets (customers, products, orders, order_items).
    Punto de entrada para usar desde otro script:

        import generate_sales_data as gsd
        gsd.main(output_dir="mi_carpeta", num_customers=50_000)
    """
    set_seed(seed)
    print("Generando datasets realistas...")

    print("\n[1/4] Generando customers...")
    customers_df = generate_customers(num_customers, start_date, end_date)

    print("[2/4] Generando products...")
    products_df = generate_products(num_products)

    print("[3/4] Generando orders...")
    orders_df = generate_orders(customers_df, num_orders, end_date)

    print("[4/4] Generando order_items...")
    order_items_df = generate_order_items(orders_df, num_products)

    save_datasets({
        'customers': customers_df,
        'products': products_df,
        'orders': orders_df,
        'order_items': order_items_df
    }, output_dir=output_dir)

    print_summary(customers_df, products_df, orders_df, order_items_df)
    print(f"\nTodos los archivos guardados en ./{output_dir}/")
    print("READY FOR SQL ANALYTICS!")

    return {
        'customers': customers_df,
        'products': products_df,
        'orders': orders_df,
        'order_items': order_items_df
    }

def main():
    generate_data()


if __name__ == "__main__":
    main()