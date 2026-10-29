from dataclasses import dataclass, field


@dataclass
class FailureInjector:
    fail_actions: set[str] = field(default_factory=set)

    def check(self, action: str) -> None:
        if action in self.fail_actions:
            raise RuntimeError(f"injected failure: {action}")

