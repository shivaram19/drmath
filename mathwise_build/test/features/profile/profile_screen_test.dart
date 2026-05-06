import 'package:flutter_test/flutter_test.dart';
import 'package:mathwise/features/profile/profile_screen.dart';

import '../../test_helpers.dart';

void main() {
  group('ProfileScreen', () {
    testWidgets('renders user name', (WidgetTester tester) async {
      setLargeViewport(tester);
      await pumpWithTheme(tester, const ProfileScreen());

      // Demo user name from DemoData
      expect(find.textContaining('Alex'), findsOneWidget);
    });

    testWidgets('shows achievements section', (WidgetTester tester) async {
      setLargeViewport(tester);
      await pumpWithTheme(tester, const ProfileScreen());

      expect(find.text('Achievements'), findsOneWidget);
    });

    testWidgets('shows topic progress section', (WidgetTester tester) async {
      setLargeViewport(tester);
      await pumpWithTheme(tester, const ProfileScreen());

      expect(find.text('Topic Progress'), findsOneWidget);
    });
  });
}
