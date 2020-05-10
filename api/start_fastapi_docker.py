import os
import logging
import uvicorn
from OpenSSL import crypto, SSL

def create_self_signed_cert(cert_key: str, cert_file: str):
    """Create new self signed certificate for use by Uvicorn  HTTPS

    Arguments:
        cert_key {str} -- full path of certificate private key
        cert_file {str} -- full path of certificate file
    """
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
        print(f"Created new SSL certificate {cert_file}")
    with open(cert_key, "wt") as f:
        f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k).decode("utf-8"))
        print(f"Created new SSL private key {cert_key}")


def check_if_https_cert_exists(cert_key: str, cert_file: str):
    """Check if SSL certificate already exists, if not call 
    create_self_signed_cert to create new self signed certificate

    Arguments:
        cert_key {str} -- full path of certificate private key
        cert_file {str} -- full path of certificate file
    """
    if not os.path.exists(cert_key):
        print("SSL key doesn't exist, creating new self signed certificate.")
        try:
            os.makedirs(os.path.dirname(cert_key))
            print("Created cert directories")
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
        else:
            create_self_signed_cert(cert_key, cert_file)


if __name__ == "__main__":  
    log_level = os.getenv('LOG_LEVEL') # log level supplied as environment variable in docker-fastapi-variables.env
    reload_state = False

    # Deal with HTTP certificate
    cert_key = "/fastapi/data/certs/server.key"
    cert_file = "/fastapi/data/certs/server.pem"
    check_if_https_cert_exists(cert_key=cert_key, cert_file=cert_file)
        
    # run uvicorn / fast api application
    uvicorn.run(
        "api.Main:api", 
        host="0.0.0.0", 
        port=8080, 
        log_level=log_level, 
        reload=reload_state, 
        ssl_keyfile=cert_key,
        ssl_certfile=cert_file
    )