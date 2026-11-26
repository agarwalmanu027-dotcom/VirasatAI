"""Resume after the first ONNX export stopped at the CPU/GPU comparison.

Paste into the SAME Colab runtime. It reuses the already exported files and
cached test embeddings, verifies ONNX parity, then saves to private Drive.
"""

import numpy as np
from googleapiclient.http import MediaFileUpload

assert who == "manuagarwal885@gmail.com"
assert winner == "retrieval_3"
assert onnx_path.exists() and refs_path.exists() and labels_path.exists()
assert features["test", "full"].shape == (456, 384)
assert session.get_inputs()[0].name == "image"

reference = features["test", "full"][:12]
loader = DataLoader(Photos(splits["test"][:12], "full"), batch_size=1,
                    shuffle=False)
max_error = 0.0
onnx_features = []
for batch, torch_embedding in zip(loader, reference):
    output = session.run(None, {"image": batch.numpy().astype(np.float32)})[0][0]
    output = output.astype(np.float32)
    output /= np.linalg.norm(output)
    max_error = max(max_error, float(np.max(np.abs(output - torch_embedding))))
    onnx_features.append(output)
onnx_features = np.stack(onnx_features)
assert np.array_equal(retrieval_prob(reference, 3).argmax(axis=1),
                      retrieval_prob(onnx_features, 3).argmax(axis=1)), \
       "ONNX changed held-out predictions"
assert max_error < 0.002, f"ONNX embedding difference too large: {max_error}"
print("EXPORT_PARITY_OK", {"checked_test_photos": 12,
                           "max_embedding_error": max_error,
                           "onnx_mb": round(onnx_path.stat().st_size / 1e6, 1),
                           "references_mb": round(refs_path.stat().st_size / 1e6, 1)},
      flush=True)

export_folder = drive.files().create(
    body={"name": "dinov2_onnx_candidate_2026-10-22",
          "mimeType": "application/vnd.google-apps.folder",
          "parents": [OUTPUT_PARENT_ID]}, fields="id,webViewLink").execute()
for file_path in (onnx_path, refs_path, labels_path):
    drive.files().create(
        body={"name": file_path.name, "parents": [export_folder["id"]]},
        media_body=MediaFileUpload(str(file_path), resumable=True),
        fields="id").execute()
print("EXPORT_SAVED", export_folder, flush=True)
