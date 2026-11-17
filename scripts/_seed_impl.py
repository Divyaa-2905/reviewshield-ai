import random
from datetime import UTC, datetime, timedelta

from app.core.security import get_password_hash, verify_password
from app.models.behavior_profile import BehaviorProfile
from app.models.fraud_cluster import FraudCluster
from app.models.prediction import Prediction
from app.models.prediction_feedback import PredictionFeedback
from app.models.product import Product
from app.models.review import Review
from app.models.review_similarity import ReviewSimilarity
from app.models.reviewer import Reviewer
from app.models.user import User, UserRole
from app.services.ml_service import MLService
from app.services.vector_store import VectorStore
from sqlalchemy.orm import Session

from ml.behavior.profiler import analyze_reviewer_behavior
from ml.graph.intelligence import analyze_graph, build_review_graph
from ml.similarity.engine import build_similarity_index, compute_all_pairs_efficient
from ml.temporal.analyzer import analyze_temporal_patterns

SEED = 42
random.seed(SEED)


def reset_demo_data(db: Session) -> None:
    db.query(ReviewSimilarity).delete()
    db.query(PredictionFeedback).delete()
    db.query(Prediction).delete()
    db.query(BehaviorProfile).delete()
    db.query(FraudCluster).delete()
    db.query(Review).delete()
    db.query(Reviewer).delete()
    db.query(Product).delete()
    db.commit()


def seed_users(db: Session) -> None:
    users = [
        ("admin", "admin@reviewshield.demo", "admin123", UserRole.ADMIN),
        ("analyst", "analyst@reviewshield.demo", "analyst123", UserRole.ANALYST),
        ("viewer", "viewer@reviewshield.demo", "viewer123", UserRole.VIEWER),
    ]
    for username, email, password, role in users:
        user = db.query(User).filter(User.username == username).first()
        if user is None:
            db.add(
                User(
                    username=username,
                    email=email,
                    hashed_password=get_password_hash(password),
                    role=role,
                )
            )
        elif not verify_password(password, user.hashed_password):
            user.hashed_password = get_password_hash(password)
    db.commit()


