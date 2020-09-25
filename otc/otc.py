"""OT protocol functionalities.
Oblivious transfer (OT) communications protocol message/response
functionality implementations based on Ed25519 primitives.
"""

import doctest
import nacl.encoding
import nacl.hash
import nacl.secret
import nacl.bindings
import oblivious

def _hash(bs):
    """
    Generic hash function for hashing keys.
    """
    return nacl.hash.blake2b(bytes(bs), encoder=nacl.encoding.RawEncoder)

class common(): # pylint: disable=R0903
    """
    Wrapper class for an object that maintains a party's
    state.
    """
    def __init__(self):
        self.secret = oblivious.rnd() # Secret key: x in Z/pZ.
        self.public = oblivious.bas(self.secret) # Public key: X = g^x.

class receive(common):
    """
    Wrapper class for an object that maintains the receiving
    party's state and builds receiver requests/responses.
    >>> r = receive()
    >>> (len(r.secret), len(r.public))
    (32, 32)
    """
    def query(self, send_public, bit):
        """
        Build the initial query for two data messages
        from which to choose upon receipt.
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
        g_to_a = send_public

        # Below is the receiver's public key g^b.
        g_to_b = self.public

        # If receiver's election bit is 0, B = g^b.
        # If receiver's election bit is 1, B = A * g^b.
        B_s0 = g_to_b # pylint: disable=C0103
        B_s1 = oblivious.add(g_to_a, g_to_b) # pylint: disable=C0103

        return B_s0 if bit == 0 else B_s1

    def elect(self, send_public, bit, data_zero, data_one):
        """
        Choose from the two supplied data messages, decrypting
        the one that was chosen at the time of the query.
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
        b = self.secret

        # This is the sender's public key A = g^a.
        g_to_a = send_public

        # Build the decryption key g^(ab).
        k_s = _hash(oblivious.mul(b, g_to_a))

        # Decryption and decoding function.
        dec = lambda c, k: nacl.secret.SecretBox(k).decrypt(bytes(24) + c)

        # Decrypt the chosen message.
        return dec(data_zero if bit == 0 else data_one, k_s)

class send(common): # pylint: disable=R0903
    """
    Wrapper class for an object that maintains the sending
    party's state and builds sender requests/responses.
    >>> s = send()
    >>> (len(s.secret), len(s.public))
    (32, 32)
    """
    def reply(self, receive_public, data_zero, data_one):
        """
        Build the reply (the two data messages) that should
        be sent in reply to a query.
        >>> (s, r) = (send(), receive())
        >>> req = r.query(s.public, 0)
        >>> rsp = s.reply(r.public, [123],  'abc')
        Traceback (most recent call last):
          ...
        TypeError: each message must be a bytes-like object
        >>> rsp = s.reply(r.public, bytes([123]),  bytes([234]))
        Traceback (most recent call last):
          ...
        ValueError: each message must be of length 16
        """
        if not isinstance(data_zero, (bytes, bytearray)) or\
           not isinstance(data_one, (bytes, bytearray)):
            raise TypeError('each message must be a bytes-like object')
        if len(data_zero) != 16 or len(data_zero) != 16:
            raise ValueError('each message must be of length 16')

        # These are the sender's secret and public keys.
        a = self.secret
        g_to_a = self.public

        # Second argument is receiver's public key B_s, which depends on
        # the receiver's election bit s and is B_0 = g^b or B_1 = A * g^b.
        B_s = receive_public # pylint: disable=C0103

        # Build the key for the message for the zero case.
        k_0 = _hash(oblivious.mul(a, B_s))

        # Build the key for the message for the one case.
        k_1 = _hash(oblivious.mul(a, oblivious.sub(B_s, g_to_a)))

        # Encrypt the messages for both cases.
        nonce = bytes([0]*nacl.bindings.crypto_secretbox_NONCEBYTES)

        # Encryption and encoding function.
        enc = lambda m, nonce, k: nacl.secret.SecretBox(k).encrypt(m, nonce)[-32:]

        # Encrypt the two messages.
        return (enc(data_zero, nonce, k_0), enc(data_one, nonce, k_1))

if __name__ == "__main__":
    doctest.testmod() # pragma: no cover
