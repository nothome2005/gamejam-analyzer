from abc import ABC, abstractmethod

class GitProviderAdapter(ABC):
    """
    Abstract adapter interface for Git hosting services (AC-NF-006).
    """
    @abstractmethod
    def verify_commit_exists(self, repo_url: str, commit_hash: str) -> bool:
        pass

    @abstractmethod
    def fetch_archive_hash(self, repo_url: str, commit_hash: str) -> str:
        pass

class MockGitHubAdapter(GitProviderAdapter):
    def verify_commit_exists(self, repo_url: str, commit_hash: str) -> bool:
        return len(commit_hash) in (40, 64)

    def fetch_archive_hash(self, repo_url: str, commit_hash: str) -> str:
        return "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

class MockGitLabAdapter(GitProviderAdapter):
    def verify_commit_exists(self, repo_url: str, commit_hash: str) -> bool:
        return len(commit_hash) in (40, 64)

    def fetch_archive_hash(self, repo_url: str, commit_hash: str) -> str:
        return "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
