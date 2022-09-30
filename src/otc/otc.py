"""
Oblivious transfer (OT) communications protocol message/response functionality
implementations based on `Curve25519 <https://cr.yp.to/ecdh.html>`__ and the
`Ristretto <https://ristretto.group>`__ group.
"""

from __future__ import annotations
from typing import Tuple, Union
import doctest
import hashlib
import bcl
import oblivious

def _hash(bs: bytes) -> bytes:
    """
    Generic hash function for hashing keys.
    """
    return hashlib.sha256(bs).digest()

class common:
    """
    Wrapper class for an object that maintains a party's
    state.
    """
    def __init__(self: common):
        # Secret key: x in Z/pZ.
        self.secret = oblivious.ristretto.scalar.random()

        # Public key: X = g^x.
        self.public = oblivious.ristretto.point.base(self.secret)

class receive(common):
    """
    Wrapper class for an object that maintains the receiving party's state and
    builds receiver requests/responses.

    >>> r = receive()
    >>> (len(r.secret), len(r.public))
    (32, 32)
    """
    def query(
            self: receive,
            send_public: oblivious.ristretto.point,
            bit: int
        ) -> oblivious.ristretto.point:
        """
        Build the initial query for two data messages (from which one must be
        chosen upon receipt).

        :param send_public: Public key obtained from sender.
        :param bit: Index (``0`` or ``1``) indicating choice of message to
            receive.

        >>> (s, r) = (send(), receive())
        >>> req = r.query(s.public, 'abc')
        Traceback (most recent call last):
          ...
        TypeError: election bit must be an integer
        >>> req = r.query(s.public, 3)
        Traceback (most recent call last):
          ...
        ValueError: election bit must be 0 or 1
        """
        if not isinstance(bit, int):
            raise TypeError('election bit must be an integer')

        if not bit in [0, 1]:
            raise ValueError('election bit must be 0 or 1')

        # The sender's public key is A = g^a.
        g_to_a: oblivious.ristretto.point = send_public

        # Below is the receiver's public key g^b.
        g_to_b: oblivious.ristretto.point = self.public

        # Return B, where:
        # * if receiver's election bit is 0, B = g^b, and
        # * if receiver's election bit is 1, B = A * g^b.
        return g_to_b if bit == 0 else g_to_a + g_to_b

    def elect(
            self: receive,
            send_public: oblivious.ristretto.point,
            bit: int,
            data_zero: Union[bytes, bytearray],
            data_one: Union[bytes, bytearray]
        ) -> bytes:
        """
        Choose from the two supplied data messages, decrypting the one that was
        chosen at the time of the query.

        :param send_public: Public key obtained from sender.
        :param bit: Index (``0`` or ``1``) indicating choice of message to
            receive.
        :param data_zero: Ciphertext corresponding to first message
            (*i.e.*, at index ``0``) from sender.
        :param data_one: Ciphertext corresponding to second message
            (*i.e.*, at index ``1``) from sender.

        >>> (s, r) = (send(), receive())
        >>> r_public = r.query(s.public, 0)
        >>> messages = s.reply(r_public, bytes([123]*16),  bytes([234]*16))
        >>> [n for n in r.elect(s.public, 0, *messages)] == ([123]*16)
        True
        >>> (s, r) = (send(), receive())
        >>> r_public = r.query(s.public, 1)
        >>> messages = s.reply(r_public, bytes([123]*16), bytes([234]*16))
        >>> [n for n in r.elect(s.public, 1, *messages)] == ([234]*16)
        True

        The election bit must be either the integer ``0`` or the integer ``1``.

        >>> r.elect(s.public, 'abc', *messages)
        Traceback (most recent call last):
          ...
        TypeError: election bit must be an integer
        >>> r.elect(s.public, 3, *messages)
        Traceback (most recent call last):
          ...
        ValueError: election bit must be 0 or 1
        """
        if not isinstance(bit, int):
            raise TypeError('election bit must be an integer')

        if not bit in [0, 1]:
            raise ValueError('election bit must be 0 or 1')

        # This is the receiver's secret key b.
        b: oblivious.ristretto.scalar = self.secret

        # This is the sender's public key A = g^a.
        g_to_a: oblivious.ristretto.point = send_public

        # Build the decryption key g^(ab).
        k_s = bcl.secret(_hash(b * g_to_a))

        # Decryption and decoding function.
        dec = lambda c, k: bcl.symmetric.decrypt(k, bcl.cipher(bytes(24) + c))

        # Decrypt the chosen message.
        return dec(data_zero if bit == 0 else data_one, k_s)

class send(common):
    """
    Wrapper class for an object that maintains the sending party's state and
    builds sender requests/responses.

    >>> s = send()
    >>> (len(s.secret), len(s.public))
    (32, 32)
    """
    def reply(
            self: send,
            receive_public: oblivious.ristretto.point,
            data_zero: Union[bytes, bytearray],
            data_one: Union[bytes, bytearray]
        ) -> Tuple[bcl.cipher, bcl.cipher]:
        """
        Build the response (the two data messages) that should be sent in reply
        to a query.

        :param receive_public: Public key obtained from receiver.
        :param data_zero: First message (*i.e.*, at index ``0``) of the two
            from which the receiver must choose.
        :param data_one: Second message (*i.e.*, at index ``1``) of the two
            from which the receiver must choose.

        >>> (s, r) = (send(), receive())
        >>> req = r.query(s.public, 0)

        Messages must be bytes-like objects that have length exactly ``16``.

        >>> rsp = s.reply(r.public, [123],  'abc')
        Traceback (most recent call last):
          ...
        TypeError: each message must be a bytes-like object
        >>> rsp = s.reply(r.public, bytes([123]),  bytes([234]))
        Traceback (most recent call last):
          ...
        ValueError: each message must be of length 16
        """
        if (
            not isinstance(data_zero, (bytes, bytearray)) or
            not isinstance(data_one, (bytes, bytearray))
        ):
            raise TypeError('each message must be a bytes-like object')

        if len(data_zero) != 16 or len(data_zero) != 16:
            raise ValueError('each message must be of length 16')

        # These are the sender's secret and public keys.
        a: oblivious.ristretto.scalar = self.secret
        g_to_a: oblivious.ristretto.point = self.public

        # Second argument is receiver's public key B_s, which depends on
        # the receiver's election bit s and is B_0 = g^b or B_1 = A * g^b.
        B_s: oblivious.ristretto.point = receive_public # pylint: disable=invalid-name

        # Build the key for the message for the zero case.
        k_0 = bcl.secret(_hash(a * B_s))

        # Build the key for the message for the one case.
        k_1 = bcl.secret(_hash(a * (B_s - g_to_a)))

        # Encryption and encoding function.
        enc = lambda m, k: (
            bcl.symmetric.encrypt(k, m, bcl.nonce(bcl.nonce.length))[-32:]
        )

        # Encrypt the two messages.
        return (enc(data_zero, k_0), enc(data_one, k_1))

if __name__ == '__main__':
    doctest.testmod() # pragma: no cover
