from dataclasses import dataclass


@dataclass(frozen=True)
class Metrics:
    true_positives: int
    false_positives: int
    false_negatives: int
    true_negatives: int

    @property
    def precision(self) -> float:
        """When the AI says 'breaking', how often is it right?"""
        if self.false_positives + self.true_positives == 0:
            return 0.0
        return self.true_positives / (self.false_positives + self.true_positives)

    @property
    def recall(self) -> float:
        """Of all truly breaking releases, how many did the AI catch?"""
        if self.false_negatives + self.true_positives == 0:
            return 0.0
        return self.true_positives / (self.false_negatives + self.true_positives)


def compute_metrics(results: list[tuple[bool, bool]]) -> Metrics:
    """Count outcomes from (expected, predicted) pairs."""
    true_positives = 0
    false_positives = 0
    false_negatives = 0
    true_negatives = 0

    for expected, predicted in results:
        if expected and predicted:
            true_positives += 1
        elif not expected and predicted:
            false_positives += 1
        elif expected and not predicted:
            false_negatives += 1
        else:
            true_negatives += 1

    return Metrics(
        true_positives=true_positives,
        false_positives=false_positives,
        false_negatives=false_negatives,
        true_negatives=true_negatives
    )