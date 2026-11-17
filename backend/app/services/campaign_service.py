from collections import defaultdict
from statistics import mean

import networkx as nx
from ml.graph.intelligence import build_review_graph
from ml.temporal.analyzer import analyze_temporal_patterns, detect_synchronized_activity
from sqlalchemy.orm import Session

from app.models.review import Review
from app.models.review_similarity import ReviewSimilarity


class CampaignService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_campaigns(self) -> dict:
        reviews = self.db.query(Review).all()
        if not reviews:
            return {"campaigns": [], "total": 0, "data_source": "no review data"}

        payloads = [self._review_payload(review) for review in reviews]
        payload_by_id = {review["review_id"]: review for review in payloads}
        review_pk_to_id = {review.id: review.review_id for review in reviews}
        similarity_rows = self.db.query(ReviewSimilarity).all()
        similarity_pairs = [
            {
                "review_a_id": review_pk_to_id[pair.review_a_id],
                "review_b_id": review_pk_to_id[pair.review_b_id],
                "similarity_score": pair.similarity_score,
            }
            for pair in similarity_rows
            if pair.review_a_id in review_pk_to_id and pair.review_b_id in review_pk_to_id
        ]
        graph = build_review_graph(payloads, similarity_pairs)

        campaigns = []
        components = sorted(
            nx.connected_components(graph),
            key=lambda component: tuple(sorted(component)),
        )
        for component in components:
            reviewer_ids = sorted(
                node.split(":", 1)[1] for node in component if node.startswith("reviewer:")
            )
            product_ids = sorted(
                node.split(":", 1)[1] for node in component if node.startswith("product:")
            )
            component_reviews = [
                review
                for review in payloads
                if review["reviewer_id"] in reviewer_ids and review["product_id"] in product_ids
            ]
            if len(reviewer_ids) < 2 or len(component_reviews) < 2:
                continue

            review_ids = {review["review_id"] for review in component_reviews}
            pair_evidence = [
                pair
                for pair in similarity_pairs
                if pair["review_a_id"] in review_ids
                and pair["review_b_id"] in review_ids
                and payload_by_id[pair["review_a_id"]]["reviewer_id"]
                != payload_by_id[pair["review_b_id"]]["reviewer_id"]
            ]
            temporal = analyze_temporal_patterns(component_reviews)
            timestamps_by_product: dict[str, list] = defaultdict(list)
            for review in component_reviews:
                timestamps_by_product[review["product_id"]].append(review["review_timestamp"])
            synchronized_pairs = detect_synchronized_activity(list(timestamps_by_product.values()))
            temporal_risk = max(
                temporal["temporal_risk"],
                min(synchronized_pairs * 0.15, 0.6),
            )
            similarity_score = (
                mean(pair["similarity_score"] for pair in pair_evidence)
                if pair_evidence
                else 0.0
            )
            if not pair_evidence and temporal_risk == 0:
                continue

            graph_risk = min(
                1.0,
                0.15 + len(reviewer_ids) * 0.12 + len(product_ids) * 0.08,
            )
            risk_score = min(
                1.0,
                graph_risk * 0.35 + temporal_risk * 0.35 + similarity_score * 0.30,
            )
            subgraph = graph.subgraph(component)
            reviewer_links = sum(
                1 for _, _, edge in subgraph.edges(data=True) if edge.get("edge_type") == "similarity_link"
            )

            campaigns.append(
                {
                    "campaign_id": "",
                    "risk_score": risk_score,
                    "reviewer_count": len(reviewer_ids),
                    "product_count": len(product_ids),
                    "review_count": len(component_reviews),
                    "connected_entities": {
                        "reviewers": reviewer_ids,
                        "products": product_ids,
                        "reviews": [
                            {
                                "review_id": review["review_id"],
                                "reviewer_id": review["reviewer_id"],
                                "product_id": review["product_id"],
                                "rating": review["rating"],
                                "review_timestamp": review["review_timestamp"].isoformat(),
                            }
                            for review in component_reviews
                        ],
                    },
                    "temporal_evidence": {
                        "risk_score": temporal_risk,
                        "burst_windows": int(temporal["metrics"].get("burst_windows", 0)),
                        "avg_interval_hours": temporal["metrics"].get("avg_interval_hours"),
                        "synchronized_pairs": synchronized_pairs,
                        "observations": temporal["observations"],
                    },
                    "similarity_evidence": {
                        "pair_count": len(pair_evidence),
                        "average_score": similarity_score,
                        "max_score": max(
                            (pair["similarity_score"] for pair in pair_evidence),
                            default=0.0,
                        ),
                        "pairs": sorted(
                            pair_evidence,
                            key=lambda pair: pair["similarity_score"],
                            reverse=True,
                        )[:20],
                    },
                    "graph_evidence": {
                        "node_count": subgraph.number_of_nodes(),
                        "edge_count": subgraph.number_of_edges(),
                        "similarity_link_count": reviewer_links,
                    },
                    "explanation": self._explanation(
                        temporal_risk,
                        synchronized_pairs,
                        pair_evidence,
                        reviewer_links,
                    ),
                }
            )

        campaigns.sort(
            key=lambda campaign: (
                -campaign["risk_score"],
                campaign["connected_entities"]["reviewers"],
            )
        )
        for index, campaign in enumerate(campaigns, start=1):
            campaign["campaign_id"] = f"campaign-{index}"

        return {
            "campaigns": campaigns,
            "total": len(campaigns),
            "data_source": self._data_source(reviews),
        }

    @staticmethod
    def _review_payload(review: Review) -> dict:
        return {
            "review_id": review.review_id,
            "reviewer_id": review.reviewer.reviewer_id if review.reviewer else str(review.reviewer_id),
            "product_id": review.product.product_id if review.product else str(review.product_id),
            "rating": review.rating,
            "review_text": review.review_text,
            "review_timestamp": review.review_timestamp,
        }

    @staticmethod
    def _data_source(reviews: list[Review]) -> str:
        demo_count = sum(bool(review.is_demo) for review in reviews)
        if demo_count == len(reviews):
            return "demo/sample"
        if demo_count:
            return "mixed demo and stored data"
        return "stored review data"

    @staticmethod
    def _explanation(
        temporal_risk: float,
        synchronized_pairs: int,
        pair_evidence: list[dict],
        reviewer_links: int,
    ) -> str:
        signals = ["reviewer-product network connection"]
        if synchronized_pairs or temporal_risk:
            signals.append("concentrated or synchronized review timing")
        if pair_evidence:
            signals.append("cross-reviewer text similarity")
        if reviewer_links:
            signals.append("similarity links between reviewers")
        return "Campaign candidate supported by " + ", ".join(signals) + ". Risk is a heuristic estimate, not proof of fraud."
