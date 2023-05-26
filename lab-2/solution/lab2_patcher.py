with open('hack_app', 'rb') as f:
    data = f.read()

patched_data = data[:5534] + (116).to_bytes(1, 'little') + data[5534+1:]

with open('patched_hack_app', 'wb+') as f:
    f.write(patched_data)
