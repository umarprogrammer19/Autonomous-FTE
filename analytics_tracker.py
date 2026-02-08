import json
import os
from datetime import datetime
from typing import Dict, List, Optional

class AnalyticsTracker:
    """Track analytics for the social media automation system"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        self.analytics_file = os.path.join(data_dir, "analytics.json")
        self.load_analytics()
    
    def load_analytics(self):
        """Load analytics from file or initialize defaults"""
        if os.path.exists(self.analytics_file):
            try:
                with open(self.analytics_file, 'r') as f:
                    self.analytics = json.load(f)
            except:
                self.analytics = self.get_default_analytics()
        else:
            self.analytics = self.get_default_analytics()
    
    def get_default_analytics(self) -> Dict:
        """Get default analytics structure"""
        return {
            "emails_sent": 0,
            "whatsapp_messages_sent": 0,
            "ai_posts_generated": 0,
            "last_email_sent": None,
            "last_whatsapp_sent": None,
            "last_ai_post_generated": None,
            "total_interactions": 0
        }
    
    def save_analytics(self):
        """Save analytics to file"""
        with open(self.analytics_file, 'w') as f:
            json.dump(self.analytics, f, indent=2)
    
    def increment_emails_sent(self):
        """Increment email counter"""
        self.analytics["emails_sent"] += 1
        self.analytics["last_email_sent"] = datetime.now().isoformat()
        self.analytics["total_interactions"] += 1
        self.save_analytics()
    
    def increment_whatsapp_sent(self):
        """Increment WhatsApp message counter"""
        self.analytics["whatsapp_messages_sent"] += 1
        self.analytics["last_whatsapp_sent"] = datetime.now().isoformat()
        self.analytics["total_interactions"] += 1
        self.save_analytics()
    
    def increment_ai_posts_generated(self):
        """Increment AI post counter"""
        self.analytics["ai_posts_generated"] += 1
        self.analytics["last_ai_post_generated"] = datetime.now().isoformat()
        self.analytics["total_interactions"] += 1
        self.save_analytics()
    
    def get_analytics(self) -> Dict:
        """Get current analytics"""
        return self.analytics.copy()
    
    def reset_analytics(self):
        """Reset all analytics to default values"""
        self.analytics = self.get_default_analytics()
        self.save_analytics()

# Global analytics tracker instance
tracker = AnalyticsTracker()

# Convenience functions
def increment_emails_sent():
    tracker.increment_emails_sent()

def increment_whatsapp_sent():
    tracker.increment_whatsapp_sent()

def increment_ai_posts_generated():
    tracker.increment_ai_posts_generated()

def get_analytics():
    return tracker.get_analytics()

def reset_analytics():
    tracker.reset_analytics()