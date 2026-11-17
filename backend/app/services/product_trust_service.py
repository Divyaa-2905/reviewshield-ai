from collections import Counter

from sqlalchemy.orm import Session

from app.models.prediction import Prediction
from app.models.product import Product
from app.models.review import Review
from app.services.campaign_service import CampaignService


class ProductTrustService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def analyze(self, product: Product) -> dict:
        reviews = (
            self.db.query(Review)
            .filter(Review.product_id == product.id)
            .order_by(Review.review_timestamp.desc(), Review.id.desc())
            .all()
        )
        total_reviews = len(reviews)
        ratings = Counter(f"{review.rating:g}" for review in reviews)
        rating_distribution = dict(sorted(ratings.items(), key=lambda item: float(item[0])))

        if not total_reviews:
            return {
                "product_id": product.product_id,
                "product_name": product.name,
                "review_count": 0,
                "prediction_coverage": 0,
                "predicted_review_count": 0,
                "suspicious_review_count": 0,
                "suspicious_percentage": None,
                "rating_distribution": rating_distribution,
                "average_rating": None,
                "five_star_percentage": None,
                "campaign_count": 0,
                "campaign_review_count": 0,
                "campaign_involvement_percentage": None,
                "risk_score": None,
                "trust_score": None,
                "indicators": [],
                "score_explanation": "No stored reviews are available, so a product trust score cannot be estimated.",
            }

        review_ids = [review.id for review in reviews]
        latest_predictions: dict[int, Prediction] = {}
        predictions = (
            self.db.query(Prediction)
            .filter(Prediction.review_id.in_(review_ids))
            .order_by(Prediction.created_at.desc(), Prediction.id.desc())
            .all()
        )
        for prediction in predictions:
            latest_predictions.setdefault(prediction.review_id, prediction)

        predicted_count = len(latest_predictions)
        suspicious_count = sum(
            prediction.classification.lower() in {"suspicious", "potentially fake"}
            for prediction in latest_predictions.values()
        )
        suspicious_percentage = suspicious_count / predicted_count * 100 if predicted_count else None
        campaign_payload = CampaignService(self.db).get_campaigns()
        product_review_ids = {review.review_id for review in reviews}
        involved_review_ids = {
            review["review_id"]
            for campaign in campaign_payload["campaigns"]
            for review in campaign["connected_entities"]["reviews"]
            if review["product_id"] == product.product_id
        }
        campaign_review_count = len(product_review_ids & involved_review_ids)
        campaign_involvement = campaign_review_count / total_reviews * 100
        five_star_count = sum(review.rating == 5 for review in reviews)
        five_star_percentage = five_star_count / total_reviews * 100
        rating_risk = max(0.0, min(100.0, (five_star_percentage - 60.0) / 40.0 * 100))

        active_weights = {
            "suspicious_reviews": 0.50 if predicted_count else 0.0,
            "rating_distribution": 0.25,
            "campaign_involvement": 0.25,
        }
        weight_total = sum(active_weights.values())
        normalized_weights = {key: value / weight_total for key, value in active_weights.items()}
        indicator_risks = {
            "suspicious_reviews": suspicious_percentage or 0.0,
            "rating_distribution": rating_risk,
            "campaign_involvement": campaign_involvement,
        }
        risk_score = sum(indicator_risks[key] * weight for key, weight in normalized_weights.items())

        indicators = [
            {
                "key": "suspicious_reviews",
                "label": "Suspicious review share",
                "value": suspicious_percentage,
                "risk_score": suspicious_percentage,
                "weight": round(normalized_weights["suspicious_reviews"] * 100, 1),
                "explanation": (
                    f"{suspicious_count} of {predicted_count} reviews with a stored prediction were classified "
                    "Suspicious or Potentially Fake. Unscored reviews are not treated as genuine."
                    if predicted_count
                    else "No reviews have stored predictions; this indicator is unavailable and excluded from the score."
                ),
            },
            {
                "key": "rating_distribution",
                "label": "Five-star concentration",
                "value": five_star_percentage,
                "risk_score": rating_risk,
                "weight": round(normalized_weights["rating_distribution"] * 100, 1),
                "explanation": (
                    "Risk begins above 60% five-star reviews and rises linearly to 100% at a fully five-star "
                    "distribution. This is a review-pattern heuristic, not evidence of fraud."
                ),
            },
            {
                "key": "campaign_involvement",
                "label": "Campaign involvement",
                "value": campaign_involvement,
                "risk_score": campaign_involvement,
                "weight": round(normalized_weights["campaign_involvement"] * 100, 1),
                "explanation": (
                    f"{campaign_review_count} of {total_reviews} product reviews appear in a detected campaign "
                    "candidate. Campaign detection is heuristic and does not prove coordination."
                ),
            },
        ]
        return {
            "product_id": product.product_id,
            "product_name": product.name,
            "review_count": total_reviews,
            "prediction_coverage": predicted_count / total_reviews * 100,
            "predicted_review_count": predicted_count,
            "suspicious_review_count": suspicious_count,
            "suspicious_percentage": suspicious_percentage,
            "rating_distribution": rating_distribution,
            "average_rating": sum(review.rating for review in reviews) / total_reviews,
            "five_star_percentage": five_star_percentage,
            "campaign_count": sum(
                any(
                    review["product_id"] == product.product_id
                    for review in campaign["connected_entities"]["reviews"]
                )
                for campaign in campaign_payload["campaigns"]
            ),
            "campaign_review_count": campaign_review_count,
            "campaign_involvement_percentage": campaign_involvement,
            "risk_score": risk_score,
            "trust_score": 100.0 - risk_score,
            "indicators": indicators,
            "score_explanation": (
                "Risk score is the weighted mean of available indicators (suspicious share 50%, rating concentration "
                "25%, campaign involvement 25%). Missing prediction coverage removes that indicator and its weight "
                "is redistributed proportionally. Trust score equals 100 minus risk score. These are estimates, "
                "not proof of fraud."
            ),
        }
