import hashlib

if __name__ == '__main__':
    HWID = input("Enter your HWID: ")

    cut_HWID = HWID[0:0x10]
    assert len(cut_HWID) == 0x10

    result = hashlib.md5(cut_HWID.encode())
    print(result.digest()[::-1].hex())


