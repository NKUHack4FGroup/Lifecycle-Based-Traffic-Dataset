import os
import argparse
from cryptography.x509 import Extension, KeyUsage, BasicConstraints
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.x509.oid import NameOID
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import ec


def generate_certificate(original_cert_path, use_original_issuer, use_self_issuer, save_path):
    # ------------ 读取原始证书文件 ------------ #
    with open(original_cert_path, 'rb') as f:
        original_cert_data = f.read()
    # 解析原证书，并存储original_cert
    original_cert = x509.load_pem_x509_certificate(original_cert_data)

    # ------------ 创建新的RSA密钥对 ------------ #
    # 从 save_path 获取目录和文件名前缀
    save_dir, cert_filename = os.path.split(save_path)
    # 提取原证书信息
    original_public_key = original_cert.public_key()
    if isinstance(original_public_key, rsa.RSAPublicKey):
        key_size = original_public_key.key_size
        public_exponent = original_public_key.public_numbers().e
        print(f"Use the same rsa parameters as the original certificate："
              f"key_size={key_size}, public_exponent={public_exponent}")
        if key_size != 2048:
            print("the key_size invalid, use 2048")
        new_private_key = rsa.generate_private_key(
            public_exponent=public_exponent,
            key_size=2048
        )
    elif isinstance(original_public_key, ec.EllipticCurvePublicKey):
        curve = original_public_key.curve
        new_private_key = ec.generate_private_key(curve, default_backend())
        print("Use the same EC parameters as the original certificate")
    else:
        print("Unknown key parameters. Use default key parameters, public_exponent=65537, key_size=2048")
        new_private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
    # 按照标准格式存储私钥
    private_key_path = os.path.join(save_dir, "new_private.key")
    with open(private_key_path, "wb") as f:
        f.write(new_private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))
    print(f"new private key has been established at {private_key_path}")
    # 创建新的公钥并存储
    new_public_key = new_private_key.public_key()
    public_key_path = os.path.join(save_dir, "new_public.key")
    with open(public_key_path, "wb") as f:
        f.write(new_public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))
    print(f"New public key has been established at {public_key_path}")

    # ------------------- 证书构建 --------------------- #
    # 创建一个新的证书构建器
    builder = x509.CertificateBuilder()
    # 主题信息
    builder = builder.subject_name(original_cert.subject)
    # builder = builder.issuer_name(original_cert.issuer)
    # 颁发者信息
    if use_original_issuer:
        builder = builder.issuer_name(original_cert.issuer)
    elif use_self_issuer:
        new_issuer_name = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "CN"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "TJ"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "JN"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "NKU626"),
            x509.NameAttribute(NameOID.COMMON_NAME, "NkU626 Root CA"),
        ])
        builder = builder.issuer_name(new_issuer_name)
    # 有效期信息
    builder = builder.not_valid_before(original_cert.not_valid_before)
    builder = builder.not_valid_after(original_cert.not_valid_after)
    # 序列号
    if original_cert.serial_number != 0x00:
        builder = builder.serial_number(original_cert.serial_number)
    else:
        builder = builder.serial_number(1)
        print("the serial number invalid, skip this field")
    # 使用新的公钥替换原证书公钥
    builder = builder.public_key(new_public_key)

    # 添加证书的扩展信息
    has_key_usage_extension = False  # 检查原始证书是否已经包含 Key Usage 扩展信息
    has_basic_constraints_extension = False   # 检查原始证书是否已经包含 Basic Constraints 扩展信息
    for extension in original_cert.extensions:
        if isinstance(extension.value, KeyUsage):
            has_key_usage_extension = True
            print("Key usage extension is " + str(has_key_usage_extension))
        elif isinstance(extension.value, BasicConstraints):
            has_basic_constraints_extension = True
            print("basic constraints extension is " + str(has_basic_constraints_extension))
            if not extension.value.ca:
                builder = builder.add_extension(
                    x509.BasicConstraints(ca=True, path_length=None),
                    critical=True
                )
                print("Modified Basic Constraints extension: ca=True")
                continue
        builder = builder.add_extension(extension.value, extension.critical)
    # 如果原始证书中没有 Key Usage 扩展信息，则添加
    if not has_key_usage_extension:
        builder = builder.add_extension(
            x509.KeyUsage(
                digital_signature=False,
                content_commitment=False,
                key_encipherment=False,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=True,
                crl_sign=False,
                encipher_only=False,
                decipher_only=False
            ),
            critical=True
        )
    # 如果原始证书中没有 Basic Constraints 扩展信息，则添加
    if not has_basic_constraints_extension:
        builder = builder.add_extension(
            x509.BasicConstraints(ca=True, path_length=None),
            critical=True
        )

    signature_algorithm = original_cert.signature_algorithm_oid
    print("signature_algorithm:", original_cert.signature_algorithm_oid._name)
    print("signature_hash_algorithm:", original_cert.signature_hash_algorithm.name)

    # --------------- 签发新的证书 --------------- #
    if 'sha256' in original_cert.signature_hash_algorithm.name:
        print("use sha256 with original cert")
        new_cert = builder.sign(
            private_key=new_private_key, algorithm=hashes.SHA256()
        )
    elif 'sha1' in original_cert.signature_hash_algorithm.name:
        print("sha1 signature hash algorithm not supported, using SHA256")
        new_cert = builder.sign(
            private_key=new_private_key, algorithm=hashes.SHA256()
        )
    elif 'sha384' in original_cert.signature_hash_algorithm.name:
        print("use sha384 with original cert")
        new_cert = builder.sign(
            private_key=new_private_key, algorithm=hashes.SHA384()
        )
    else:
        new_cert = 0

    if new_cert != 0:
        # 将新证书保存到文件中
        with open(save_path, 'wb') as f:
            f.write(new_cert.public_bytes(serialization.Encoding.PEM))
        print("newcert has been established")
    else:
        print("unknown signature algorithm")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--path", help="Path to cert.pem file", required=True)
    parser.add_argument("-s", "--save-path", help="Path to save the new certificate", default='new_cert.pem')

    # 使用互斥组保证 use-original-issuer 和 use-self-issuer 不会同时被指定
    issuer_group = parser.add_mutually_exclusive_group(required=True)
    issuer_group.add_argument("--use-original-issuer", help="Use original issuer of the certificate",
                              action="store_true")
    issuer_group.add_argument("--use-self-issuer", help="Use a self-signed issuer for the certificate",
                              action="store_true")

    args = parser.parse_args()

    # 传递 use_self_issuer 参数到 generate_certificate 函数
    generate_certificate(args.path, args.use_original_issuer, args.use_self_issuer, args.save_path)


if __name__ == "__main__":
    main()
