from dataclasses import dataclass


@dataclass(frozen=True)
class DocumentArtifact:
    action: str
    path: str
    content: str

    def __post_init__(self) -> None:
        if self.action != "document.create":
            raise ValueError("DocumentArtifact action must be document.create")
        if not isinstance(self.path, str) or not self.path:
            raise TypeError("DocumentArtifact path must be a non-empty string")
        if not isinstance(self.content, str):
            raise TypeError("DocumentArtifact content must be a string")
