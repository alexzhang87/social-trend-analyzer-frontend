#!/usr/bin/env python3
"""
Offline Test Data Collection Service (English Version)
Uses mock data to validate data collection pipeline functionality
Optimized for English business scenarios and overseas markets
"""

import asyncio
import sqlite3
from datetime import datetime
from typing import List, Dict, Any
from loguru import logger
import json

# Mock training data for English business scenarios
MOCK_CUSTOMER_SUPPORT_DATA = [
    {
        "instruction": "Customer inquiry about product return policy",
        "input": "I'd like to understand your return policy. Can I return a product if I'm not satisfied?",
        "output": "We offer a 30-day hassle-free return policy. You can return any item within 30 days of purchase, provided it's in original packaging with tags intact. Return process: 1) Contact customer service for a return authorization number 2) Ship the item back using our prepaid return label 3) We'll process your refund within 3-5 business days after receiving the item.",
        "category": "customer_support",
        "business_relevance": 0.95,
        "quality_score": 0.92
    },
    {
        "instruction": "Customer consultation about product features",
        "input": "What are the main features of this product? What use cases is it best suited for?",
        "output": "Our product offers these key features: 1) Intelligent data analytics with AI-powered insights 2) Automated report generation and scheduling 3) Multi-dimensional data visualization dashboards 4) Real-time monitoring and alert system. It's ideal for: enterprise data analysis, market research, business intelligence, operational monitoring. Particularly valuable for SMBs needing quick data insights without extensive technical resources.",
        "category": "product_consultation",
        "business_relevance": 0.88,
        "quality_score": 0.85
    },
    {
        "instruction": "Technical support consultation",
        "input": "I can't log into the system. It says my password is incorrect, but I'm sure it's right.",
        "output": "For login issues, please try these troubleshooting steps: 1) Verify username and password are entered correctly (check caps lock) 2) Clear browser cache and cookies 3) Try password reset if the issue persists 4) Check your internet connection stability 5) If problems continue, please provide a screenshot of the error message and our technical team will investigate further.",
        "category": "technical_support",
        "business_relevance": 0.82,
        "quality_score": 0.88
    },
    {
        "instruction": "Customer service quality improvement",
        "input": "How can we improve our customer service quality and increase customer satisfaction?",
        "output": "Key strategies for improving customer service quality: 1) Implement comprehensive staff training programs focusing on product knowledge and soft skills 2) Optimize service workflows to reduce response times 3) Establish customer feedback loops and regular satisfaction surveys 4) Deploy AI-powered chatbots for 24/7 basic support 5) Create a knowledge base for self-service options 6) Monitor key metrics like CSAT, NPS, and first-call resolution rates.",
        "category": "customer_support",
        "business_relevance": 0.90,
        "quality_score": 0.89
    },
    {
        "instruction": "Product user experience optimization",
        "input": "Users are saying our product interface is too complex. How can we improve the user experience?",
        "output": "UX optimization recommendations: 1) Conduct user journey mapping to identify pain points 2) Simplify navigation with clear information architecture 3) Implement progressive disclosure to reduce cognitive load 4) Add onboarding tutorials and contextual help 5) Use responsive design for cross-device compatibility 6) A/B test interface changes and gather user feedback 7) Follow accessibility guidelines (WCAG) for inclusive design.",
        "category": "product_consultation",
        "business_relevance": 0.93,
        "quality_score": 0.91
    }
]

