"""Export the evaluated DINOv2 encoder from the SAME live Colab runtime.

Run after evaluate_dinov2_retrieval_colab.py. This only prepares a candidate;
Flutter integration and phone performance remain unverified. Artifacts are
saved to the dataset owner's existing private Drive root after parity passes.
"""

import subprocess
import sys

assert winner == "retrieval_3", "Run the DINOv2 experiment first in this runtime"
assert who == "manuagarwal885@gmail.com"
assert len(labels) == 20 and train_x.shape == (2155, 384)
assert len(train_y) == 2155

subprocess.check_call([sys.executable, "-m", "pip", "-q", "install", "onnx", "onnxruntime"])
import onnx
import onnxruntime as ort

export_dir = Path("/content/virasatai_dinov2_export")
export_dir.mkdir(exist_ok=True)
onnx_path = export_dir / "dinov2_vits14_encoder.onnx"
refs_path = export_dir / "monument_references.npz"
labels_path = export_dir / "labels.txt"

cpu_model = model.cpu().eval()
example = torch.randn(1, 3, 224, 224)


class EncoderOnly(torch.nn.Module):
    def __init__(self, backbone):
        super().__init__()
        self.backbone = backbone

    def forward(self, image):
        # Keep the optional training mask outside the ONNX input signature.
        return self.backbone.forward_features(image, masks=None)["x_norm_clstoken"]


encoder_only = EncoderOnly(cpu_model).eval()
with torch.inference_mode():
    torch.onnx.export(encoder_only, example, str(onnx_path), opset_version=17,
                      input_names=["image"], output_names=["embedding"],
                      dynamic_axes={"image": {0: "batch"},
                                    "embedding": {0: "batch"}},
                      dynamo=False)
onnx.checker.check_model(str(onnx_path))

# The reference bank is training-only. Preserve exact class ordering and
# per-class 3-neighbour aggregation used by the evaluated experiment.
np.savez_compressed(refs_path, embeddings=train_x.astype(np.float32),
                    class_ids=train_y.astype(np.int32), labels=np.array(labels))
labels_path.write_text("\n".join(labels) + "\n", encoding="utf-8")

session = ort.InferenceSession(str(onnx_path), providers=["CPUExecutionProvider"])
assert [item.name for item in session.get_inputs()] == ["image"]
assert session.get_outputs()[0].name == "embedding"

# Compare embeddings and final retrieval labels on actual held-out photos.
# Small numerical differences are fine only if the decision remains the same.
holdout_rows = splits["test"][:12]
reference = features["test", "full"][:12]
assert reference.shape == (12, 384)
loader = DataLoader(Photos(holdout_rows, "full"), batch_size=1, shuffle=False)
max_error = 0.0
onnx_features = []
with torch.inference_mode():
    for batch, torch_embedding in zip(loader, reference):
        output = session.run(None, {"image": batch.numpy().astype(np.float32)})[0][0]
        output = output.astype(np.float32)
        output /= np.linalg.norm(output)
        max_error = max(max_error, float(np.max(np.abs(output - torch_embedding))))
        onnx_features.append(output)
onnx_features = np.stack(onnx_features)
torch_prediction = retrieval_prob(reference, 3).argmax(axis=1)
onnx_prediction = retrieval_prob(onnx_features, 3).argmax(axis=1)
assert np.array_equal(torch_prediction, onnx_prediction), "ONNX changed held-out predictions"
assert max_error < 0.002, f"ONNX embedding difference too large: {max_error}"
print("EXPORT_PARITY_OK", {"checked_test_photos": len(holdout_rows),
                           "max_embedding_error": max_error,
                           "onnx_mb": round(onnx_path.stat().st_size / 1e6, 1),
                           "references_mb": round(refs_path.stat().st_size / 1e6, 1)},
      flush=True)
print("EXPORT_FILES", str(onnx_path), str(refs_path), str(labels_path), flush=True)

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
