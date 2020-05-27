# Ideas

- The extension GUI will be in the form of left sidebar panel.
- There will be three components: lab extension (UI), server extension, and IPython kernel extension.
  - The server extension is the one communicating with Rucio via REST API. All Rucio-related configurations are exposed to the server extension only.
  - The UI communicates with the server extension to display relevant information and send relevant commands.
  - The IPython kernel extension exposes a function to translate Rucio DID to a volatile physical path (e.g. `rucio_path(did)`).

## Server Extension
The server extension performs the following.
- Rucio authentication
- Retrieving details about a DID:
  - Attached files, uses `GET /dids/{scope}/{name}/files`
  - Data availability, uses `GET /replicas/{scope}/{name}`
  - Data staging status, uses `GET /dids/{scope}/{name}/rules` to get `rule_id`, then uses `GET /rules/{rule_id}`
- When receiving a request to list files of a DID:
  - First, it retrieves the cache for a given DID
    - If not found, it retrieves the files and stores it in the cache with expiration
  - It returns an array of file DIDs attached to the given DID.
- When receiving a request to file details:
  - First, it retrieves the cache for a given DID
    - If not found, it does the following:
      - Retrieves the replicas of the DID for the destination RSE
        - If not exists, it does the following:
          - Retrieves the rule ID for the destination RSE
          - If such replication rule exists, retrieves the rule status
          - Output the status back to the UI to know whether the replication is on progress or stuck
        - If it exists, find the volatile file path from the retrieved PFN
          - Check if the server extension can see the file in the filesystem.
          - If not, throw an error
      - Then, store it in the cache for a certain amount of time
    - If found, check the expiry and the path (if any)
      - If the path should exist but no longer exists, purge cache and retrieve the data again.
  - It returns the following:
    - File availability and volatile path
    - Replication status (OK/REPLICATING/STUCK)
- When receiving a request to refresh replication status:
  - Retrieves the replicas of the DID for the destination RSE
    - If not exists, it does the following:
      - Retrieves the rule ID for the destination RSE
      - If such replication rule exists, retrieves the rule status
      - Output the status back to the UI to know whether the replication is on progress or stuck
    - If it exists, find the volatile file path from the retrieved PFN
      - Check if the server extension can see the file in the filesystem.
      - If not, throw an error
  - Update the cache database for the given DID
  - It returns the following:
    - File availability and volatile path
    - Replication status (OK/REPLICATING/STUCK)
- Creating a new replication rule to a destination RSE (not RSE expression)
- Store which Rucio instance to use (differs from experiment to experiment) (`~/.rucio_jupyterlab/instance.txt`)
- Store user preferences in a SQLite database in the user's home directory (`~/.rucio_jupyterlab/{rucio_instance_name}.db`)
  - Bookmarked DIDs.
  - DID caches.
- Retrieves instance configuration JSON from remote location.

Example configuration JSON:
```json
{
    "instances": [
        {
            "name": "atlas",
            "display_name": "ATLAS",
            "rucio_base_url": "https://rucio-prod.cern.ch",
            "auth": {
                "type": "userpass",
                "username": "swan",
                "password": "swan"
            },
            "destination_rse": "ATLAS-SWAN-DATADISK",
            "rse_mount_path": "/eos/atlas",
            "pfn_path_begins_at": 0,
            "create_replication_rule_enabled": true,
            "direct_download_enabled": true,
            "cache_expires_at": 17346723566
        },
        {
            "from_url": "https://rucio-config.atlas.cern.ch/config.json"
        }
    ]
}
```

### SQLite Database Entities
- UserPreferences
  - Key
  - Value
- Bookmarks
  - DID
  - Type (dataset|container|file)
- DatasetContainerCache
  - DID
  - FileDID
  - Expiry
- FileCache
  - DID
  - RSE
  - Expiry
  - ReplicationRuleID
  - ReplicationStatus (OK|REPLICATING|FAILED)
  - Path

## Lab Extension (UI)
The lab extension performs the following:
- Checking whether the kernel has the extension enabled. If not, display warning.
- Retrieving user preferences from server extension, and displaying it accordingly.
- Prompting users to pick which Rucio instance to use.
- Receiving a DID from user, retrieving the DID details from server extension, and displaying it in a list.
- Retrieving DID details from server extension.
- Refreshing the replication status of a DID regularly, if the details is shown on the UI.
- Exchange messages with the kernel extension and respond accordingly.
  - When the kernel extension sends a request to get a path from DID, return the path
  - If the data hasn't been made available, return an error message, and display the requested DID on the UI (along with a helpful instructional message) to allow users to stage the data in one click.

## IPython Kernel Extension
The kernel extension performs the following:
- Expose a function to translate DID into an accessible path, e.g. `rucio_did(did)`
- Communicate with the lab extension to get the path. If the path does not exist, raise an exception.
  - The error message should prompt the user to open the extension and make the data available.