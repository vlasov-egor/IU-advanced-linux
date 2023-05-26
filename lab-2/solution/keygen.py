import hashlib

HWID = input("Enter your HWID: ")
result = hashlib.md5(HWID[0:0x10].encode())
print(result.digest()[::-1].hex())
