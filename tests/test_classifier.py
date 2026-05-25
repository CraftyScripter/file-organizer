from __future__ import annotations

from pathlib import Path

from core.classifier import FileClassifier, FileMetadata


def test_type_classification_preserves_original_categories() -> None:
    classifier = FileClassifier()
    metadata = FileMetadata(Path("report.pdf"), "pdf", 1, 0, 0)

    assert classifier.classify(metadata, "type") == Path("document")


def test_custom_rule_can_route_large_pdf_to_books() -> None:
    classifier = FileClassifier(
        [{"enabled": True, "conditions": {"ext": "pdf", "size_gt_mb": 50}, "destination": "Books"}]
    )
    metadata = FileMetadata(Path("big.pdf"), "pdf", 60 * 1024 * 1024, 0, 0)

    assert classifier.classify(metadata, "custom_rules") == Path("Books")
