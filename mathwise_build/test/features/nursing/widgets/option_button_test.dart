import 'package:flutter_test/flutter_test.dart';
import 'package:mathwise/features/nursing/widgets/option_button.dart';

import '../../../test_helpers.dart';

void main() {
  group('OptionButton', () {
    testWidgets('renders option text and letter', (WidgetTester tester) async {
      await pumpWithTheme(
        tester,
        const OptionButton(option: 'A) 120/80 mmHg'),
      );

      expect(find.text('A'), findsOneWidget);
      expect(find.text('A) 120/80 mmHg'), findsOneWidget);
    });

    testWidgets('calls onTap when tapped', (WidgetTester tester) async {
      var tapped = false;
      await pumpWithTheme(
        tester,
        OptionButton(
          option: 'B) Option B',
          onTap: () => tapped = true,
        ),
      );

      await tester.tap(find.text('B) Option B'));
      await tester.pump();

      expect(tapped, isTrue);
    });

    testWidgets('does not call onTap in feedback mode',
        (WidgetTester tester) async {
      var tapped = false;
      await pumpWithTheme(
        tester,
        OptionButton(
          option: 'C) Option C',
          showFeedback: true,
          onTap: () => tapped = true,
        ),
      );

      await tester.tap(find.text('C) Option C'));
      await tester.pump();

      expect(tapped, isFalse);
    });

    testWidgets('meets Android and iOS tap target guidelines',
        (WidgetTester tester) async {
      await pumpWithTheme(
        tester,
        const OptionButton(option: 'D) Option D'),
      );

      await expectLater(
        tester,
        meetsGuideline(androidTapTargetGuideline),
      );
      await expectLater(
        tester,
        meetsGuideline(iOSTapTargetGuideline),
      );
    });
  });
}
