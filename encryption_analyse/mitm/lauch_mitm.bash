#!/bin/bash
WIRELESS_CARD="wlx0c82682f6f1e"
# WIRELESS_CARD="wlxaca2132ab4a7"


sudo sysctl -w net.ipv4.ip_forward=1
sudo sysctl -w net.ipv4.conf.all.send_redirects=0


# set iptables rules
# flush rules of wireless card
sudo iptables -t nat -F PREROUTING 

# The IP address is denied
# sudo iptables -t nat -A PREROUTING -i $WIRELESS_CARD -p tcp --dport 60443 -d 146.56.253.30  -j RETURN
# sudo iptables -t nat -A PREROUTING -i $WIRELESS_CARD -p tcp --dport 443 -d 47.111.40.241 -j RETURN
# sudo iptables -t nat -A PREROUTING -i $WIRELESS_CARD -p tcp --dport 443 -d 111.63.147.168 -j RETURN

# Allow IP to pass through

#sudo iptables -t nat -A PREROUTING -i $WIRELESS_CARD -p tcp -d  --dport 8883 -j REDIRECT --to-port 8080


sudo iptables -t nat -A PREROUTING -i $WIRELESS_CARD -p tcp -d 120.24.189.144 --dport 443 -j REDIRECT --to-port 8080
sudo iptables -t nat -A PREROUTING -i $WIRELESS_CARD -p tcp -d 113.240.127.19 --dport 443 -j REDIRECT --to-port 8080

#sudo iptables -t nat -A PREROUTING -i $WIRELESS_CARD -p tcp -d 221.181.52.63 --dport 443 -j REDIRECT --to-port 8080
# sudo iptables -t nat -A PREROUTING -i $WIRELESS_CARD -p tcp -d 47.98.0.183 --dport 443 -j REDIRECT --to-port 8080
# sudo iptables -t nat -A PREROUTING -i $WIRELESS_CARD -p tcp -d 47.114.236.50 --dport 443 -j REDIRECT --to-port 8080
# sudo iptables -t nat -A PREROUTING -i $WIRELESS_CARD -p tcp -d 47.97.242.6 --dport 443 -j REDIRECT --to-port 8080



# sudo iptables -t nat -A PREROUTING -i $WIRELESS_CARD -p tcp --dport 80 -j REDIRECT --to-port 8080
# sudo iptables -t nat -A PREROUTING -i $WIRELESS_CARD -p tcp --dport 443 -j REDIRECT --to-port 8080
# sudo iptables -t nat -A PREROUTING -i $WIRELESS_CARD -p tcp --dport 8883 -j REDIRECT --to-port 8080
# sudo iptables -t nat -A PREROUTING -i $WIRELESS_CARD -p tcp --dport 1884 -j REDIRECT --to-port 8080

# sudo iptables -t nat -A PREROUTING -i $WIRELESS_CARD -p tcp --dport 443 -j RETURN

# launch mitmproxy on transparent mode
# Show menu for user to select the mitmproxy mode
echo "Select the mitmproxy mode:"
echo "1) With a CA certificate"
echo "2) With custom certificate"
read -p "Enter your choice [1-2]: " choice

case $choice in
    1)
        echo "Starting mitmproxy without custom certificate..."
        cp ./certCA.pem ./mitmproxy-ca.pem
        mitmproxy --mode transparent --showhost --ssl-insecure --set confdir=./ --tcp-host '.*' -p 8080
        ;;
    2)
        echo "Starting mitmproxy with custom certificate..."
        cp ./certCA.pem ./server.pem
        mitmproxy --mode transparent --showhost --ssl-insecure --certs ./server.pem --tcp-host '.*' -p 8080
        ;;
    *)
        echo "Invalid choice, exiting..."
        exit 1
        ;;
esac
