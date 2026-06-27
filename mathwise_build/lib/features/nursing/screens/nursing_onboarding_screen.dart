import 'package:flutter/material.dart';

import '../services/nursing_storage_service.dart';
import '../widgets/nursing_app_bar.dart';
import 'nursing_home_screen.dart';

/// Brief 3-card onboarding for first-time nursing users.
class NursingOnboardingScreen extends StatefulWidget {
  const NursingOnboardingScreen({super.key});

  @override
  State<NursingOnboardingScreen> createState() => _NursingOnboardingScreenState();
}

class _NursingOnboardingScreenState extends State<NursingOnboardingScreen> {
  final _storage = NursingStorageService();
  final _pageController = PageController();
  int _currentPage = 0;

  final _pages = const [
    _OnboardingPage(
      icon: Icons.menu_book_outlined,
      title: 'Practice by Subject',
      body: 'Choose a nursing subject and topic. Practice MCQs one by one and read explanations.',
    ),
    _OnboardingPage(
      icon: Icons.timer_outlined,
      title: 'Full Mock Test',
      body: 'Take a timed 60-minute mock test with navigation and review, just like the real exam.',
    ),
    _OnboardingPage(
      icon: Icons.trending_up,
      title: 'Review Weak Areas',
      body: 'See which topics need more work and get a personalized practice PDF.',
    ),
  ];

  void _next() {
    if (_currentPage < _pages.length - 1) {
      _pageController.nextPage(
        duration: const Duration(milliseconds: 300),
        curve: Curves.easeInOut,
      );
    } else {
      _finish();
    }
  }

  Future<void> _finish() async {
    await _storage.setOnboardingSeen(true);
    if (!mounted) return;
    Navigator.of(context).pushReplacement(
      MaterialPageRoute<void>(builder: (_) => const NursingHomeScreen()),
    );
  }

  @override
  void dispose() {
    _pageController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: const NursingAppBar(
        title: 'Getting Started',
        showBackButton: false,
      ),
      body: Column(
        children: [
          Expanded(
            child: PageView(
              controller: _pageController,
              onPageChanged: (index) => setState(() => _currentPage = index),
              children: _pages,
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(20),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                TextButton(
                  onPressed: _finish,
                  child: const Text('Skip'),
                ),
                Row(
                  children: List.generate(
                    _pages.length,
                    (index) => Container(
                      width: 8,
                      height: 8,
                      margin: const EdgeInsets.symmetric(horizontal: 4),
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: index == _currentPage
                            ? Theme.of(context).colorScheme.primary
                            : Colors.grey.shade300,
                      ),
                    ),
                  ),
                ),
                ElevatedButton(
                  onPressed: _next,
                  child: Text(
                    _currentPage == _pages.length - 1
                        ? 'Get Started'
                        : 'Next',
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _OnboardingPage extends StatelessWidget {
  final IconData icon;
  final String title;
  final String body;

  const _OnboardingPage({
    required this.icon,
    required this.title,
    required this.body,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(32),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(icon, size: 80, color: Theme.of(context).colorScheme.primary),
          const SizedBox(height: 32),
          Text(
            title,
            style: Theme.of(context).textTheme.headlineSmall,
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 16),
          Text(
            body,
            style: Theme.of(context).textTheme.bodyLarge,
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }
}
