# Examples

This page provides detailed examples of how to use the `xmrig` API. Each example demonstrates a specific functionality. 

## Examples List

01. [Add Miners](#add-miners)
02. [List All Miners](#list-all-miners)
03. [Get Individual Miners](#get-individual-miners)
04. [Update Config](#update-config)
05. [Update Individual Miners Endpoints](#update-individual-miners-endpoints)
06. [Update All Endpoints for All Miners](#update-all-endpoints-for-all-miners)
07. [Start/Stop All Miners](#start-or-stop-all-miners)
08. [Pause/Resume All Miners](#pause-or-resume-all-miners)
09. [Remove Miner](#remove-miner)
10. [Access Properties](#access-properties)
11. [Full Example](#full-example)

## Add Miners

This example demonstrates how to add XMRig miners to the XMRigManager. It shows how to configure logging and add miners to the manager.

```python title="add_miners.py" linenums="1"
{% include "../examples/add_miners.py" %}
```

## List All Miners

This example demonstrates how to list all XMRig miners managed by the XMRigManager. It shows how to configure logging, add miners to the manager, and list all miners.

```python title="list_all_miners.py" linenums="1"
{% include "../examples/list_all_miners.py" %}
```

## Get Individual Miners

This example demonstrates how to retrieve individual XMRig miners from the XMRigManager. It shows how to configure logging, add miners to the manager, and retrieve individual miners.

```python title="get_individual_miners.py" linenums="1"
{% include "../examples/get_individual_miners.py" %}
```

## Update Config

This example demonstrates how to update the configuration of an XMRig miner using the XMRigManager. It shows how to configure logging, add miners to the manager, retrieve the current config, modify it, and post the updated config.

```python title="update_config.py" linenums="1"
{% include "../examples/update_config.py" %}
```

## Update Individual Miners Endpoints

This example demonstrates how to update the endpoints for individual XMRig miners using the XMRigManager. It shows how to configure logging, add miners to the manager, and update the summary, backends, and config endpoints for each miner.

```python title="update_individual_miners_endpoints.py" linenums="1"
{% include "../examples/update_individual_miners_endpoints.py" %}
```

## Update All Endpoints for All Miners

This example demonstrates how to update all endpoints for all XMRig miners using the XMRigManager. It shows how to configure logging, add miners to the manager, and update all endpoints for all miners in the manager.

```python title="update_all_endpoints_for_all_miners.py" linenums="1"
{% include "../examples/update_all_endpoints_for_all_miners.py" %}
```

## Start Or Stop All Miners

This example demonstrates how to start and stop all XMRig miners using the XMRigManager. It shows how to configure logging, add miners to the manager, and perform start/stop actions on all miners.

```python title="start_stop_all_miners.py" linenums="1"
{% include "../examples/start_stop_all_miners.py" %}
```

## Pause Or Resume All Miners

This example demonstrates how to pause and resume all XMRig miners using the XMRigManager. It shows how to configure logging, add miners to the manager, and perform pause/resume actions on all miners.

```python title="pause_resume_all_miners.py" linenums="1"
{% include "../examples/pause_resume_all_miners.py" %}
```

## Remove Miner

This example demonstrates how to remove an XMRig miner from the XMRigManager. It shows how to configure logging, add miners to the manager, list all miners, remove a miner, and list all miners again.

```python title="remove_miner.py" linenums="1"
{% include "../examples/remove_miner.py" %}
```

## Access Properties

This example demonstrates how to use the XMRigManager to manage multiple XMRig miners. It shows how to configure logging, add miners to the manager, and retrieve data from individual miners. The example logs various properties of the miners, such as summary, backends, config, hashrates, and job counters.

```python title="access_properties.py" linenums="1"
{% include "../examples/access_properties.py" %}
```

## Full Example

This full example demonstrates various functionalities of the XMRigManager. It shows how to configure logging, add and remove miners, list all miners, update endpoints, pause/resume miners, start/stop miners, and update the miner's config.

```python title="full_example.py" linenums="1"
{% include "../examples/full-example.py" %}
```