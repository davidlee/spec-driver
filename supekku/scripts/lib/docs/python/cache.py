"""File-based caching for AST parsing with mtime and hash validation."""

import hashlib
import json
import os
import time
from pathlib import Path
from typing import Dict, Optional, Tuple

from .path_utils import PathNormalizer


class ParseCache:
    """File-based caching for AST parsing with mtime and hash validation."""

    def __init__(self, cache_dir: Optional[Path] = None):
        """Initialize cache with optional custom directory."""
        if cache_dir:
            self.cache_dir = cache_dir
        else:
            # Use platform-appropriate cache directory
            cache_base = (
                Path.home() / ".cache"
                if os.name != "nt"
                else Path.home() / "AppData" / "Local"
            )
            self.cache_dir = cache_base / "deterministic_ast_doc_generator"

        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.stats = {"hits": 0, "misses": 0, "invalidations": 0}

    def _get_cache_key(self, file_path: Path) -> str:
        """Generate stable cache key for file."""
        normalized = PathNormalizer.normalize_path_for_id(file_path)
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]

    def _get_cache_file(self, file_path: Path) -> Path:
        """Get cache file path for given source file."""
        cache_key = self._get_cache_key(file_path)
        return self.cache_dir / f"{cache_key}.json"

    def _get_file_info(self, file_path: Path) -> Tuple[float, str]:
        """Get file modification time and content hash."""
        stat = file_path.stat()
        mtime = stat.st_mtime

        # Calculate content hash
        with open(file_path, "rb") as f:
            content_hash = hashlib.sha256(f.read()).hexdigest()

        return mtime, content_hash

    def get(self, file_path: Path) -> Optional[Dict]:
        """Get cached analysis if valid, None otherwise."""
        cache_file = self._get_cache_file(file_path)

        if not cache_file.exists():
            self.stats["misses"] += 1
            return None

        try:
            # Check if source file still exists
            if not file_path.exists():
                self.stats["misses"] += 1
                return None

            current_mtime, current_hash = self._get_file_info(file_path)

            # Load cached data
            with open(cache_file, "r", encoding="utf-8") as f:
                cached_data = json.load(f)

            cached_mtime = cached_data.get("mtime")
            cached_hash = cached_data.get("content_hash")

            # Validate cache with both mtime and hash
            if cached_mtime == current_mtime and cached_hash == current_hash:
                self.stats["hits"] += 1
                return cached_data.get("analysis")
            else:
                self.stats["invalidations"] += 1
                # Remove stale cache
                cache_file.unlink(missing_ok=True)
                return None

        except (json.JSONDecodeError, KeyError, OSError):
            self.stats["misses"] += 1
            # Remove corrupted cache
            cache_file.unlink(missing_ok=True)
            return None

    def put(self, file_path: Path, analysis: Dict) -> None:
        """Store analysis in cache with metadata."""
        try:
            mtime, content_hash = self._get_file_info(file_path)
            cache_file = self._get_cache_file(file_path)

            cache_data = {
                "mtime": mtime,
                "content_hash": content_hash,
                "cached_at": time.time(),
                "file_path": str(file_path),
                "analysis": analysis,
            }

            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(cache_data, f, indent=2)

        except OSError:
            # Ignore cache write failures
            pass

    def clear(self) -> None:
        """Clear all cached data."""
        if self.cache_dir.exists():
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink(missing_ok=True)
        self.stats = {"hits": 0, "misses": 0, "invalidations": 0}

    def get_stats(self) -> Dict[str, int]:
        """Get cache performance statistics."""
        total = self.stats["hits"] + self.stats["misses"]
        hit_rate = (self.stats["hits"] / total * 100) if total > 0 else 0

        return {
            **self.stats,
            "total_requests": total,
            "hit_rate_percent": round(hit_rate, 1),
        }
