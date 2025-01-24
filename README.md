### EMLOV4-Session-12 Assignment - Kubernetes - IV: IRSA, Volumes, ISTIO & KServe (under development)

(under development) - (class room work is completed and able to deploy sd3 and infer it without any issues)
I took a g6.2xlarge instance and it cost 0.4$ even for spot instance so either develop with a small model first with g4dn.xlarge
and if eveything works fine go for sd3 models. Else you will end up lossing 3-4 dollars.

Todo: while developing assignment use a small model of diffuser. Dont use sd3 first itself it needs 24GB GPU RAM to load

$ curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3
$ chmod 700 get_helm.sh
$ ./get_helm.sh