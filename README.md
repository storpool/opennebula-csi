# OpenNebula CSI

## Overview

This CSI driver is designed to be used by Kubernetes deployments inside OpenNebula virtual machines. The CSI driver
provision persistent images with the requested size. It then attaches the images to the required virtual machine.

## Deployment

The OpenNebula CSI follows the deployment pattern of having a single container image that contains all the required
code.

### Preparation

The CSI driver needs to map OpenNebula virtual machines to Kubernetes nodes in a one-to-one manner. To do so, it will
try to find out the OpenNebula VM ID in the list of its arguments. If it fails, the driver will try to read the VM ID
from a file located at `/var/lib/cloud/vm-id`.

#### VM ID Discovery

The CSI driver now automatically discovers the VM ID using an initContainer that queries the OpenNebula API. This eliminates the need for manual VM configuration scripts.

The initContainer (`one-vmid:latest`) runs before the main CSI containers and:
1. Connects to the OpenNebula API using credentials from the `sp-one` secret
2. Queries the VM pool to find the VM matching the Kubernetes node name
3. Writes the VM ID to `/var/lib/cloud/vm-id` for the main container to use

#### Required Secret

Create a secret named `sp-one` in the `kube-system` namespace with the following keys:
- `ONE_API_ENDPOINT`: The OpenNebula API endpoint URL
- `ONE_API_USERNAME`: OpenNebula API username
- `ONE_API_PASSWORD`: OpenNebula API password

```shell
kubectl create secret generic sp-one -n kube-system \
  --from-literal=ONE_API_ENDPOINT=http://your-opennebula-endpoint:2633/RPC2 \
  --from-literal=ONE_API_USERNAME=your-username \
  --from-literal=ONE_API_PASSWORD=your-password
```

### Starting the CSI driver

Deploying the CSI driver is carried out by using `kubectl`: 

```shell
kubectl apply -f manifests/
```

The above command will also create a `StorageClass` called `storpool-nvme` that will use the default OpenNebula
datastore. Feel free to delete it and create your own `StorageClasses` as described in the next section.

### Managing image datastores

The CSI driver is designed to map a Kubernetes `StorageClass` object to an OpenNebula image datastore in a one-to-one
fashion. The mapping is done by setting the `datastore_id` parameter of the `StorageClass` object to match the desired
OpenNebula datastore. Below is an example `StorageClass` object definition:

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: one-datastore-1
provisioner: onecsi.storpool.com
parameters:
  datastore_id: 1
mountOptions:
  - noatime
allowVolumeExpansion: true
volumeBindingMode: WaitForFirstConsumer
```

## Building

The driver can be built like this:

```shell
docker build -t <repo_url>:<desired_tag> .
```

> [!NOTE]
> If you decide to build a custom image, please remember to update the URL in the manifests