def seed_demo_data(db: Session) -> None:
    reset_demo_data(db)
    seed_users(db)

    products_data = [
        ("prod-001", "Wireless Earbuds Pro", "electronics", "TechStore"),
        ("prod-002", "Organic Face Cream", "beauty", "GlowMart"),
        ("prod-003", "Smart Fitness Band", "electronics", "FitGear"),
        ("prod-004", "Kitchen Blender XL", "home", "HomeBest"),
        ("prod-005", "LED Desk Lamp", "home", "BrightLife"),
    ]
    products = {}
    for pid, name, cat, seller in products_data:
        p = Product(product_id=pid, name=name, category=cat, seller=seller, is_demo=True)
        db.add(p)
        db.flush()
        products[pid] = p

    reviewers_data = [
        ("rev-normal-01", 180, 0.1),
        ("rev-normal-02", 365, 0.05),
        ("rev-active-01", 90, 0.3),
        ("rev-suspicious-01", 30, 0.85),
        ("rev-suspicious-02", 25, 0.9),
        ("rev-coord-01", 20, 0.8),
        ("rev-coord-02", 18, 0.82),
        ("rev-coord-03", 15, 0.78),
    ]
    reviewers = {}
    now = datetime.now(UTC)
    for rid, age_days, susp in reviewers_data:
        r = Reviewer(
            reviewer_id=rid,
            account_created_at=now - timedelta(days=age_days),
            suspicious_score=susp,
            is_demo=True,
        )
        db.add(r)
        db.flush()
        reviewers[rid] = r

    genuine_templates = [
        "Good product for the price. Works as expected after two weeks of use.",
        "Decent quality but delivery took longer than expected.",
        "Satisfied with the purchase. Would consider buying again.",
        "Average experience. Nothing exceptional but no major issues.",
    ]
    suspicious_templates = [
        "Amazing product! Best purchase ever! Highly recommend to everyone!!!",
        "Excellent quality and very fast delivery. Five stars!",
        "Perfect product, love it! Must buy for everyone!",
    ]
    paraphrase_pairs = [
        ("Excellent product and very fast delivery.", "Great product with quick delivery."),
        ("Best earbuds I have ever used!", "These are the greatest earbuds ever!"),
    ]

    review_records = []
    review_id_counter = 1
    base_time = now - timedelta(days=60)

    def add_review(reviewer_key, product_key, text, rating, day_offset, label):
        nonlocal review_id_counter
        review = Review(
            review_id=f"rev-{review_id_counter:04d}",
            reviewer_id=reviewers[reviewer_key].id,
            product_id=products[product_key].id,
            rating=rating,
            review_text=text,
            review_timestamp=base_time + timedelta(days=day_offset, hours=random.randint(0, 23)),
            verified_purchase=random.choice([True, False]),
            review_label=label,
            is_demo=True,
        )
        db.add(review)
        db.flush()
        review_records.append(
            {
                "review_id": review.review_id,
                "reviewer_id": reviewer_key,
                "product_id": product_key,
                "rating": rating,
                "review_text": text,
                "review_timestamp": review.review_timestamp,
                "review_label": label,
                "db_id": review.id,
            }
        )
        review_id_counter += 1
        return review

    for i, template in enumerate(genuine_templates):
        add_review("rev-normal-01", "prod-001", template, 4.0, i * 5, "genuine")
        add_review("rev-normal-02", "prod-003", template, 3.5, i * 7 + 2, "genuine")

    for i, template in enumerate(suspicious_templates):
        add_review("rev-suspicious-01", "prod-002", template, 5.0, 10 + i, "fake")
        add_review("rev-suspicious-02", "prod-004", template, 5.0, 12 + i, "fake")

    for a, b in paraphrase_pairs:
        add_review("rev-suspicious-01", "prod-002", a, 5.0, 20, "fake")
        add_review("rev-suspicious-02", "prod-002", b, 5.0, 20, "fake")

    coord_reviewers = ["rev-coord-01", "rev-coord-02", "rev-coord-03"]
    burst_day = 25
    for rev_key in coord_reviewers:
        add_review(rev_key, "prod-005", suspicious_templates[0], 5.0, burst_day, "fake")
        add_review(rev_key, "prod-005", suspicious_templates[1], 5.0, burst_day, "fake")

    db.commit()

    build_similarity_index(review_records)
    VectorStore(db).persist_embeddings(review_records, "tfidf")
    pairs = compute_all_pairs_efficient(review_records, threshold=0.5)
    review_id_map = {r["review_id"]: r["db_id"] for r in review_records}
    for pair in pairs:
        ra = next(r for r in review_records if r["review_id"] == pair["review_a_id"])
        rb = next(r for r in review_records if r["review_id"] == pair["review_b_id"])
        db.add(
            ReviewSimilarity(
                review_a_id=review_id_map[pair["review_a_id"]],
                review_b_id=review_id_map[pair["review_b_id"]],
                similarity_score=pair["similarity_score"],
                similarity_type=pair["similarity_type"],
                same_product=ra["product_id"] == rb["product_id"],
                same_reviewer=ra["reviewer_id"] == rb["reviewer_id"],
            )
        )
    db.commit()

    graph = build_review_graph(review_records, pairs)
    graph_analysis = analyze_graph(graph)
    for cluster in graph_analysis["clusters"]:
        db.add(
            FraudCluster(
                cluster_id=cluster["cluster_id"],
                risk_score=cluster["risk_score"],
                reviewer_count=cluster["reviewer_count"],
                product_count=cluster["product_count"],
                review_count=len(review_records),
                reviewers=cluster["reviewers"],
                products=cluster["products"],
                explanation=cluster["explanation"],
                graph_metrics=graph_analysis["metrics"],
            )
        )
    db.commit()

    ml_service = MLService(db)
    for record in review_records:
        ml_service.analyze_and_store(record["db_id"])

    for rid, reviewer in reviewers.items():
        revs = [r for r in review_records if r["reviewer_id"] == rid]
        behavior = analyze_reviewer_behavior(revs, reviewer.account_created_at)
        temporal = analyze_temporal_patterns(revs)
        db.add(
            BehaviorProfile(
                reviewer_id=reviewer.id,
                behavioural_metrics=behavior["metrics"],
                temporal_metrics=temporal["metrics"],
                rating_metrics={"suspicious_score": reviewer.suspicious_score},
                anomaly_metrics={"behavior_risk": behavior["behavior_risk"]},
                observations="; ".join(behavior["observations"] + temporal["observations"]),
            )
        )
        reviewer.total_reviews = len(revs)
        if revs:
            ratings = [r["rating"] for r in revs]
            reviewer.average_rating = sum(ratings) / len(ratings)
            reviewer.five_star_percentage = sum(1 for r in ratings if r == 5) / len(ratings)
            reviewer.product_count = len({r["product_id"] for r in revs})
    db.commit()

    print(
        f"DEMO DATA: {len(review_records)} reviews, {len(pairs)} similarities, "
        f"{len(graph_analysis['clusters'])} clusters"
    )
