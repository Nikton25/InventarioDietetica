from pathlib import Path
import joblib
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split

DEFAULT_MODEL_PATH = Path(__file__).resolve().parent / "modelo_reposicion.joblib"
SAFETY_MARGIN_DAYS = 1.0


def build_features(stock_actual: float, ventas_diarias: float, dias_entrega: float) -> np.ndarray:
    dias_cobertura = stock_actual / ventas_diarias
    return np.array([[dias_cobertura, dias_entrega]], dtype=float)


def generate_synthetic_data(n_samples: int = 500, random_state: int = 42) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(random_state)

    dias_cobertura = rng.uniform(0.0, 30.0, size=n_samples)
    dias_entrega = rng.integers(1, 15, size=n_samples).astype(float)

    # Agrega ligero ruido aleatorio para evitar una frontera de separación trivial
    ruido = rng.normal(0.0, 0.25, size=n_samples)
    necesita_reposicion = ((dias_cobertura + ruido) <= (dias_entrega + SAFETY_MARGIN_DAYS)).astype(int)

    X = np.column_stack([dias_cobertura, dias_entrega])
    return X, necesita_reposicion


def train_and_save_model(output_path: Path | str = DEFAULT_MODEL_PATH) -> LogisticRegression:
    X, y = generate_synthetic_data(n_samples=500, random_state=42)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = LogisticRegression(random_state=42)
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
