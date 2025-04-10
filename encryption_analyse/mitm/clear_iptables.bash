# set iptables rules
# flush rules of wireless card
sudo iptables -F PREROUTING -t nat
sudo iptables -F OUTPUT -t nat
sudo iptables -t filter -F
sudo iptables -t nat -F
sudo iptables -t mangle -F
sudo iptables -t raw -F
sudo iptables -t security -F
sudo iptables -X
sudo iptables -P INPUT ACCEPT
sudo iptables -P FORWARD ACCEPT
sudo iptables -P OUTPUT ACCEPT
sudo iptables -t nat -P PREROUTING ACCEPT
sudo iptables -t nat -P OUTPUT ACCEPT
sudo iptables -t nat -P POSTROUTING ACCEPT
sudo sysctl -w net.ipv4.ip_forward=0
