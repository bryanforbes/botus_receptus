from typing import Union, Optional, BinaryIO


class AudioSource:
    def read(self) -> bytes: ...

    def is_opus(self) -> bool: ...

    def cleanup(self) -> None: ...

    def __del__(self) -> None: ...


class PCMAudio(AudioSource):
    def __init__(self, stream) -> None: ...


class FFmpegPCMAudio(AudioSource):
    def __init__(self, source: Union[str, BinaryIO], *, executable: str = ..., pipe: bool = ...,
                 stderr: Optional[BinaryIO] = ..., options: Optional[str] = ...,
                 before_options: Optional[str] = ...) -> None: ...


class PCMVolumeTransformer(AudioSource):
    volume: float

    def __init__(self, original: AudioSource, volume: float = ...) -> None: ...
