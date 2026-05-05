enum SectionType { concrete, pictorial, abstract }

class ConceptSection {
  final SectionType type;
  final String title;
  final String body;
  final String? imageUrl;
  final String? formula;

  const ConceptSection({
    required this.type,
    required this.title,
    required this.body,
    this.imageUrl,
    this.formula,
  });
}

class ConceptTopic {
  final String id;
  final String breadcrumb;
  final String title;
  final double progress;
  final List<ConceptSection> sections;
  final ConceptQuestion? quickCheck;

  const ConceptTopic({
    required this.id,
    required this.breadcrumb,
    required this.title,
    required this.progress,
    required this.sections,
    this.quickCheck,
  });
}

class ConceptQuestion {
  final String question;
  final List<String> options;
  final int correctIndex;

  const ConceptQuestion({
    required this.question,
    required this.options,
    required this.correctIndex,
  });
}
