"""Run bundled DINO ONNX on locally prepared app-preprocessed image tensors.

The probe is exploratory; reviewed app-gallery images may overlap training.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tmp" / "onnx_diagnostics_deps"))
import numpy as np  # noqa: E402
import onnxruntime as ort  # noqa: E402


def main() -> None:
    manifest = ROOT / "tmp" / "unknown_scan" / "fixture_manifest.json"
    rows = json.loads(manifest.read_text(encoding="utf-8"))
    options = ort.SessionOptions()
    options.intra_op_num_threads = 4
    options.inter_op_num_threads = 1
    model = ROOT / "frontend_recovered" / "assets" / "models" / "dinov2_vits14_encoder.onnx"
    session = ort.InferenceSession(str(model), options, providers=["CPUExecutionProvider"])
    assert [i.name for i in session.get_inputs()] == ["image"]
    assert [o.name for o in session.get_outputs()] == ["embedding"]
    for i, row in enumerate(rows, 1):
        source = np.fromfile(row["tensor"], dtype="<f4").reshape(1, 3, 224, 224)
        embedding = session.run(["embedding"], {"image": source})[0]
        assert embedding.shape == (1, 384)
        embedding.astype("<f4").tofile(row["embedding"])
        if i % 10 == 0 or i == len(rows):
            print("EMBEDDED", i, len(rows), flush=True)


if __name__ == "__main__":
    main()
