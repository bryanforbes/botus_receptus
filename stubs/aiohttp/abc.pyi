from typing import Sized, Iterable, Iterator, Mapping, Optional
from http.cookies import SimpleCookie


class AbstractCookieJar(Sized, Iterable[SimpleCookie]):
    def __len__(self) -> int: ...

    def __iter__(self) -> Iterator[SimpleCookie]: ...

    def update_cookies(self, cookies: Mapping[str, str],
                       response_url: Optional[str] = ...) -> None: ...

    def filter_cookies(self,
                       response_url: str) -> SimpleCookie: ...
