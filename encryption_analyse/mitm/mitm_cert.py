from mitmproxy import certs
 
for path in certs.cert_paths():
    print(path)
 
with open(path, 'rb') as f:
    cert_bytes = f.read()
    cert = certs.load_certificate(cert_bytes)
    print(cert.get_subject())