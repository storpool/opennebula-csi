#!/usr/bin/env python3

import os
import sys
import pyone


def get_config():
    """Get configuration from environment variables."""
    config = {}
    required_vars = [
        "SP_NODE_NAME",
        "ONE_API_ENDPOINT",
        "ONE_API_USERNAME",
        "ONE_API_PASSWORD",
    ]

    missing_vars = []
    for var in required_vars:
        value = os.environ.get(var)
        if not value:
            missing_vars.append(var)
        else:
            config[var] = value

    if missing_vars:
        print(
            f"Error: Missing required environment variables: {', '.join(missing_vars)}",
            file=sys.stderr,
        )
        sys.exit(1)

    return config


if __name__ == "__main__":
    config = get_config()

    # Create API proxy
    api = pyone.OneServer(
        config["ONE_API_ENDPOINT"],
        session=f"{config['ONE_API_USERNAME']}:{config['ONE_API_PASSWORD']}",
    )

    try:
        for vm in api.vmpool.info(-1, -1, -1, 3).VM:
            if vm.get_NAME() == config["SP_NODE_NAME"]:
                vmid = vm.get_ID()
                print("Found VM ID:", vmid)
                with open("/var/lib/cloud/vm-id", "w") as f:
                    f.write(str(vmid))
                    # Add a newline for consistency with contrib/one-context.sh
                    f.write("\n")
                break
        else:
            print(
                f"Error: No VM found with name {config['SP_NODE_NAME']}",
                file=sys.stderr,
            )
            sys.exit(1)
    except pyone.OneException as e:
        print(f"Error from the OpenNebula API: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        api.server_close()
