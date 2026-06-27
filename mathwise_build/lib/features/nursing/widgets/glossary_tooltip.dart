import 'package:flutter/material.dart';

/// Highlights medical terms that have Telugu translations in the glossary.
class GlossaryText extends StatelessWidget {
  final String text;
  final Map<String, String> glossary;
  final TextStyle? style;

  const GlossaryText({
    super.key,
    required this.text,
    required this.glossary,
    this.style,
  });

  @override
  Widget build(BuildContext context) {
    final defaultStyle = style ?? DefaultTextStyle.of(context).style;
    final tokens = text.split(RegExp(r'(?=[\s\.,;!?])|(?<=[\s\.,;!?])'));

    return Text.rich(
      TextSpan(
        children: tokens.map((token) {
          final lower = token.trim().toLowerCase();
          final telugu = glossary[lower];
          if (telugu != null && token.trim().isNotEmpty) {
            return WidgetSpan(
              alignment: PlaceholderAlignment.middle,
              child: Tooltip(
                message: telugu,
                child: Text(
                  token,
                  style: defaultStyle.copyWith(
                    decoration: TextDecoration.underline,
                    decorationColor:
                        Theme.of(context).colorScheme.primary.withValues(
                              alpha: 0.5,
                            ),
                    color: Theme.of(context).colorScheme.primary,
                  ),
                ),
              ),
            );
          }
          return TextSpan(text: token, style: defaultStyle);
        }).toList(),
      ),
    );
  }
}
