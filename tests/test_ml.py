from pathlib import Path
import joblib
import numpy as np
from ml.train_model import build_features, generate_synthetic_data, train_and_save_model


def test_generate_synthetic_data_shape_and_columns():
    X, y = generate_synthetic_data(n_samples=300, random_state=42)
    assert X.shape == (300, 2)
    assert y.shape == (300,)
    assert set(np.unique(y)).issubset({0, 1})


def test_train_and_save_model_creates_artifact_and_predicts(tmp_path: Path):
    model_path = tmp_path / "modelo_reposicion.joblib"
    train_and_save_model(output_path=model_path)

    assert model_path.exists()
    model = joblib.load(model_path)

    # Caso crítico: stock bajo (5), ventas altas (10/día), entrega en 7 días -> necesita reposición (1)
    assert int(model.predict(build_features(5.0, 10.0, 7.0))[0]) == 1

    # Caso holgado: stock alto (95), ventas bajas (1/día), entrega en 2 días -> stock suficiente (0)
    assert int(model.predict(build_features(95.0, 1.0, 2.0))[0]) == 0

    # Caso baja rotación y bajo stock (Garbanzos): cobertura 1.3 días <= 5 + 1 -> necesita reposición (1)
    assert int(model.predict(build_features(2.0, 1.5, 5.0))[0]) == 1

    # Caso cobertura 9 días vs entrega 7 días (+1 margen = 8): 9 > 8 -> stock suficiente (0)
    assert int(model.predict(build_features(18.0, 2.0, 7.0))[0]) == 0

    # Caso stock moderado y baja rotación (Avena): cobertura 16.7 días > 4 + 1 -> stock suficiente (0)
    assert int(model.predict(build_features(25.0, 1.5, 4.0))[0]) == 0

    # Caso stock en gramos (Té Verde): 500g / 120g diarios = 4.2 días <= 5 + 1 -> necesita reposición (1)
    assert int(model.predict(build_features(500.0, 120.0, 5.0))[0]) == 1

    # Caso stock en gramos holgado (Té Verde): 500g / 25g diarios = 20 días > 5 + 1 -> stock suficiente (0)
    assert int(model.predict(build_features(500.0, 25.0, 5.0))[0]) == 0
