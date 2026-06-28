/// Concept Content Screen — Types of Triangles
///
/// Research basis:
/// - Bruner (1966) CPA sequence: Concrete → Pictorial → Abstract [^5].
///   This screen enforces this ordering as an invariant. Section 1 (bridge
///   photo) = Concrete. Section 2 (SVG classification guide) = Pictorial.
///   Section 3 (Pythagorean formula) = Abstract.
///
/// - Setyawan et al. (2024) meta-analysis: CPA effect size g = 0.72 [^6].
///   Reordering these sections would violate the Research-First Covenant.
///
/// - CAST UDL (2018): Multiple means of representation [^24].
///   Text + photo + diagram + formula accommodates visual, verbal, and
///   abstract learners in a single scroll.
///
/// - Sweller (1988): Split-attention increases extraneous load [^1].
///   All representations are vertically stacked; no lateral eye movement.
///
/// ADR-010 Decisions: D2, D10
library;

import 'package:flutter/material.dart';
import '../../core/constants/app_colors.dart';
import '../../shared/data/demo_data.dart';
import '../../shared/models/concept.dart';
import '../../shared/widgets/top_app_bar.dart';
import '../practice/practice_question_screen.dart';

class ConceptContentScreen extends StatefulWidget {
  const ConceptContentScreen({super.key});

  @override
  State<ConceptContentScreen> createState() => _ConceptContentScreenState();
}

class _ConceptContentScreenState extends State<ConceptContentScreen> {
  int? _selectedOption;
  bool _showFeedback = false;

  void _navigateToPractice(BuildContext context) {
    Navigator.push(
      context,
      MaterialPageRoute<void>(builder: (_) => const PracticeQuestionScreen()),
    );
  }

  void _submitAnswer() {
    if (_selectedOption == null) return;
    setState(() {
      _showFeedback = true;
    });
  }

