import os
import requests
import ecdsa
import hashlib
import base58

def generate_private_key():
    return os.urandom(32).hex()

def private_to_public(private_key_hex):
    sk = ecdsa.SigningKey.from_string(bytes.fromhex(private_key_hex), curve=ecdsa.SECP256k1)
    vk = sk.verifying_key
    public_key_bytes = b'\x04' + vk.to_string()
    return public_key_bytes.hex()

def public_to_address(public_key_hex):
    public_key_bytes = bytes.fromhex(public_key_hex)
    sha256 = hashlib.sha256(public_key_bytes).digest()
    ripemd160 = hashlib.new('ripemd160', sha256).digest()
    prefixed = b'\x00' + ripemd160
    checksum = hashlib.sha256(hashlib.sha256(prefixed).digest()).digest()[:4]
    binary_address = prefixed + checksum
    return base58.b58encode(binary_address).decode()

def private_to_wif(private_key_hex):
    extended_key = b'\x80' + bytes.fromhex(private_key_hex)
    checksum = hashlib.sha256(hashlib.sha256(extended_key).digest()).digest()[:4]
    final_key = extended_key + checksum
    return base58.b58encode(final_key).decode()

def check_balance(address):
    try:
        url = f"https://blockstream.info/api/address/{address}"
        response = requests.get(url)
        if response.status_code != 200:
            return -1
        data = response.json()
        return data['chain_stats']['funded_txo_sum'] - data['chain_stats']['spent_txo_sum']
    except:
        return -1

while True:
    priv = generate_private_key()
    pub = private_to_public(priv)
    addr = public_to_address(pub)
    wif = private_to_wif(priv)

    balance = check_balance(addr)

    if balance > 0:
        print("\n=== FOUND WALLET WITH BALANCE ===")
        print("Address :", addr)
        print("WIF     :", wif)
        print("Balance :", balance / 100000000, "BTC")
        break
      
