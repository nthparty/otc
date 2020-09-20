"""OT protocol functionalities.
Oblivious transfer (OT) protocol message/response functionality
implementations based on Ed25519 primitives.
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

class common():
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
    """
    def query(self, send_public, bit):
        """
        Build the initial query for two data messages
        from which to choose upon receipt.
        """
        if not isinstance(bit, int):
            raise TypeError('selection bit must be an integer')
        if not bit in [0, 1]:
            raise ValueError('selection bit must be 0 or 1')

        # The sender's public key is A = g^a.
        g_to_a = send_public

        # Below is the receiver's public key g^b.
        g_to_b = self.public

        # If receiver's selection bit is 0, B = g^b.
        # If receiver's selection bit is 1, B = A * g^b.
        B_s0 = g_to_b
        B_s1 = oblivious.add(g_to_a, g_to_b)

        return B_s0 if bit == 0 else B_s1

    def elect(self, send_public, bit, data_zero, data_one):
        """
        Choose from the two supplied data messages, decrypting
        the one that was chosen at the time of the query.
        """
        if not isinstance(bit, int):
            raise TypeError('selection bit must be an integer')
        if not bit in [0, 1]:
            raise ValueError('selection bit must be 0 or 1')

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

class send(common):
    """
    Wrapper class for an object that maintains the sending
    party's state and builds sender requests/responses.
    """
    def reply(self, receive_public, data_zero, data_one):
        """
        Build the reply (the two data messages) that should
        be sent in reply to a query.
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
        # the receiver's selection bit s and is B_0 = g^b or B_1 = A * g^b.
        B_s = receive_public

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
    doctest.testmod()
