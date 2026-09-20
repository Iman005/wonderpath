"""
IIdentityResolver — abstraction over "who is making this request".

The MVP implementation (DeviceIdentityResolver) resolves an anonymous
device UUID from a request header/cookie. A future real-auth
implementation (JWT/OIDC) can replace it without touching any other
module, since every other module only depends on this interface's
`resolve()` contract.
"""
from abc import ABC, abstractmethod


class IIdentityResolver(ABC):
    @abstractmethod
    def resolve(self) -> str:
        """Return the current owner identity string (e.g. device id)."""
        raise NotImplementedError