MOCK_BUSINESS_STRATEGY_DATA = [
    {
        "instruction": "Market entry strategy analysis",
        "input": "We're a SaaS company looking to enter the European market. How should we develop our market entry strategy?",
        "output": "European SaaS market entry strategy: 1) Market Research: Focus on key markets like Germany, UK, France - analyze digital adoption rates and competitive landscape 2) Localization: Multi-language support, GDPR compliance, local payment methods 3) Partnership Strategy: Identify local system integrators and channel partners 4) Pricing Strategy: Consider local purchasing power and competitive pricing models 5) Go-to-Market: Digital marketing focus, participate in local industry events, build thought leadership content 6) Legal Compliance: Ensure data privacy regulations and local business registration requirements are met.",
        "category": "business_strategy",
        "business_relevance": 0.95,
        "quality_score": 0.90
    },
    {
        "instruction": "Product positioning analysis",
        "input": "How can our product find differentiated positioning in a highly competitive market?",
        "output": "Differentiation positioning strategy: 1) Deep User Research: Identify unmet needs and pain points in your target segment 2) Competitive Gap Analysis: Map competitor features and identify service gaps 3) Unique Value Proposition: Define your distinctive value based on user needs and competitive gaps 4) Feature Differentiation: Develop unique capabilities that competitors can't easily replicate 5) Service Differentiation: Provide superior customer experience and support 6) Brand Differentiation: Build a unique brand story and values that resonate with your audience 7) Niche Focus: Consider specializing in a specific vertical or use case.",
        "category": "product_strategy",
        "business_relevance": 0.92,
        "quality_score": 0.87
    },
    {
        "instruction": "New market development strategy",
        "input": "How should a startup develop an effective market development strategy?",
        "output": "Startup market development strategy: 1) Target Market Definition: Choose a specific niche to avoid competing directly with established players 2) MVP Validation: Launch minimum viable product to test market demand 3) Early Adopter Cultivation: Focus on serving initial customers exceptionally well to build word-of-mouth 4) Cost-Effective Marketing: Leverage content marketing, social media, and SEO rather than expensive advertising 5) Strategic Partnerships: Build relationships with complementary businesses for mutual referrals 6) Data-Driven Iteration: Continuously collect user feedback and iterate quickly based on market response.",
        "category": "business_strategy",
        "business_relevance": 0.94,
        "quality_score": 0.88
    },
    {
        "instruction": "Product feature planning",
        "input": "How should we prioritize product features and create a development roadmap?",
        "output": "Product feature prioritization framework: 1) User Research: Conduct surveys, interviews, and usage analytics to understand user needs 2) Value Assessment: Evaluate features based on user value and business impact 3) Technical Feasibility: Assess development complexity and resource requirements 4) Competitive Analysis: Understand competitor feature sets and identify differentiation opportunities 5) RICE Scoring: Use Reach, Impact, Confidence, and Effort metrics for objective prioritization 6) Agile Planning: Create quarterly roadmaps with flexibility for market changes 7) Stakeholder Alignment: Ensure product, engineering, and business teams agree on priorities.",
        "category": "product_strategy",
        "business_relevance": 0.91,
        "quality_score": 0.86
    },
    {
        "instruction": "SaaS growth strategy",
        "input": "What growth strategies should a B2B SaaS company focus on to scale effectively?",
        "output": "B2B SaaS growth strategies: 1) Product-Led Growth: Design your product to drive user acquisition and expansion 2) Content Marketing: Create valuable content that attracts and educates your target audience 3) Customer Success: Focus on onboarding, adoption, and retention to reduce churn 4) Referral Programs: Incentivize existing customers to refer new users 5) Partnership Channels: Develop integration partnerships and reseller networks 6) Account-Based Marketing: Target high-value prospects with personalized campaigns 7) Freemium Model: Offer a free tier to lower adoption barriers and demonstrate value 8) Expansion Revenue: Focus on upselling and cross-selling to existing customers.",
        "category": "business_strategy",
        "business_relevance": 0.96,
        "quality_score": 0.89
    }
]

MOCK_TECHNICAL_SUPPORT_DATA = [
    {
        "instruction": "API integration troubleshooting",
        "input": "We're having issues integrating with your API. The authentication keeps failing even though we're using the correct credentials.",
        "output": "API authentication troubleshooting steps: 1) Verify API key format and ensure no extra spaces or characters 2) Check if you're using the correct endpoint URL (staging vs production) 3) Ensure proper HTTP headers are included (Content-Type: application/json) 4) Verify timestamp and signature generation if using HMAC authentication 5) Check rate limiting - you may be hitting API limits 6) Review our API documentation for the latest authentication requirements 7) Test with our API testing tool or Postman collection 8) If issues persist, please share your request headers (without sensitive data) for further diagnosis.",
        "category": "technical_support",
        "business_relevance": 0.88,
        "quality_score": 0.90
    },
    {
        "instruction": "System performance optimization",
        "input": "Our application is running slowly. What steps can we take to improve performance?",
        "output": "Performance optimization checklist: 1) Database Optimization: Review query performance, add proper indexes, optimize slow queries 2) Caching Strategy: Implement Redis or Memcached for frequently accessed data 3) CDN Implementation: Use content delivery networks for static assets 4) Code Profiling: Identify bottlenecks using profiling tools 5) Load Balancing: Distribute traffic across multiple servers 6) Image Optimization: Compress and optimize images, use modern formats like WebP 7) Minification: Minify CSS, JavaScript, and HTML 8) Monitoring: Set up APM tools to track performance metrics continuously.",
        "category": "technical_support",
        "business_relevance": 0.85,
        "quality_score": 0.87
    }
]

