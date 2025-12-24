from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from enum import Enum


class NewsSource(Enum):
    GOOGLE_NEWS = "google_news"
    NAVER_NEWS = "naver_news"


class TTSProvider(Enum):
    TYPECAST = "typecast"
    EDGE = "edge"


class UploadPrivacy(Enum):
    PUBLIC = "public"
    UNLISTED = "unlisted"
    PRIVATE = "private"


@dataclass
class NewsItem:
    title: str
    summary: str
    url: str
    source: NewsSource
    source_name: str
    published_at: Optional[datetime] = None
    image_url: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "summary": self.summary,
            "url": self.url,
            "source": self.source.value,
            "source_name": self.source_name,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "image_url": self.image_url,
        }


@dataclass
class SelectedNews:
    news_item: NewsItem
    selection_reason: str
    hook_idea: str
    
    def to_dict(self) -> dict:
        return {
            "news": self.news_item.to_dict(),
            "selection_reason": self.selection_reason,
            "hook_idea": self.hook_idea,
        }


@dataclass
class Script:
    title: str
    hook: str
    body: str
    outro: str
    full_script: str
    keywords: list[str]
    hashtags: list[str]
    description: str
    
    @property
    def character_count(self) -> int:
        return len(self.full_script)
    
    @property
    def estimated_duration(self) -> float:
        return len(self.full_script) / 350 * 60
    
    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "hook": self.hook,
            "body": self.body,
            "outro": self.outro,
            "full_script": self.full_script,
            "keywords": self.keywords,
            "hashtags": self.hashtags,
            "description": self.description,
            "character_count": self.character_count,
            "estimated_duration": self.estimated_duration,
        }


@dataclass
class TTSConfig:
    voice_id: str
    style: str = "news"
    emotion: str = "neutral"
    speed: float = 1.0
    pitch: float = 0.0


@dataclass
class TTSResult:
    audio_path: str
    duration: float
    character_count: int
    provider: TTSProvider


@dataclass
class MediaAsset:
    file_path: str
    media_type: str
    source_url: str
    keyword: str
    duration: Optional[float] = None
    width: Optional[int] = None
    height: Optional[int] = None


@dataclass
class ShortsVideo:
    script: Script
    audio_path: str
    video_path: str
    thumbnail_path: Optional[str] = None
    duration: float = 0.0
    file_size_mb: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict:
        return {
            "script": self.script.to_dict(),
            "audio_path": self.audio_path,
            "video_path": self.video_path,
            "thumbnail_path": self.thumbnail_path,
            "duration": self.duration,
            "file_size_mb": self.file_size_mb,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class UploadResult:
    video_id: str
    video_url: str
    title: str
    privacy: UploadPrivacy
    uploaded_at: datetime = field(default_factory=datetime.now)
    success: bool = True
    error_message: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "video_id": self.video_id,
            "video_url": self.video_url,
            "title": self.title,
            "privacy": self.privacy.value,
            "uploaded_at": self.uploaded_at.isoformat(),
            "success": self.success,
            "error_message": self.error_message,
        }


@dataclass
class PipelineResult:
    shorts_videos: list[ShortsVideo] = field(default_factory=list)
    upload_results: list[UploadResult] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.now)
    finished_at: Optional[datetime] = None
    success: bool = True
    errors: list[str] = field(default_factory=list)
    
    @property
    def duration(self) -> float:
        if self.finished_at:
            return (self.finished_at - self.started_at).total_seconds()
        return 0.0
    
    def to_dict(self) -> dict:
        return {
            "shorts_count": len(self.shorts_videos),
            "upload_count": len(self.upload_results),
            "started_at": self.started_at.isoformat(),
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
            "duration_seconds": self.duration,
            "success": self.success,
            "errors": self.errors,
        }
