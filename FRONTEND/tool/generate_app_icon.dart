import 'dart:ui' as ui;
import 'dart:io';
import 'package:flutter/material.dart';

/// This script generates a 1024x1024 PNG icon using Icons.eco
Future<void> main() async {
  const size = 1024.0;

  final recorder = ui.PictureRecorder();
  final canvas = Canvas(recorder);

  final painter = const _EcoIconPainter();
  painter.paint(canvas, const Size(size, size));

  final picture = recorder.endRecording();
  final img = await picture.toImage(size.toInt(), size.toInt());

  final pngBytes = await img.toByteData(format: ui.ImageByteFormat.png);

  final file = File('assets/icons/app_icon.png');
  await file.create(recursive: true);
  await file.writeAsBytes(pngBytes!.buffer.asUint8List());

  print("✅ Icon generated at assets/icons/app_icon.png");
}

class _EcoIconPainter extends CustomPainter {
  const _EcoIconPainter();

  @override
  void paint(Canvas canvas, Size size) {
    final paintBg = Paint()..color = const Color(0xFF1B5E20);
    canvas.drawRect(Offset.zero & size, paintBg);

    const icon = Icons.eco;
    const iconColor = Colors.white;

    final textPainter = TextPainter(
      text: TextSpan(
        text: String.fromCharCode(icon.codePoint),
        style: TextStyle(
          fontFamily: icon.fontFamily,
          fontSize: size.width * 0.55,
          color: iconColor,
        ),
      ),
      textDirection: TextDirection.ltr,
    );

    textPainter.layout();
    textPainter.paint(
      canvas,
      Offset(
        (size.width - textPainter.width) / 2,
        (size.height - textPainter.height) / 2,
      ),
    );
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