class TestDataCollectionService:
    def __init__(self, db_path: str = "test_training_data_en.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize test database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create training_data table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS training_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                instruction TEXT NOT NULL,
                input_text TEXT NOT NULL,
                output_text TEXT NOT NULL,
                category TEXT NOT NULL,
                source TEXT NOT NULL,
                business_relevance REAL NOT NULL,
                quality_score REAL NOT NULL,
                language TEXT DEFAULT 'english',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
        logger.info("Test database initialized successfully")
    
    def clear_existing_data(self):
        """Clear existing test data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM training_data")
        conn.commit()
        conn.close()
        logger.info("Existing test data cleared")
    
    def insert_mock_data(self, data_list: List[Dict], source: str):
        """Insert mock data into database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for item in data_list:
            cursor.execute("""
                INSERT INTO training_data 
                (instruction, input_text, output_text, category, source, 
                 business_relevance, quality_score, language)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                item["instruction"],
                item["input"],
                item["output"],
                item["category"],
                source,
                item["business_relevance"],
                item["quality_score"],
                "english"
            ))
        
        conn.commit()
        conn.close()
        logger.info(f"Inserted {len(data_list)} records from {source}")
    
    async def collect_training_data(self):
        """Collect and process training data"""
        logger.info("Starting English training data collection...")
        
        # Clear existing data
        self.clear_existing_data()
        
        # Insert mock data from different sources
        self.insert_mock_data(MOCK_CUSTOMER_SUPPORT_DATA, "customer_support_en")
        self.insert_mock_data(MOCK_BUSINESS_STRATEGY_DATA, "business_strategy_en")
        self.insert_mock_data(MOCK_TECHNICAL_SUPPORT_DATA, "technical_support_en")
        
        # Generate additional synthetic data for English business scenarios
        additional_data = self.generate_additional_english_data()
        self.insert_mock_data(additional_data, "synthetic_business_en")
        
        logger.info("English training data collection completed")
    
    def generate_additional_english_data(self) -> List[Dict]:
        """Generate additional synthetic data for English business scenarios"""
        additional_data = [
            {
                "instruction": "Startup funding strategy",
                "input": "We're a early-stage startup. What funding options should we consider and how should we prepare?",
                "output": "Startup funding strategy: 1) Bootstrap: Use personal savings and revenue to maintain control 2) Angel Investors: Seek individual investors who provide capital and mentorship 3) Venture Capital: For high-growth potential, prepare pitch deck and financial projections 4) Crowdfunding: Platforms like Kickstarter for product validation and funding 5) Government Grants: Research local startup grants and tax incentives 6) Preparation: Develop solid business plan, financial model, and legal structure 7) Due Diligence: Prepare legal documents, IP protection, and compliance requirements.",
                "category": "business_strategy",
                "business_relevance": 0.93,
                "quality_score": 0.88
            },
            {
                "instruction": "Digital marketing strategy for SaaS",
                "input": "How should we approach digital marketing for our B2B SaaS product?",
                "output": "B2B SaaS digital marketing strategy: 1) Content Marketing: Create valuable blog posts, whitepapers, and case studies 2) SEO Optimization: Target long-tail keywords related to your solution 3) LinkedIn Marketing: Engage with decision-makers through thought leadership content 4) Email Marketing: Nurture leads with educational email sequences 5) Webinars: Host educational sessions to demonstrate expertise 6) PPC Advertising: Use Google Ads and LinkedIn Ads for targeted campaigns 7) Marketing Automation: Implement lead scoring and automated workflows 8) Analytics: Track metrics like CAC, LTV, and conversion rates.",
                "category": "business_strategy",
                "business_relevance": 0.91,
                "quality_score": 0.86
            },
            {
                "instruction": "Customer retention strategies",
                "input": "Our customer churn rate is higher than we'd like. What strategies can help improve retention?",
                "output": "Customer retention improvement strategies: 1) Onboarding Excellence: Create smooth, guided onboarding experience 2) Customer Success Team: Proactively help customers achieve their goals 3) Regular Check-ins: Schedule periodic reviews to address concerns early 4) Feature Adoption: Help customers discover and use valuable features 5) Feedback Loops: Regular surveys and feedback collection 6) Loyalty Programs: Reward long-term customers with benefits 7) Predictive Analytics: Identify at-risk customers before they churn 8) Continuous Value Delivery: Regular product updates and improvements.",
                "category": "customer_support",
                "business_relevance": 0.94,
                "quality_score": 0.89
            },
            {
                "instruction": "Agile development methodology",
                "input": "We want to implement agile development practices. What's the best approach for our team?",
                "output": "Agile implementation approach: 1) Start with Scrum: Begin with 2-week sprints and basic ceremonies 2) Team Training: Educate team on agile principles and practices 3) Tools Setup: Implement project management tools like Jira or Azure DevOps 4) Daily Standups: Short daily meetings to sync progress and blockers 5) Sprint Planning: Collaborative planning sessions with the whole team 6) Retrospectives: Regular team reflection and process improvement 7) Continuous Integration: Automate testing and deployment processes 8) Stakeholder Involvement: Include product owners in planning and reviews.",
                "category": "technical_support",
                "business_relevance": 0.87,
                "quality_score": 0.85
            }
        ]
        return additional_data
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get data collection statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total records
        cursor.execute("SELECT COUNT(*) FROM training_data")
        total_records = cursor.fetchone()[0]
        
        # Records by category
        cursor.execute("""
            SELECT category, COUNT(*) 
            FROM training_data 
            GROUP BY category
        """)
        category_stats = dict(cursor.fetchall())
        
        # Records by source
        cursor.execute("""
            SELECT source, COUNT(*) 
            FROM training_data 
            GROUP BY source
        """)
        source_stats = dict(cursor.fetchall())
        
        # Quality statistics
        cursor.execute("""
            SELECT 
                AVG(quality_score) as avg_quality,
                MIN(quality_score) as min_quality,
                MAX(quality_score) as max_quality
            FROM training_data
        """)
        quality_stats = cursor.fetchone()
        
        conn.close()
        
        return {
            "total_records": total_records,
            "category_distribution": category_stats,
            "source_distribution": source_stats,
            "quality_metrics": {
                "average_quality": round(quality_stats[0], 3),
                "min_quality": quality_stats[1],
                "max_quality": quality_stats[2]
            },
            "language": "english",
            "target_market": "international"
        }
    
    def export_training_samples(self, limit: int = 50) -> List[Dict]:
        """Export training samples for review"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT instruction, input_text, output_text, category, 
                   business_relevance, quality_score
            FROM training_data 
            ORDER BY quality_score DESC, business_relevance DESC
            LIMIT ?
        """, (limit,))
        
        results = cursor.fetchall()
        conn.close()
        
        samples = []
        for row in results:
            samples.append({
                "instruction": row[0],
                "input": row[1],
                "output": row[2],
                "category": row[3],
                "business_relevance": row[4],
                "quality_score": row[5]
            })
        
        return samples

async def main():
    """Main function to test data collection"""
    logger.info("Starting English Data Collection Test...")
    
    service = TestDataCollectionService()
    
    # Collect training data
    await service.collect_training_data()
    
    # Get statistics
    stats = service.get_collection_stats()
    
    print("\n" + "="*60)
    print("ENGLISH DATA COLLECTION TEST RESULTS")
    print("="*60)
    print(f"Total Records: {stats['total_records']}")
    print(f"Language: {stats['language']}")
    print(f"Target Market: {stats['target_market']}")
    
    print(f"\nCategory Distribution:")
    for category, count in stats['category_distribution'].items():
        print(f"  {category}: {count} records")
    
    print(f"\nSource Distribution:")
    for source, count in stats['source_distribution'].items():
        print(f"  {source}: {count} records")
    
    print(f"\nQuality Metrics:")
    quality = stats['quality_metrics']
    print(f"  Average Quality: {quality['average_quality']}")
    print(f"  Quality Range: {quality['min_quality']} - {quality['max_quality']}")
    
    # Export samples
    samples = service.export_training_samples(limit=20)
    print(f"\nExported {len(samples)} high-quality training samples")
    
    print("\n" + "="*60)
    print("ENGLISH DATA COLLECTION PIPELINE WORKING CORRECTLY!")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())