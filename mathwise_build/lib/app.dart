import 'package:flutter/material.dart';
import 'core/constants/app_theme.dart';
import 'features/home/home_screen.dart';

class MathWiseApp extends StatelessWidget {
  const MathWiseApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'MathWise',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.lightTheme,
      home: const HomeScreen(),
    );
  }
}
