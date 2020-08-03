# Setting Up Rucio with XCache

This guide assumes that the Rucio instance, XRootD storage node, and XCache has been set up; and the XCache and XRootD nodes have been configured properly.

### Introduction
Rucio supports the use of XCache out of the box. In essence, Rucio will prepend an XCache URL to the actual PFN, if the client and RSE are located on different sites. For example:
- `RSE1` is located on `SITE1` with the URL `root://rse1:1094//rucio`.
- `RSE2` is located on `SITE2` with the URL `root://rse2:1094//rucio`.
- `SITE3` has an XCache installed on `root://cache3:1094/`.

When a client accesses `RSE1` from `SITE1`, Rucio will return `root://rse1:1094//rucio/scope/xx/xx/name` as PFN.
However, when a client accesses `RSE1` from `SITE3`, Rucio will return `root://cache3:1094//root://rse1:1094//rucio/scope/xx/xx/name` as PFN.

### Setting up Rucio
1. Make sure XRootD storage nodes and XCache server have been properly configured.
2. Assign a site name to the RSEs to be cached. 
```
$ rucio-admin rse set-attribute --rse RSENAME --key site --value SITENAME
```
3. Set a configuration item for each XCache instance on a site. Note that the value should not include `root://`.
```
$ rucio-admin config set --section root-proxy-internal --option SITENAME --value XCACHE_HOST_NAME:PORT
```

### Setting up client
To get the list of replicas with the caches prepended to the PFNs, the client must be in a different site.
Hence, the client must be configured with a site name. To do that:

#### Using Rucio client's `list_replicas` method
Set an environment variable `SITE_NAME=sitename`, or specify the `client_location` parameter with a dict containing `site` key: `{'site': 'sitename'}`

#### Using `/replicas/list` REST API
Specify the `client_location` with a dict containing `site` key in the JSON request body.
```
{
    ...
    "client_location": {
        "site": "sitename",
        ...
    }
}
```

#### Configuring `rucio-jupyterlab` extension
Specify the `site_name` option in the instance configuration.
```
{
    "instances": [
        {
            ...
            "site_name": "sitename"
        }
    ]
}
```