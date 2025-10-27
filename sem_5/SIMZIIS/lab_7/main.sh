openssl req -x509 -newkey rsa:2048 -keyout key_selfsigned.key -out cert_selfsigned.crt -sha256 -days 365 -nodes
openssl x509 -in cert_selfsigned.crt -text -noout