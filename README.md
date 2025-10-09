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

The recommended approach is to add the contents of the `contrib/one-context.sh` script to the start-up script of the
virtual machine. The script will take care of creating the `/var/lib/cloud/vm-id` file and populating its contents with
the correct VM ID.

> [!NOTE]
> After adding the code from `contrib/one-context.sh` to the start-up script of a virtual machine, the virtual machine
> must be restarted for the new start-up script to be executed.

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