  @override
  Widget build(BuildContext context) {
    const concept = DemoData.trianglesConcept;

    return Scaffold(
      appBar: const MathWiseAppBar(showBackButton: true),
      body: SingleChildScrollView(
        padding: const EdgeInsets.fromLTRB(24, 16, 24, 120),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildHero(context, concept),
            const SizedBox(height: 32),
            // Section 1: CONCRETE (real-world photograph).
            // Rationale: Bruner (1966) — anchor abstract concepts in physical reality [^5].
            _buildRealLifeSection(context, concept.sections[0]),
            const SizedBox(height: 32),
            // Section 2: PICTORIAL (diagrams and classifications).
            // Rationale: Pictorial bridges concrete experience and abstract symbolism [^5].
            _buildClassificationGuide(context, concept.sections[1]),
            const SizedBox(height: 32),
            // Section 3: ABSTRACT (formula and symbolic reasoning).
            // Rationale: Only after concrete and pictorial grounding is the student
            // ready for pure symbolic manipulation [^5].
            _buildExplanationSection(context, concept.sections[2]),
            const SizedBox(height: 32),
            // Quick Check: Retrieval practice, not re-reading.
            // Rationale: Roediger & Karpicke (2006): retrieval produces 50% better
            // long-term retention than re-reading [^16].
            if (concept.quickCheck != null)
              _buildQuickCheck(context, concept.quickCheck!),
            const SizedBox(height: 32),
            _buildCTA(context),
          ],
        ),
      ),
    );
  }

  Widget _buildHero(BuildContext context, ConceptTopic concept) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            const Icon(Icons.category, color: AppColors.primary, size: 18),
            const SizedBox(width: 8),
            Text(
              concept.breadcrumb.toUpperCase(),
              style: Theme.of(context).textTheme.labelLarge?.copyWith(
                color: AppColors.primary,
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),
        Text(concept.title, style: Theme.of(context).textTheme.displayLarge),
        const SizedBox(height: 12),
        Container(
          width: MediaQuery.of(context).size.width * 0.35 * concept.progress,
          height: 6,
          decoration: BoxDecoration(
            color: AppColors.primaryContainer,
            borderRadius: BorderRadius.circular(3),
          ),
        ),
        const SizedBox(height: 8),
        Text(
          '${(concept.progress * 100).round()}% mastered',
          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
            color: AppColors.onSurfaceVariant,
          ),
        ),
      ],
    );
  }

  Widget _buildRealLifeSection(BuildContext context, ConceptSection section) {
    // Concrete representation: photograph of a real bridge with triangular trusses.
    // This answers "Why do we care?" before "What is it?"
    // Rationale: Relevance activates prior knowledge, improving encoding (Ausubel 1968).
    return Column(
      children: [
        Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Expanded(
              flex: 5,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    section.title,
                    style: Theme.of(context).textTheme.displaySmall?.copyWith(
                      color: AppColors.secondary,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    section.body,
                    style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                      color: AppColors.onSurfaceVariant,
                    ),
                  ),
                  const SizedBox(height: 12),
                  // Fun fact container: low-stakes retrieval cue.
                  // Rationale: Elaborative interrogation improves retention by 1.5× (Dunlosky 2013).
                  Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: AppColors.secondaryContainer.withValues(alpha: 0.3),
                      borderRadius: const BorderRadius.only(
                        topRight: Radius.circular(12),
                        bottomRight: Radius.circular(12),
                        bottomLeft: Radius.circular(12),
                      ),
                      border: const Border(
                        left: BorderSide(color: AppColors.secondary, width: 4),
                      ),
                    ),
                    child: Text(
                      "Fun Fact: A triangle's internal angles always sum to exactly 180 degrees!",
                      style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                        color: AppColors.secondary,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              flex: 7,
              child: ClipRRect(
                borderRadius: BorderRadius.circular(24),
                child: Container(
                  height: 200,
                  color: AppColors.surfaceContainerLow,
                  child: Stack(
                    fit: StackFit.expand,
                    children: [
                      // Concrete case study image.
                      Image.network(
                        section.imageUrl ?? 'https://images.unsplash.com/photo-1545558014-8692077e9b5c?w=600',
                        fit: BoxFit.cover,
                        errorBuilder: (context, error, stackTrace) => const Icon(Icons.broken_image),
                      ),
                      Container(
                        decoration: BoxDecoration(
                          gradient: LinearGradient(
                            begin: Alignment.topCenter,
                            end: Alignment.bottomCenter,
                            colors: [
                              Colors.transparent,
                              AppColors.onSurface.withValues(alpha: 0.6),
                            ],
                          ),
                        ),
                      ),
                      Positioned(
                        bottom: 16,
                        left: 16,
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'CASE STUDY',
                              style: Theme.of(context).textTheme.labelLarge?.copyWith(
                                color: Colors.white.withValues(alpha: 0.8),
                              ),
                            ),
                            Text(
                              'Triangular Steel Trusses',
                              style: Theme.of(context).textTheme.displaySmall?.copyWith(
                                color: Colors.white,
                                fontSize: 18,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildClassificationGuide(BuildContext context, ConceptSection section) {
    // Pictorial representation: geometric diagrams and classifications.
    // 3-column grid: equilateral, right-angled, scalene.
    // Rationale: Side-by-side comparison activates discriminative learning (Gentner 1983).
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: AppColors.surfaceContainerLowest,
        borderRadius: BorderRadius.circular(32),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.04),
            blurRadius: 20,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        children: [
          Text(
            section.title,
            style: Theme.of(context).textTheme.displaySmall,
          ),
          const SizedBox(height: 4),
          Text(
            section.body,
            style: Theme.of(context).textTheme.bodyLarge?.copyWith(
              color: AppColors.onSurfaceVariant,
            ),
          ),
          const SizedBox(height: 24),
          const Row(
            children: [
              Expanded(
                child: _TriangleTypeCard(
                  title: 'Equilateral',
                  description: 'All sides and angles are equal.',
                  color: AppColors.surface,
                ),
              ),
              SizedBox(width: 12),
              Expanded(
                child: _TriangleTypeCard(
                  title: 'Right-Angled',
                  description: 'Exactly one 90° angle.',
                  color: AppColors.surface,
                ),
              ),
              SizedBox(width: 12),
              Expanded(
                child: _TriangleTypeCard(
                  title: 'Scalene',
                  description: 'No sides or angles are equal.',
                  color: AppColors.surface,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildExplanationSection(BuildContext context, ConceptSection section) {
    // Abstract representation: theorem statement and formula.
    // Placed LAST in the scroll — never first. CPA ordering is invariant.
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: AppColors.surfaceContainerLow,
        borderRadius: BorderRadius.circular(32),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 64,
            height: 64,
            decoration: BoxDecoration(
              color: AppColors.primary,
              borderRadius: BorderRadius.circular(16),
            ),
            child: const Icon(Icons.lightbulb, color: Colors.white, size: 32),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  section.title,
                  style: Theme.of(context).textTheme.displaySmall,
                ),
                const SizedBox(height: 8),
                Text(
                  section.body,
                  style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                    color: AppColors.onSurfaceVariant,
                  ),
                ),
                const SizedBox(height: 16),
                // Formula presented in a visually distinct card.
                // Rationale: Isolating the formula reduces split-attention (Sweller 1988) [^1].
                if (section.formula != null)
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                    decoration: BoxDecoration(
                      color: Colors.white.withValues(alpha: 0.5),
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: Colors.white),
                    ),
                    child: Text(
                      section.formula!,
                      style: Theme.of(context).textTheme.displayMedium?.copyWith(
                        color: AppColors.primary,
                        fontSize: 20,
                      ),
                    ),
                  ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildQuickCheck(BuildContext context, ConceptQuestion quickCheck) {
    // Retrieval practice: one question at the end of the concept.
    // Rationale: Roediger & Karpicke (2006): testing produces 50% better
    // long-term retention than re-reading [^16].
    final options = quickCheck.options;
    final labels = ['A', 'B', 'C', 'D'];

    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: AppColors.surfaceContainerHighest.withValues(alpha: 0.5),
        borderRadius: BorderRadius.circular(32),
        border: Border.all(color: AppColors.surfaceContainer),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Expanded(
                child: Text(
                  'Quick Check',
                  style: Theme.of(context).textTheme.displaySmall,
                  overflow: TextOverflow.ellipsis,
                  maxLines: 1,
                ),
              ),
              const SizedBox(width: 8),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                decoration: BoxDecoration(
                  color: AppColors.primary.withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Text(
                  'QUESTION 1 OF 1',
                  style: Theme.of(context).textTheme.labelLarge?.copyWith(
                    color: AppColors.primary,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Text(
            quickCheck.question,
            style: Theme.of(context).textTheme.headlineMedium?.copyWith(
              fontWeight: FontWeight.w500,
            ),
          ),
          const SizedBox(height: 16),
          ...List.generate((options.length / 2).ceil(), (rowIndex) {
            final start = rowIndex * 2;
            final end = (start + 2).clamp(0, options.length);
            return Padding(
              padding: EdgeInsets.only(bottom: rowIndex < (options.length / 2).ceil() - 1 ? 12 : 0),
              child: Row(
                children: [
                  for (int i = start; i < end; i++)
                    Expanded(
                      child: Padding(
                        padding: EdgeInsets.only(right: i < end - 1 ? 12 : 0),
                        child: _QuizOption(
                          label: labels[i],
                          text: options[i],
                          isSelected: _selectedOption == i,
                          isSubmitted: _showFeedback,
                          isCorrectOption: i == quickCheck.correctIndex,
                          onTap: _showFeedback
                              ? null
                              : () {
                                  setState(() {
                                    _selectedOption = i;
                                  });
                                },
                        ),
                      ),
                    ),
                  if (end - start < 2) const Expanded(child: SizedBox()),
                ],
              ),
            );
          }),
          const SizedBox(height: 20),
          if (_showFeedback) ...[
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: _selectedOption == quickCheck.correctIndex
                    ? Colors.green.withValues(alpha: 0.1)
                    : AppColors.errorContainer.withValues(alpha: 0.3),
                borderRadius: BorderRadius.circular(16),
                border: Border.all(
                  color: _selectedOption == quickCheck.correctIndex
                      ? Colors.green
                      : AppColors.error,
                ),
              ),
              child: Row(
                children: [
                  Icon(
                    _selectedOption == quickCheck.correctIndex
                        ? Icons.check_circle
                        : Icons.error,
                    color: _selectedOption == quickCheck.correctIndex
                        ? Colors.green
                        : AppColors.error,
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      _selectedOption == quickCheck.correctIndex
                          ? 'Correct! Great job.'
                          : 'Not quite. The correct answer is ${labels[quickCheck.correctIndex]}.',
                      style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),
          ],
          Align(
            alignment: Alignment.centerRight,
            child: ElevatedButton.icon(
              onPressed: _showFeedback
                  ? null
                  : _submitAnswer,
              icon: const Icon(Icons.check_circle, size: 18),
              label: const Text('Submit Answer'),
              style: ElevatedButton.styleFrom(
                backgroundColor: AppColors.secondary,
                foregroundColor: AppColors.onSecondary,
                padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCTA(BuildContext context) {
    // "Practice This Topic" bridges concept to retrieval.
    // Rationale: Transfer-appropriate processing — practice in the same mode
    // as assessment improves performance (Morris et al. 1977).
    return Column(
      children: [
        SizedBox(
          width: double.infinity,
          child: ElevatedButton(
            onPressed: () => _navigateToPractice(context),
            style: ElevatedButton.styleFrom(
              backgroundColor: AppColors.primary,
              foregroundColor: AppColors.onPrimary,
              padding: const EdgeInsets.symmetric(vertical: 20),
              textStyle: const TextStyle(
                fontFamily: 'Lexend',
                fontSize: 20,
                fontWeight: FontWeight.w700,
              ),
            ),
            child: const Text('Practice This Topic'),
          ),
        ),
        const SizedBox(height: 12),
        Text(
          "Complete 5 problems to earn 50 XP and unlock 'Circle Geometry'",
          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
            color: AppColors.outline,
          ),
          textAlign: TextAlign.center,
        ),
      ],
    );
  }
}

class _TriangleTypeCard extends StatelessWidget {
  final String title;
  final String description;
  final Color color;

  const _TriangleTypeCard({
    required this.title,
    required this.description,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Container(
          height: 120,
          decoration: BoxDecoration(
            color: color,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: AppColors.surfaceContainer),
          ),
          child: const Center(
            child: Icon(
              Icons.change_history,
              size: 48,
              color: AppColors.primaryContainer,
            ),
          ),
        ),
        const SizedBox(height: 12),
        Text(
          title,
          style: const TextStyle(
            fontWeight: FontWeight.bold,
            color: AppColors.primary,
            fontSize: 14,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          description,
          style: Theme.of(context).textTheme.bodyMedium?.copyWith(fontSize: 12),
          textAlign: TextAlign.center,
        ),
      ],
    );
  }
}

class _QuizOption extends StatelessWidget {
  final String label;
  final String text;
  final bool isSelected;
  final bool isSubmitted;
  final bool isCorrectOption;
  final VoidCallback? onTap;

  const _QuizOption({
    required this.label,
    required this.text,
    this.isSelected = false,
    this.isSubmitted = false,
    this.isCorrectOption = false,
    this.onTap,
  });

  Color get _borderColor {
    if (!isSubmitted) {
      return isSelected ? AppColors.primary : Colors.transparent;
    }
    if (isCorrectOption) return Colors.green;
    if (isSelected) return AppColors.error;
    return Colors.transparent;
  }

  Color get _labelBgColor {
    if (!isSubmitted) {
      return isSelected ? AppColors.primary : AppColors.surfaceContainer;
    }
    if (isCorrectOption) return Colors.green;
    if (isSelected) return AppColors.error;
    return AppColors.surfaceContainer;
  }

  Color get _labelTextColor {
    if (!isSubmitted) {
      return isSelected ? Colors.white : AppColors.onSurfaceVariant;
    }
    if (isCorrectOption) return Colors.white;
    if (isSelected) return Colors.white;
    return AppColors.onSurfaceVariant;
  }

  Color get _textColor {
    if (!isSubmitted) {
      return isSelected ? AppColors.onSurface : AppColors.onSurfaceVariant;
    }
    if (isCorrectOption) return Colors.green;
    if (isSelected) return AppColors.error;
    return AppColors.onSurfaceVariant;
  }

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(16),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
            color: _borderColor,
            width: 2,
          ),
        ),
        child: Row(
          children: [
            Container(
              width: 40,
              height: 40,
              decoration: BoxDecoration(
                color: _labelBgColor,
                borderRadius: BorderRadius.circular(12),
              ),
              child: Center(
                child: Text(
                  label,
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    color: _labelTextColor,
                  ),
                ),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Text(
                text,
                style: TextStyle(
                  fontWeight: isSelected ? FontWeight.w500 : FontWeight.normal,
                  color: _textColor,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
