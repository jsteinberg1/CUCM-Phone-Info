import os
import uvicorn
from api.Config import config

cert_key = os.path.join(config.certs_folder,"server.key")
cert_file = os.path.join(config.certs_folder,"server.pem")

from OpenSSL import crypto, SSL
   
def create_self_signed_cert():    
    # cert private key doesn't exist, create new key
    #can look at generated file using openssl:
    #openssl x509 -inform pem -in selfsigned.crt -noout -text
    # create a key pair
    k = crypto.PKey()
    k.generate_key(crypto.TYPE_RSA, 4096)
    # create a self-signed cert
    cert = crypto.X509()
    cert.get_subject().CN = "cucmphoneinfo"
    cert.set_serial_number(0)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(10*365*24*60*60)
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(k)
    cert.sign(k, 'sha512')
    with open(cert_file, "wt") as f:
        f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert).decode("utf-8"))
    with open(cert_key, "wt") as f:
        f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k).decode("utf-8"))


if __name__ == "__main__":  
    log_level = os.getenv('LOG_LEVEL')
    reload_state = False

    if not os.path.exists(cert_key):
        create_self_signed_cert()
        
    uvicorn.run(
        "api.Main:api", 
        host="0.0.0.0", 
        port=8080, 
        log_level=log_level, 
        reload=reload_state, 
        ssl_keyfile=cert_key,
        ssl_certfile=cert_file
    )