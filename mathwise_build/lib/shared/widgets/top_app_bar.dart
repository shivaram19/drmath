import 'package:flutter/material.dart';
import '../../core/constants/app_colors.dart';

class MathWiseAppBar extends StatelessWidget implements PreferredSizeWidget {
  final String? title;
  final List<Widget>? actions;
  final bool showBackButton;
  final VoidCallback? onBack;
  final Widget? leading;

  const MathWiseAppBar({
    super.key,
    this.title,
    this.actions,
    this.showBackButton = false,
    this.onBack,
    this.leading,
  });

  @override
  Widget build(BuildContext context) {
    return AppBar(
      backgroundColor: const Color(0xFFF8FAFC),
      elevation: 0,
      scrolledUnderElevation: 0,
      leading: showBackButton
          ? IconButton(
              onPressed: onBack ?? () => Navigator.of(context).pop(),
              icon: const Icon(Icons.arrow_back, color: AppColors.primaryContainer),
            )
          : leading,
      title: title != null
          ? Text(
              title!,
              style: Theme.of(context).appBarTheme.titleTextStyle,
            )
          : Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Icon(
                  Icons.menu_book,
                  color: AppColors.primaryContainer,
                  size: 28,
                ),
                const SizedBox(width: 8),
                Text(
                  'MathWise',
                  style: Theme.of(context).appBarTheme.titleTextStyle,
                ),
              ],
            ),
      actions: actions ??
          [
            const Padding(
              padding: EdgeInsets.only(right: 16),
              child: CircleAvatar(
                radius: 18,
                backgroundColor: AppColors.primaryContainer,
                child: Icon(
                  Icons.person,
                  color: Colors.white,
                  size: 20,
                ),
              ),
            ),
          ],
    );
  }

  @override
  Size get preferredSize => const Size.fromHeight(kToolbarHeight);
}
