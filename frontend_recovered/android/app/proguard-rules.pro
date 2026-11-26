# ONNX Runtime's native JNI code resolves these classes/methods dynamically.
# Removing or renaming them causes SIGABRT during OrtSession.run on release APKs.
-keep class ai.onnxruntime.** { *; }
