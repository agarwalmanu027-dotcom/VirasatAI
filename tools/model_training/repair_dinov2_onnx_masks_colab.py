"""Repair the ONNX optional-mask input in the same live DINOv2 Colab runtime.

The previous export created an unexpected required 'masks' input. This cell
re-exports an image-only wrapper, checks output parity, then saves artifacts.
"""

import numpy as np
import onnx
import onnxruntime as ort
import torch
from googleapiclient.http import MediaFileUpload

assert who == "manuagarwal885@gmail.com" and winner == "retrieval_3"
assert onnx_path.exists() and refs_path.exists() and labels_path.exists()
assert features["test", "full"].shape == (456, 384)


class ImageOnlyEncoder(torch.nn.Module):
    def __init__(self, backbone):
        super().__init__()
        self.backbone = backbone

    def forward(self, image):
        return self.backbone.forward_features(image, masks=None)["x_norm_clstoken"]


cpu_model = model.cpu().eval()
image_only = ImageOnlyEncoder(cpu_model).eval()
example = torch.randn(1, 3, 224, 224)
with torch.inference_mode():
    torch.onnx.export(image_only, example, str(onnx_path), opset_version=17,
                      input_names=["image"], output_names=["embedding"],
                      dynamic_axes={"image": {0: "batch"},
                                    "embedding": {0: "batch"}}, dynamo=False)
onnx.checker.check_model(str(onnx_path))
session = ort.InferenceSession(str(onnx_path), providers=["CPUExecutionProvider"])
inputs = [item.name for item in session.get_inputs()]
assert inputs == ["image"], f"Unexpected ONNX inputs: {inputs}"

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
assert max_error < 0.002, f"Embedding difference too large: {max_error}"
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
