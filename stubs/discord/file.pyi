from typing import Union, Optional, BinaryIO


class File:
    fp: Union[str, BinaryIO]
    filename: Optional[str]

    def __init__(self, fp: Union[str, BinaryIO], filename: Optional[str] = ...) -> None: ...

    def open_file(self) -> Union[str, BinaryIO]: ...

    def close(self) -> None: ...
