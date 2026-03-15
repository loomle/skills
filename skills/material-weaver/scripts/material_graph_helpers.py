"""Helpers for UE material graph scripting patterns."""

from collections import defaultdict, deque


def pin_for_unary_node(node_class_name: str) -> str:
    """Return recommended input pin name for unary node classes in UE 5.7."""
    unary_empty_pin = {
        "MaterialExpressionComponentMask",
        "MaterialExpressionFloor",
        "MaterialExpressionFrac",
        "MaterialExpressionSine",
        "MaterialExpressionAbs",
        "MaterialExpressionOneMinus",
        "MaterialExpressionSaturate",
    }
    if node_class_name in unary_empty_pin:
        return ""
    return "Input"


def assign_layers_from_roots(roots, upstream_edges):
    """Assign leftward layers by traversing upstream from output roots.

    Args:
        roots: list[str], output-side start nodes.
        upstream_edges: dict[str, list[tuple[str, str]]]
            mapping node -> [(upstream_node_key, input_pin_name), ...]

    Returns:
        dict[str, int] where smaller value means closer to output side.
    """
    layer = {}
    q = deque()
    for r in roots:
        # keep all roots in the same output-side band
        layer[r] = 0
        q.append(r)

    while q:
        node = q.popleft()
        for upstream, _pin in upstream_edges.get(node, []):
            candidate = layer[node] + 1
            # Keep the farthest (deepest upstream) layer index for stable leftward expansion.
            if upstream not in layer or candidate > layer[upstream]:
                layer[upstream] = candidate
                q.append(upstream)
    return layer


def _incoming_dependents(upstream_edges):
    """Build reverse dependency map upstream -> [downstream nodes]."""
    rev = defaultdict(list)
    for downstream, inputs in upstream_edges.items():
        for upstream, _pin in inputs:
            rev[upstream].append(downstream)
    return rev


def order_nodes_within_layers(layer_map, upstream_edges, pin_priority=None, root_order=None):
    """Order nodes in each layer to reduce crossings.

    Uses a simple barycenter strategy based on downstream node order.
    pin_priority optionally controls per-node input pin ordering:
    e.g. {"A":0, "B":1, "Alpha":2}
    """
    pin_priority = pin_priority or {}
    by_layer = defaultdict(list)
    for node, l in layer_map.items():
        by_layer[l].append(node)

    layers = sorted(by_layer.keys())
    order = {}

    # Initialize output/root layer in deterministic order.
    if layers:
        rightmost = layers[0]
        root_order = root_order or by_layer[rightmost]
        root_rank = {k: i for i, k in enumerate(root_order)}
        by_layer[rightmost].sort(key=lambda n: (root_rank.get(n, 999), n))
        for idx, n in enumerate(by_layer[rightmost]):
            order[n] = idx

    incoming = _incoming_dependents(upstream_edges)

    for l in layers[1:]:
        nodes = by_layer[l]

        def score(node):
            deps = incoming.get(node, [])
            if deps:
                return sum(order.get(d, 0) for d in deps) / len(deps)

            # fallback: consider explicit pin preference where applicable
            pin_scores = []
            for down, inputs in upstream_edges.items():
                for up, pin in inputs:
                    if up == node:
                        pin_scores.append(pin_priority.get(pin, 99))
            if pin_scores:
                return sum(pin_scores) / len(pin_scores)
            return 0

        nodes.sort(key=lambda n: (score(n), n))
        for idx, n in enumerate(nodes):
            order[n] = idx

    return {l: by_layer[l] for l in layers}


def layout_from_layers(layered_nodes, x_step=320, y_step=180, root_x=-360):
    """Convert layered node order into target positions.

    Returns:
        dict[node_key, (x, y)]
    """
    positions = {}
    for col, layer in enumerate(sorted(layered_nodes.keys())):
        nodes = layered_nodes[layer]
        x = root_x - col * x_step
        first_y = -((len(nodes) - 1) * y_step) // 2
        for i, node in enumerate(nodes):
            positions[node] = (x, first_y + i * y_step)
    return positions


def second_pass_column_layout(items, min_gap=48):
    """Given [(key, y, h)], return non-overlapping y map with simple downward push."""
    result = {}
    cursor_bottom = None
    for key, y, h in sorted(items, key=lambda t: t[1]):
        y2 = y
        if cursor_bottom is not None and y2 < cursor_bottom + min_gap:
            y2 = cursor_bottom + min_gap
        result[key] = y2
        cursor_bottom = y2 + h
    return result
