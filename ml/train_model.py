from pathlib import Path
import joblib
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PolynomialFeatures, StandardScaler

DEFAULT_MODEL_PATH = Path(__file__).resolve().parent / "modelo_reposicion.joblib"

# Escenarios operativos basados en el catálogo inicial del inventario:
# [stock_actual, ventas_diarias, dias_entrega]
CATALOG_SCENARIOS = np.array(
    [
        # Garbanzos Seleccionados (2 kg)
        [2.0, 1.5, 5.0],
        [2.0, 0.8, 4.0],
        [2.0, 0.2, 3.0],
        # Semillas de Chía (3.5 kg)
        [3.5, 1.0, 5.0],
        [3.5, 0.5, 7.0],
        [3.5, 0.25, 3.0],
        # Aceite de Coco Neutro (4 unidades)
        [4.0, 1.0, 5.0],
        [4.0, 0.5, 7.0],
        [4.0, 0.3, 4.0],
        # Almendras Nonpareil (4.5 kg)
        [4.5, 1.2, 5.0],
        [4.5, 0.8, 6.0],
        [4.5, 0.3, 3.0],
        # Granola Artesanal con Miel (6 paquetes)
        [6.0, 1.5, 4.0],
        [6.0, 1.0, 5.0],
        [6.0, 0.5, 4.0],
        # Aceite de Oliva Extra Virgen (8 litros)
        [8.0, 2.0, 5.0],
        [8.0, 1.5, 6.0],
        [8.0, 0.6, 4.0],
        # Lentejas Turcas (14 kg)
        [14.0, 3.0, 5.0],
        [14.0, 1.5, 4.0],
        [14.0, 1.0, 5.0],
        # Mix de Semillas (18 paquetes)
        [18.0, 4.0, 5.0],
        [18.0, 1.8, 4.0],
        [18.0, 1.2, 5.0],
        # Avena Arrollada Tradicional (25 kg)
        [25.0, 5.0, 6.0],
        [25.0, 1.5, 4.0],
        [25.0, 2.0, 5.0],
        # Té Verde en Hebras (500 gramos)
        [500.0, 120.0, 5.0],
        [500.0, 80.0, 7.0],
        [500.0, 25.0, 5.0],
        [500.0, 40.0, 4.0],
    ],
    dtype=float,
)


def _label_scenarios(X: np.ndarray, noise: np.ndarray | None = None) -> np.ndarray:
    dias_cobertura = X[:, 0] / X[:, 1]
    ruido = noise if noise is not None else np.zeros(len(X), dtype=float)
    return ((dias_cobertura + ruido) <= (X[:, 2] + 2.0)).astype(int)


def generate_synthetic_data(n_samples: int = 1000, random_state: int = 42) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(random_state)

    # Combina productos de baja rotación/stock, escala estándar y escala en gramos
    n_low = n_samples // 3
    n_grams = n_samples // 6
    n_std = n_samples - n_low - n_grams

    stock_low = rng.uniform(0.5, 25.0, size=n_low)
    ventas_low = rng.uniform(0.2, 4.0, size=n_low)

    stock_std = rng.uniform(0.5, 100.0, size=n_std)
    ventas_std = rng.uniform(0.5, 15.0, size=n_std)

    stock_grams = rng.uniform(50.0, 600.0, size=n_grams)
    ventas_grams = rng.uniform(10.0, 150.0, size=n_grams)

    stock_actual = np.concatenate([stock_low, stock_std, stock_grams])
    ventas_diarias = np.concatenate([ventas_low, ventas_std, ventas_grams])
    dias_entrega = rng.integers(1, 15, size=n_samples).astype(float)

    X = np.column_stack([stock_actual, ventas_diarias, dias_entrega])
    # Agrega ligero ruido aleatorio para evitar una frontera de separación trivial
    ruido = rng.normal(0.0, 0.25, size=n_samples)
    y = _label_scenarios(X, noise=ruido)
    return X, y


def generate_catalog_scenarios() -> tuple[np.ndarray, np.ndarray]:
    return CATALOG_SCENARIOS.copy(), _label_scenarios(CATALOG_SCENARIOS)


def train_and_save_model(output_path: Path | str = DEFAULT_MODEL_PATH) -> Pipeline:
    X_synth, y_synth = generate_synthetic_data(n_samples=1000, random_state=42)
    X_cat, y_cat = generate_catalog_scenarios()

    X = np.vstack([X_synth, X_cat])
    y = np.concatenate([y_synth, y_cat])

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # PolynomialFeatures(degree=2) incorpora la interacción ventas_diarias * dias_entrega
    model = Pipeline(
        [
            ("poly", PolynomialFeatures(degree=2, include_bias=False)),
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(C=10.0, max_iter=1000, random_state=42)),
        ]
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"Accuracy del modelo: {acc:.4f}")
    print(classification_report(y_test, y_pred))

    target_path = Path(output_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, target_path)
    return model


if __name__ == "__main__":
    train_and_save_model()
