#!/usr/bin/env python3
import sys
import os
import argparse

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from src.ecocart.main import GroceryCartTracker
from src.ecocart.config import Config


def main():
    parser = argparse.ArgumentParser(description="Grocery Cart Tracker")
    parser.add_argument("--cart-id", default="cart_001", help="Cart ID")
    parser.add_argument(
        "--backend-url", default="http://localhost:8000", help="Backend URL"
    )
    parser.add_argument(
        "--video-source", type=int, default=0, help="Video source (0 for webcam)"
    )
    parser.add_argument(
        "--confidence", type=float, default=0.3, help="Confidence threshold"
    )
    parser.add_argument(
        "--no-display", action="store_true", help="Disable video display"
    )

    args = parser.parse_args()

    # Create configuration
    config = Config(
        CART_ID=args.cart_id,
        BACKEND_URL=args.backend_url,
        VIDEO_SOURCE=args.video_source,
        CONFIDENCE_THRESHOLD=args.confidence,
        DISPLAY_WINDOW=not args.no_display,
    )

    # Initialize and run tracker
    tracker = GroceryCartTracker(config)
    tracker.run()


if __name__ == "__main__":
    main()
