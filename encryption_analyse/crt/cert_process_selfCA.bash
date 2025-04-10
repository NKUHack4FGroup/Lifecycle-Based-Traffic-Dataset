#!/bin/bash

# cert.pem path
CERT_PATH="/home/sider/Desktop/Data/cert/" 

# 转换证书格式的脚本路径
CERT_TO_PEM_SCRIPT="./cert_to_pem.sh"

# Python脚本路径
PYTHON_CA="./cert_build_command.py"
PYTHON_CUSTOM="./cert_building_as_custom.py"

# 设置MITM
MITM_PATH="/home/sider/Desktop/scripts/mitm/"

# 转换证书格式
if [ -f "$CERT_TO_PEM_SCRIPT" ]; then
    bash "$CERT_TO_PEM_SCRIPT"
else
    echo "can't find cert_to_pem.sh"
    exit 1
fi

# Show menu for user to select the mitmproxy mode
echo "Select the mitmproxy mode:"
echo "1) With a CA certificate"
echo "2) With custom certificate"
read -p "Enter your choice [1-2]: " choice

case $choice in
    1)
        # 检查cert.pem文件是否存在
        if [ -f "${CERT_PATH}cert.pem" ]; then
            # 执行Python脚本
            python3 "$PYTHON_CA" -p "${CERT_PATH}cert.pem" --use-self-issuer -s "${CERT_PATH}cert_new.pem"
        else
            echo "can't cert.pem"
            exit 1
        fi
        ;;
    2)
        # 检查cert.pem文件是否存在
        if [ -f "${CERT_PATH}cert.pem" ]; then
            # 执行Python脚本
            python3 "$PYTHON_CUSTOM" -p "${CERT_PATH}cert.pem" --use-self-issuer -s "${CERT_PATH}cert_new.pem"
        else
            echo "can't cert.pem"
            exit 1
        fi
        ;;
    *)
        echo "Invalid choice, exiting..."
        exit 1
        ;;
esac


# 合并私钥和新证书文件
cat "${CERT_PATH}new_private.key" "${CERT_PATH}cert_new.pem" > "${CERT_PATH}certCA.pem"

# 复制合并后的文件到指定路径
cp "${CERT_PATH}certCA.pem" "${MITM_PATH}certCA.pem"

# 输出最终文件的位置
echo "Combined file certCA.pem has been copied to: $MITM_PATH"


