#!/usr/bin/env bash

# This script will check / create the TLS secret in a namespace
# Inputs from config.yaml:
# - ingress_namespace - The namespace in which you want the TLS secret.
# - ingress_tls_key_name - The name of the secret in the given namespace.
# - ingress_tls_certificate 
# - ingress_tls_key

# Put the cert and key into temp files...
tmpdir=/tmp/${USER}_${site_name}

if [[ ! -d ${tmpdir} ]]; then
        mkdir /tmp/${USER}_${site_name}
fi

cert_file=${tmpdir}/cert$$
key_file=${tmpdir}/key$$

echo ${ingress_tls_certificate} | sed 's/ CERTIFICATE/xCERTIFICATE/g' | sed 's/ /\n/g' | sed 's/xCERTIFICATE/ CERTIFICATE/g' > $cert_file
echo ${ingress_tls_key} | sed 's/ RSA PRIVATE /RSAPRIVATE/g' | sed 's/ /\n/g' | sed 's/RSAPRIVATE/ RSA PRIVATE /g' > $key_file

function die {
        >&2 echo "FATAL: ${@:-UNKNOWN ERROR}"
        exit 1
}

# Check to see if the key and certificate files are good...
cat ${cert_file} | openssl x509 -noout
if [[ $? != 0 ]]; then
        echo "The certificate expected in config.yaml ->  \"ingress_tls_certficate: | xxx\" is not valid. Recommend manually apply."
        exit 1
fi
 
# We are creating a Namespace and creating the ingress Secret
# To-Do - move to creating the secret in a central namespace (ex: tanzu-system-ingress)
# then use TLS Delegation with contour to reference the secret from other namespaces

kubectl create ns ${ingress_namespace} --dry-run=client -o yaml | kubectl apply -f - || die "Could not create namespace ${ingress_namespace}."

# If the secret already exists, delete it so we can recreate it...
kubectl delete secret tls ${ingress_tls_key_name} -n ${ingress_namespace}

# create or patch secret based on the certs defined in the directory /usr/src/cloud-development/tanzu-certs/${site_name}/ingress/
kubectl create secret tls ${ingress_tls_key_name} -n ${ingress_namespace} \
        --key=${key_file} \
        --cert=${cert_file} --dry-run=client -o yaml | \
        kubectl apply -f - || die "Error creating or patching TLS secret."

echo "Created TLS NameSpace and Secret"
