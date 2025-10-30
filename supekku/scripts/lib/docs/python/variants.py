"""Variant coordination for different documentation types."""

from pathlib import Path

from .models import VariantSpec, VariantType


class VariantCoordinator:
    """Coordinates different documentation variants (PUBLIC, ALL, TESTS)."""

    # Predefined variant presets
    PRESETS: dict[str, VariantSpec] = {
        "public": VariantSpec.public(),
        "all": VariantSpec.all_symbols(),
        "tests": VariantSpec.tests(),
    }

    @classmethod
    def get_preset(cls, name: str) -> VariantSpec:
        """Get a predefined variant preset by name."""
        if name not in cls.PRESETS:
            raise ValueError(
                f"Unknown variant preset: {name}. Available: {list(cls.PRESETS.keys())}",
            )
        return cls.PRESETS[name]

    @classmethod
    def get_files_for_variant(cls, path: Path, variant_spec: VariantSpec) -> list[Path]:
        """Get list of files to process for a given variant."""
        if path.is_file():
            return [path]

        if not path.is_dir():
            raise FileNotFoundError(f"Path does not exist: {path}")

        if variant_spec.variant_type == VariantType.TESTS:
            # For tests variant, only include test files
            return sorted(
                [f for f in path.rglob("*.py") if f.name.endswith("_test.py")],
            )
        # For public/all variants, exclude test files and __init__.py
        return sorted(
            [
                f
                for f in path.rglob("*.py")
                if not f.name.endswith("_test.py") and f.name != "__init__.py"
            ],
        )

    @classmethod
    def should_include_symbol(
        cls, symbol_info: dict, variant_spec: VariantSpec,
    ) -> bool:
        """Determine if a symbol should be included based on variant rules."""
        is_private = symbol_info.get("is_private", False)

        if variant_spec.variant_type == VariantType.PUBLIC:
            return not is_private
        # ALL and TESTS variants include private symbols
        return True

    @classmethod
    def filter_analysis_for_variant(
        cls, analysis: dict, variant_spec: VariantSpec,
    ) -> dict:
        """Filter analysis results based on variant specification."""
        if "error" in analysis:
            return analysis

        filtered = analysis.copy()

        # Filter constants
        if analysis.get("constants"):
            filtered["constants"] = [
                c
                for c in analysis["constants"]
                if cls.should_include_symbol(c, variant_spec)
            ]

        # Filter functions
        if analysis.get("functions"):
            filtered["functions"] = [
                f
                for f in analysis["functions"]
                if cls.should_include_symbol(f, variant_spec)
            ]

        # Filter classes and their methods
        if analysis.get("classes"):
            filtered_classes = []
            for class_info in analysis["classes"]:
                if cls.should_include_symbol(class_info, variant_spec):
                    filtered_class = class_info.copy()
                    # Filter methods within class
                    filtered_class["methods"] = [
                        m
                        for m in class_info["methods"]
                        if cls.should_include_symbol(m, variant_spec)
                    ]
                    filtered_classes.append(filtered_class)
            filtered["classes"] = filtered_classes

        return filtered
