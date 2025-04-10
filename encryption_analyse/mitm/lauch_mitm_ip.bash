#!/bin/bash
WIRELESS_CARD="wlxc01c30151c62"
# WIRELESS_CARD="wlxaca2132ab4a7"

while getopts ":s:" opt; do
  case $opt in
    s)
      IP_HOST=$OPTARG
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      exit 1
      ;;
    :)
      echo "Option -$OPTARG requires an argument." >&2
      exit 1
      ;;
  esac
done

if [ -z "$IP_HOST" ]; then
  echo "Usage: $0 -s <IP_HOST>"
  exit 1
fi


sudo sysctl -w net.ipv4.ip_forward=1
sudo sysctl -w net.ipv4.conf.all.send_redirects=0


# set iptables rules
# flush rules of wireless card
sudo iptables -t nat -F PREROUTING 

# sudo iptables -t nat -A PREROUTING -i $WIRELESS_CARD -p tcp --dport 80 -j REDIRECT --to-port 8080
sudo iptables -t nat -A PREROUTING -i $WIRELESS_CARD -p tcp -d $IP_HOST --dport 443 -j REDIRECT --to-port 8080
# sudo iptables -t nat -A PREROUTING -i $WIRELESS_CARD -p tcp --dport 8883 -j REDIRECT --to-port 8080
sudo iptables -t nat -A PREROUTING -i $WIRELESS_CARD -p tcp -d $IP_HOST --dport 1884 -j REDIRECT --to-port 8080
sudo iptables -t nat -A PREROUTING -i $WIRELESS_CARD -p tcp -d $IP_HOST --dport 30521 -j REDIRECT --to-port 8080

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
