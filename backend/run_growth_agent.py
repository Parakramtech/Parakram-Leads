"""CLI entry point for the Parakram Growth Agent.

Usage:
  python run_growth_agent.py [--location Bangalore] [--leads 50]
  python run_growth_agent.py --scorecard "Business Name" --website "https://..."
"""

import asyncio
import argparse
import logging
from agents.parakram_growth_agent import run_acquisition_cycle
from agents.digital_scorecard import process_lead_scorecard

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("growth-agent")


async def main():
    parser = argparse.ArgumentParser(description="Parakram Growth Agent — autonomous customer acquisition")
    parser.add_argument("--location", default="Bangalore", help="City to target")
    parser.add_argument("--leads", type=int, default=30, help="Max leads to process")
    parser.add_argument("--scorecard", help="Generate a scorecard for a specific business")
    parser.add_argument("--website", help="Business website URL (for scorecard)")
    args = parser.parse_args()

    if args.scorecard:
        logger.info(f"Generating scorecard for: {args.scorecard}")
        result = await process_lead_scorecard({
            "business_name": args.scorecard,
            "website_url": args.website or "",
        })
        print(f"\nGrade: {result['scorecard']['overall_grade']}")
        print(f"Score: {result['scorecard']['overall_score']}/100")
        print(f"\nViral Post:\n{result['viral_post']['post']}")
        print(f"\nHashtags: {' '.join('#' + h for h in result['viral_post']['hashtags'])}")
        return

    logger.info(f"=== Parakram Growth Agent ===")
    logger.info(f"Location: {args.location}")
    logger.info(f"Max leads: {args.leads}")
    result = await run_acquisition_cycle(location=args.location, max_leads=args.leads)
    logger.info(f"Result: {result}")


if __name__ == "__main__":
    asyncio.run(main())
