import 'package:flutter/material.dart';
import 'app/app.dart';
import 'app/app_session.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await AppSession.instance.restore();
  runApp(const VirasatApp());
}
