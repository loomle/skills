# Mode Selection

Use this table to choose between Loomle and bundled UE Python.

| Situation | Preferred Mode | Why |
| --- | --- | --- |
| Fix one broken Material edge | `LOOMLE` | Fast read-mutate-verify loop |
| Replace a small Material subgraph | `LOOMLE` | Good for local interactive rewrites |
| Explore an unfamiliar existing Material | `LOOMLE` | Query and selection are the main tools |
| Generate a new Material graph from scratch | `UE Python` | Deterministic and rerunnable |
| Need a committed script artifact | `UE Python` | Script becomes the durable output |
| Need command-line execution through `UnrealEditor-Cmd` | `UE Python` | Native fit for this execution model |
| Need actor assignment or asset post-processing | `UE Python` | Easier to orchestrate directly in Python |
| Loomle pin/address behavior is blocking reliable progress | `UE Python` | Direct MaterialEditingLibrary fallback |
| Need tight compile-and-readback loop on an existing graph | `LOOMLE` | Best interactive ergonomics |

## Rule of Thumb
- Existing graph, local change, interactive verification: use `LOOMLE`.
- New graph, deterministic generation, reusable artifact: use `UE Python`.
