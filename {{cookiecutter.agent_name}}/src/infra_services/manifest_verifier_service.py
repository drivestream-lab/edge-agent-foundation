"""Deployment manifest verification for {{ cookiecutter.agent_name }}."""

import hashlib

import httpx

from src.exceptions import ManifestVerificationError
from src.infra_services.base_infra_service import BaseInfraService
from src.logging import get_logger
from src.models import DeploymentManifest, ManifestArtifact

logger = get_logger()


class ManifestVerifierService(BaseInfraService):
    """
    Fetch and verify deployment manifests.

    TODO: Implement TUF signature verification on manifest.signature.
    Current implementation validates JSON schema and SHA-256 digests only.
    """

    def __init__(self) -> None:
        super().__init__()
        self._client: httpx.AsyncClient | None = None

    async def initialize(self) -> None:
        self._client = httpx.AsyncClient(timeout=30.0)
        self._initialized = True
        self.logger.info("ManifestVerifierService initialized")

    async def fetch_and_verify(self, manifest_url: str) -> DeploymentManifest:
        if self._client is None:
            raise RuntimeError("ManifestVerifierService not initialized")
        response = await self._client.get(manifest_url)
        response.raise_for_status()
        data = response.json()
        manifest = DeploymentManifest.model_validate(data)

        if manifest.signature:
            # TODO: TUF signature verification — reject unsigned manifests in production.
            logger.warning(
                "Manifest signature present but TUF verification not implemented",
                version=manifest.version,
            )
        else:
            logger.warning("Manifest has no signature — acceptable for dev only")

        logger.info(
            "Manifest fetched", version=manifest.version, model_version=manifest.model_version
        )
        return manifest

    def verify_artifact_hashes(self, manifest: DeploymentManifest) -> None:
        for artifact in manifest.artifacts:
            self._verify_digest_format(artifact)

    def verify_file_hash(self, artifact: ManifestArtifact, file_bytes: bytes) -> None:
        digest = hashlib.sha256(file_bytes).hexdigest()
        if digest != artifact.digest_sha256:
            raise ManifestVerificationError(
                f"Hash mismatch for {artifact.name}: expected {artifact.digest_sha256}, got {digest}"
            )
        logger.info("Artifact hash verified", name=artifact.name)

    @staticmethod
    def _verify_digest_format(artifact: ManifestArtifact) -> None:
        if len(artifact.digest_sha256) != 64:
            raise ManifestVerificationError(f"Invalid SHA-256 digest length for {artifact.name}")
        try:
            int(artifact.digest_sha256, 16)
        except ValueError as exc:
            raise ManifestVerificationError(f"Invalid SHA-256 digest for {artifact.name}") from exc

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None
        self._initialized = False

    async def health_check(self) -> bool:
        return self._initialized and self._client is not None
