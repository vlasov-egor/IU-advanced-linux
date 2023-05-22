orig_file = open('hack_app', 'rb')
orig = orig_file.read()
orig_file.close()

patched = orig[:5534] + (116).to_bytes(1, 'little') + orig[5534+1:]

patched_file = open('hack_app.patched', 'wb+')
patched_file.write(patched)
patched_file.flush()
patched_file.close()
