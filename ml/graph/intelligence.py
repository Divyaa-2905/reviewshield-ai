from collections import defaultdict

import networkx as nx


def build_review_graph(reviews: list[dict], similarity_pairs: list[dict] | None = None) -> nx.Graph:
    graph = nx.Graph()
    for review in reviews:
        reviewer_node = f"reviewer:{review['reviewer_id']}"
        product_node = f"product:{review['product_id']}"
        graph.add_node(reviewer_node, type="reviewer", label=review["reviewer_id"])
        graph.add_node(product_node, type="product", label=review["product_id"])
        graph.add_edge(
            reviewer_node,
            product_node,
            review_id=review["review_id"],
            rating=review.get("rating"),
            timestamp=str(review.get("review_timestamp", "")),
        )

    if similarity_pairs:
        reviewer_links: dict[str, set[str]] = defaultdict(set)
        review_lookup = {r["review_id"]: r for r in reviews}
        for pair in similarity_pairs:
            ra = review_lookup.get(pair["review_a_id"])
            rb = review_lookup.get(pair["review_b_id"])
            if ra and rb and ra["reviewer_id"] != rb["reviewer_id"]:
                reviewer_links[ra["reviewer_id"]].add(rb["reviewer_id"])
                reviewer_links[rb["reviewer_id"]].add(ra["reviewer_id"])

        for reviewer_id, linked in reviewer_links.items():
            for other in linked:
                n1 = f"reviewer:{reviewer_id}"
                n2 = f"reviewer:{other}"
                if graph.has_node(n1) and graph.has_node(n2):
                    graph.add_edge(n1, n2, edge_type="similarity_link")

    return graph


def analyze_graph(graph: nx.Graph) -> dict:
    if graph.number_of_nodes() == 0:
        return {"graph_risk": 0.0, "metrics": {}, "clusters": [], "observations": []}

    components = list(nx.connected_components(graph))
    degrees = dict(graph.degree())
    observations = []
    risk = 0.0

    high_degree_reviewers = [
        n for n, d in degrees.items() if n.startswith("reviewer:") and d >= 5
    ]
    if high_degree_reviewers:
        risk += 0.2
        observations.append("Reviewer with unusually high network connectivity detected.")

    suspicious_components = [c for c in components if len(c) >= 4]
    if suspicious_components:
        risk += 0.25
        observations.append("Connected component with multiple entities detected.")

    clusters = []
    for i, component in enumerate(suspicious_components[:10]):
        reviewers = [n.split(":", 1)[1] for n in component if n.startswith("reviewer:")]
        products = [n.split(":", 1)[1] for n in component if n.startswith("product:")]
        cluster_risk = min(0.4 + len(component) * 0.05, 1.0)
        clusters.append({
            "cluster_id": f"cluster-{i+1}",
            "risk_score": cluster_risk,
            "reviewer_count": len(reviewers),
            "product_count": len(products),
            "reviewers": reviewers,
            "products": products,
            "explanation": "Coordinated activity pattern in reviewer-product network.",
        })

    metrics = {
        "node_count": float(graph.number_of_nodes()),
        "edge_count": float(graph.number_of_edges()),
        "component_count": float(len(components)),
        "max_degree": float(max(degrees.values()) if degrees else 0),
    }

    return {
        "graph_risk": min(risk, 1.0),
        "metrics": metrics,
        "clusters": clusters,
        "observations": observations,
    }


def graph_to_frontend(graph: nx.Graph, risk_map: dict[str, float] | None = None) -> dict:
    risk_map = risk_map or {}
    nodes = []
    for node_id, data in graph.nodes(data=True):
        node_type = data.get("type", "unknown")
        label = data.get("label", node_id)
        nodes.append({
            "id": node_id,
            "label": label,
            "type": node_type,
            "risk_score": risk_map.get(node_id, 0.0),
        })
    edges = []
    for source, target, data in graph.edges(data=True):
        edges.append({
            "source": source,
            "target": target,
            "rating": data.get("rating"),
            "review_id": data.get("review_id"),
        })
    return {"nodes": nodes, "edges": edges}
