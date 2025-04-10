sudo iptables -F PREROUTING -t nat
sudo rm -rf mitmproxy-ca.pem
sudo rm -rf server.pem
sudo rm -rf certCA.pem
